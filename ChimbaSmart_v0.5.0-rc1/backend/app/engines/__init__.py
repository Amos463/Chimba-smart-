"""Engine registry: implemented adapters only; geological outputs remain exploratory."""
import importlib.util as iu
import numpy as np
from .. import geo

DISCLAIMER = 'Makadirio ya uchunguzi tu; si uthibitisho wa rasilimali wala ripoti ya JORC/NI 43-101.'

class Engine:
    name='base'; version='0'; requires=None; adapter_ready=False; warnings=[]
    @property
    def library_installed(self):
        return self.requires is None or iu.find_spec(self.requires) is not None
    def validate(self, ds): return []
    def run(self, ds, params): raise NotImplementedError

def _graded(ds, sample_type=None):
    return [s for s in ds['samples'] if s.get('grade') is not None and s.get('assay_unit')=='g/t' and (sample_type is None or s.get('kind')==sample_type)]

def _select_type(ds, sample_type=None):
    rows=_graded(ds)
    types=sorted({r.get('kind') for r in rows if r.get('kind')})
    if sample_type:
        return sample_type, _graded(ds, sample_type), types, False
    if len(types)<=1:
        chosen=types[0] if types else None
        return chosen, _graded(ds, chosen), types, False
    counts={k:len(_graded(ds,k)) for k in types}
    largest=max(counts.values())
    winners=[k for k,v in counts.items() if v==largest]
    if len(winners)!=1:
        return None, [], types, True
    chosen=winners[0]
    return chosen, _graded(ds,chosen), types, False

def _qa_errors(ds):
    # No controls supplied is a warning, not an invented pass. Any failing or unresolved control blocks grade engines.
    return [f"{q.get('sample_id')} ({q.get('role')}: {q.get('status')})" for q in ds.get('qa_checks',[]) if q.get('role') in ('blank','standard','duplicate') and q.get('status')!='pass']

def quick(ds, sample_type=None):
    chosen, rows, types, ambiguous = _select_type(ds,sample_type)
    if ambiguous:
        tr={'ok':False,'n':0,'msg':'Aina zaidi ya moja zina idadi sawa ya assay; chagua aina ya sampuli kabla ya trend.'}
    else:
        tr=geo.trend([(x['e'],x['n']) for x in rows],[x['grade'] for x in rows])
    tr['sample_type']=chosen
    tr['available_sample_types']=types
    tr['qa_errors']=_qa_errors(ds)
    if tr['qa_errors']:
        tr.update({'ok':False,'msg':'Uchambuzi umesimamishwa: QA/QC ina hitilafu au haijakamilika.','qa_blocked':True})
        tr.pop('direction',None)
    elif tr.get('ok'):
        tr['direction']=geo.compass(tr['bearing'])
    if any(x.get('assay_status')=='conflicting_or_multiple_assays' for x in ds['samples']):
        tr['assay_warning']='Sampuli zenye assay nyingi zinazotofautiana zimeondolewa kwenye trend; chagua/idhinisha assay kuu.'
    surveyed=[x for x in ds['orientations'] if x.get('kind')=='surveyed']
    chosen_orientation=surveyed if surveyed else ds['orientations']
    vals=[(x['strike_deg'],x['dip_deg']) for x in chosen_orientation]
    try: plane=geo.mean_orientation(vals) if vals else None
    except ValueError as exc:
        plane=None; tr['orientation_warning']=str(exc)
    if plane: plane['source_kind']='surveyed' if surveyed else 'phone_or_compass_low_confidence'
    return tr,plane

class Trend2D(Engine):
    name='trend2d'; version='1.3'; adapter_ready=True
    def validate(self,ds):
        errors=[]
        if _qa_errors(ds): errors.append('QA/QC imefail au haijakamilika; rekebisha batch kabla ya trend')
        chosen,rows,types,ambiguous=_select_type(ds,ds.get('_sample_type'))
        if ambiguous: errors.append('Chagua sample_type; aina kadhaa zina idadi sawa')
        if len(rows)<4: errors.append('Zinahitajika sampuli huru 4+ za aina moja zenye assay ya g/t')
        return errors
    def run(self,ds,p):
        tr=quick(ds,p.get('sample_type'))[0]
        return {'trend':tr,'crs':ds['crs'],'input_hash':ds['input_hash'],'scope':'surface_samples_only'}

class OrientationMean(Engine):
    name='orientation'; version='1.1'; adapter_ready=True
    def validate(self,ds): return [] if ds['orientations'] else ['Hakuna vipimo vya strike/dip']
    def run(self,ds,p): return {'plane':quick(ds)[1],'warning':'Vipimo vya simu ni vya makadirio; thibitisha kwa kifaa cha kitaalamu.'}

class IDW(Engine):
    name='idw'; version='1.1'; adapter_ready=True
    warnings=['IDW ni interpolation ya uchunguzi; si kriging wala makadirio ya rasilimali.']
    def validate(self,ds):
        errors=[]
        if _qa_errors(ds): errors.append('QA/QC imefail au haijakamilika; rekebisha batch kabla ya IDW')
        chosen,rows,types,ambiguous=_select_type(ds,ds.get('_sample_type'))
        if ambiguous: errors.append('Chagua sample_type; aina kadhaa zina idadi sawa')
        if len(rows)<3: errors.append('IDW inahitaji sampuli 3+ za aina moja zenye assay ya g/t')
        if len({(r['e'],r['n']) for r in rows})<3: errors.append('IDW inahitaji maeneo 3 tofauti')
        return errors
    def run(self,ds,p):
        sample_type,pts,_,ambiguous=_select_type(ds,p.get('sample_type'))
        if ambiguous or len(pts)<3 or len({(x['e'],x['n']) for x in pts})<3: raise ValueError('IDW inahitaji pointi 3 tofauti za eneo katika aina moja ya sampuli')
        power=float(p.get('power',2)); size=int(p.get('grid_size',30))
        if not 0.5<=power<=5 or not 5<=size<=100: raise ValueError('power 0.5..5; grid_size 5..100')
        xy=np.array([[x['e'],x['n']] for x in pts],float); z=np.array([x['grade'] for x in pts],float)
        xs=np.linspace(xy[:,0].min(),xy[:,0].max(),size); ys=np.linspace(xy[:,1].min(),xy[:,1].max(),size); out=[]
        for y in ys:
            row=[]
            for x in xs:
                d=np.hypot(xy[:,0]-x,xy[:,1]-y); exact=np.where(d<1e-9)[0]
                if len(exact): value=float(z[exact[0]])
                else:
                    w=1/np.maximum(d,1e-9)**power; value=float(np.sum(w*z)/np.sum(w))
                row.append(round(value,6))
            out.append(row)
        return {'method':'IDW','power':power,'sample_type':sample_type,'crs':ds['crs'],'x':xs.tolist(),'y':ys.tolist(),'values':out,'sample_count':len(pts),'input_hash':ds['input_hash'],'warning':'Grid ni interpolation ya uchunguzi tu.'}

class DownholeComposite(Engine):
    name='downhole_composite'; version='1.0'; adapter_ready=True
    warnings=['Composites ni maandalizi ya assay intervals; hazifanyi desurveying wala domain estimation.']
    def validate(self,ds):
        a=[i for i in ds['intervals'] if i['kind']=='assay' and i.get('value_num') is not None]
        return [] if a else ['Hakuna assay intervals za downhole za ku-composite']
    def run(self,ds,p):
        length=float(p.get('composite_length_m',1.0)); coverage=float(p.get('minimum_coverage',0.8))
        if not 0.1<=length<=10: raise ValueError('composite_length_m lazima iwe 0.1..10')
        if not 0<=coverage<=1: raise ValueError('minimum_coverage lazima iwe 0..1')
        groups={}
        for item in ds['intervals']:
            if item['kind']=='assay' and item.get('value_num') is not None: groups.setdefault(item['hole_id'],[]).append(item)
        out=[]
        for hole,items in groups.items():
            units={x.get('unit','g/t') for x in items}
            if len(units)!=1: raise ValueError(f'Units tofauti ndani ya shimo {hole}; usichanganye bila conversion')
            unit=next(iter(units)); start=min(x['from_m'] for x in items); end=max(x['to_m'] for x in items)
            while start<end-1e-9:
                stop=min(start+length,end); weighted=covered=0.0
                for x in items:
                    overlap=max(0.0,min(stop,x['to_m'])-max(start,x['from_m']))
                    if overlap: weighted+=overlap*x['value_num']; covered+=overlap
                ratio=covered/(stop-start)
                grade=weighted/covered if covered>0 and ratio>=coverage else None
                out.append({'hole_id':hole,'from_m':round(start,4),'to_m':round(stop,4),'length_m':round(stop-start,4),'covered_m':round(covered,4),'coverage':round(ratio,4),'grade':grade,'unit':unit})
                start=stop
        return {'method':'length_weighted_downhole_compositing','composite_length_m':length,'minimum_coverage':coverage,'composites':out,'input_hash':ds['input_hash'],'crs':ds['crs']}

class PyKrige(Engine):
    name='pykrige'; version='1.1'; requires='pykrige'; adapter_ready=True
    warnings=['Kriging inahitaji uchaguzi na uthibitishaji wa variogram; matokeo si resource estimate.']
    def validate(self,ds):
        errors=[]
        if _qa_errors(ds): errors.append('QA/QC imefail au haijakamilika; rekebisha batch kabla ya kriging')
        chosen,rows,types,ambiguous=_select_type(ds,ds.get('_sample_type'))
        if ambiguous: errors.append('Chagua sample_type; aina kadhaa zina idadi sawa')
        if len(rows)<5: errors.append('Ordinary kriging inahitaji sampuli 5+ za aina moja zenye assay ya g/t')
        if len({(r['e'],r['n']) for r in rows})<5: errors.append('Kriging inahitaji maeneo 5 tofauti')
        return errors
    def run(self,ds,p):
        from pykrige.ok import OrdinaryKriging
        sample_type,pts,_,ambiguous=_select_type(ds,p.get('sample_type'))
        if ambiguous or len(pts)<5 or len({(x['e'],x['n']) for x in pts})<5: raise ValueError('Kriging inahitaji pointi 5 tofauti katika aina moja ya sampuli')
        x=[s['e'] for s in pts]; y=[s['n'] for s in pts]; z=[s['grade'] for s in pts]
        model=p.get('variogram_model','spherical')
        if model not in ('linear','power','gaussian','spherical','exponential'): raise ValueError('Variogram model hairuhusiwi')
        size=int(p.get('grid_size',30))
        if not 5<=size<=100: raise ValueError('grid_size 5..100')
        ok=OrdinaryKriging(x,y,z,variogram_model=model,verbose=False,enable_plotting=False)
        gx=np.linspace(min(x),max(x),size); gy=np.linspace(min(y),max(y),size); zgrid,var=ok.execute('grid',gx,gy)
        return {'method':'ordinary_kriging','sample_type':sample_type,'variogram_model':model,'crs':ds['crs'],'x':gx.tolist(),'y':gy.tolist(),'values':np.asarray(zgrid).tolist(),'variance':np.asarray(var).tolist(),'sample_count':len(pts),'input_hash':ds['input_hash']}

class GemPyModel(Engine):
    name='gempy'; version='2026.0.3'; requires='gempy'; adapter_ready=True
    warnings=['3D implicit model; geological interpretation and competent-person review are required.']
    def validate(self,ds):
        contacts=ds.get('_contacts') or ds.get('contacts') or []
        if len(contacts)<3: return ['GemPy requires at least 3 explicit surface/stratigraphic contacts']
        extent=ds.get('_gempy_extent') or ds.get('gempy_extent')
        if not (isinstance(extent,list) and len(extent)==6): return ['GemPy requires an explicit 6-value model extent']
        return []
    def run(self,ds,p):
        import gempy as gp
        import numpy as np
        from gempy_engine.core.data.stack_relation_type import StackRelationType
        contacts=p.get('contacts') or ds.get('_contacts') or ds.get('contacts') or []
        extent=p.get('extent') or ds.get('_gempy_extent') or ds.get('gempy_extent')
        resolution=p.get('resolution',[20,20,20])
        if len(contacts)<3 or not (isinstance(extent,list) and len(extent)==6): raise ValueError('GemPy requires contacts and a 6-value extent')
        if not (isinstance(resolution,list) and len(resolution)==3 and all(isinstance(v,int) and 5<=v<=100 for v in resolution)): raise ValueError('GemPy resolution must contain three integers from 5..100')
        element_name=p.get('surface_name','Surface1')
        x=np.array([float(c['x']) for c in contacts],dtype=float)
        y=np.array([float(c['y']) for c in contacts],dtype=float)
        z=np.array([float(c['z']) for c in contacts],dtype=float)
        names=np.array([str(c.get('name',element_name)) for c in contacts])
        unique_names=sorted(set(names.tolist()))
        if len(unique_names)!=1: raise ValueError('GemPy adapter currently requires one explicit surface per job')
        orient=ds.get('orientations') or p.get('orientations') or []
        if orient:
            ox=np.array([float(o['x']) for o in orient],dtype=float)
            oy=np.array([float(o['y']) for o in orient],dtype=float)
            oz=np.array([float(o['z']) for o in orient],dtype=float)
            gx=np.array([float(o.get('pole_gx',0)) for o in orient],dtype=float)
            gy=np.array([float(o.get('pole_gy',0)) for o in orient],dtype=float)
            gz=np.array([float(o.get('pole_gz',1)) for o in orient],dtype=float)
            orientations=gp.data.OrientationsTable.from_arrays(ox,oy,oz,gx,gy,gz,names=element_name)
        else:
            orientations=gp.data.OrientationsTable.initialize_empty()
        surface=gp.data.StructuralElement(
            name=element_name,
            surface_points=gp.data.SurfacePointsTable.from_arrays(x,y,z,names=element_name),
            orientations=orientations,
            color='#015482',
        )
        group=gp.data.StructuralGroup(name=p.get('structural_group','StratSeries'),elements=[surface],structural_relation=StackRelationType.ERODE)
        frame=gp.data.StructuralFrame([group],gp.data.ColorsGenerator())
        model=gp.create_geomodel(project_name=p.get('project_name','ChimbaSmart'),extent=extent,resolution=resolution,structural_frame=frame)
        model.update_transform(gp.data.GlobalAnisotropy.NONE)
        solutions=gp.compute_model(model)
        octree_levels=getattr(solutions,'octree_levels',None)
        return {
            'method':'gempy_implicit_surface',
            'engine':'gempy','engine_version':'2026.0.3',
            'surface_name':element_name,'extent':extent,'resolution':resolution,
            'crs':ds['crs'],'input_hash':ds['input_hash'],
            'octree_levels':octree_levels,
            'warnings':list(self.warnings),
        }

class LoopStructuralModel(Engine):
    name='loopstructural'; version='1.12.0'; requires='LoopStructural'; adapter_ready=True
    warnings=['Implicit model; orientation and topology assumptions require geological review.']
    def validate(self,ds):
        constraints=ds.get('_loop_constraints') or ds.get('loop_constraints') or []
        extent=ds.get('_loop_extent') or ds.get('loop_extent')
        if len(constraints)<3: return ['LoopStructural requires at least 3 XYZ orientation/constraint points']
        if not (isinstance(extent,list) and len(extent)==2 and all(isinstance(p,(list,tuple,np.ndarray)) and len(p)==3 for p in extent)): return ['LoopStructural requires origin and maximum 3D bounds']
        return []
    def run(self,ds,p):
        import pandas as pd
        from LoopStructural import GeologicalModel
        constraints=p.get('constraints') or ds.get('_loop_constraints') or ds.get('loop_constraints') or []
        extent=p.get('extent') or ds.get('_loop_extent') or ds.get('loop_extent')
        if len(constraints)<3: raise ValueError('LoopStructural requires at least 3 constraints')
        if not (isinstance(extent,list) and len(extent)==2): raise ValueError('LoopStructural requires origin and maximum bounds')
        rows=[]
        for c in constraints:
            rows.append({'X':float(c['x']),'Y':float(c['y']),'Z':float(c['z']),'nx':float(c.get('nx',0)),'ny':float(c.get('ny',0)),'nz':float(c.get('nz',1)),'feature_name':str(c.get('feature_name','strati'))})
        df=pd.DataFrame(rows)
        feature_name=p.get('feature_name','strati')
        origin=np.asarray(extent[0],dtype=float); maximum=np.asarray(extent[1],dtype=float)
        model=GeologicalModel(origin,maximum)
        model.set_model_data(df)
        feature=model.create_and_add_foliation(feature_name,data=df,nelements=int(p.get('nelements',10000)))
        if feature is None: raise RuntimeError('LoopStructural did not create the requested geological feature')
        grid_size=int(p.get('grid_size',20))
        if not 5<=grid_size<=100: raise ValueError('LoopStructural grid_size must be 5..100')
        xs=np.linspace(origin[0],maximum[0],grid_size); ys=np.linspace(origin[1],maximum[1],grid_size); zs=np.linspace(origin[2],maximum[2],grid_size)
        xx,yy,zz=np.meshgrid(xs,ys,zs,indexing='ij')
        xyz=np.column_stack((xx.ravel(),yy.ravel(),zz.ravel()))
        values=model.evaluate_feature_value(feature_name,xyz,scale=False)
        finite=np.isfinite(np.asarray(values))
        if not bool(finite.any()): raise RuntimeError('LoopStructural returned no finite model values')
        return {
            'method':'loopstructural_implicit_foliation','engine':'LoopStructural','engine_version':'1.12.0',
            'feature_name':feature_name,'extent':[origin.tolist(),maximum.tolist()],
            'grid_size':grid_size,'crs':ds['crs'],'input_hash':ds['input_hash'],
            'values':np.asarray(values).reshape((grid_size,grid_size,grid_size)).tolist(),
            'finite_value_count':int(finite.sum()),'warnings':list(self.warnings),
        }

class PyGIMLiERT(Engine):
    name='pygimli'; version='1.6.1'; requires='pygimli'; adapter_ready=True
    warnings=['Geophysical inversion is non-unique; measurements and error model require specialist review.']
    def validate(self,ds):
        electrodes=ds.get('_geophysics_electrodes') or ds.get('geophysics_electrodes') or []
        measurements=ds.get('_geophysics_measurements') or ds.get('geophysics_measurements') or []
        if len(electrodes)<4: return ['pyGIMLi ERT requires at least 4 electrodes']
        if len(measurements)<1: return ['pyGIMLi ERT requires at least 1 four-point measurement']
        return []
    def run(self,ds,p):
        import pygimli as pg
        from pygimli.physics import ert
        import pygimli.meshtools as mt
        electrodes=p.get('electrodes') or ds.get('_geophysics_electrodes') or ds.get('geophysics_electrodes') or []
        measurements=p.get('measurements') or ds.get('_geophysics_measurements') or ds.get('geophysics_measurements') or []
        if len(electrodes)<4 or len(measurements)<1: raise ValueError('pyGIMLi requires electrodes and measurements')
        scheme=pg.DataContainerERT()
        for electrode in electrodes:
            if not isinstance(electrode,(list,tuple)) or len(electrode)!=3: raise ValueError('Each electrode must be [x,y,z]')
            scheme.createSensor(tuple(float(v) for v in electrode))
        scheme.resize(len(measurements))
        for field in ('a','b','m','n'):
            values=[]
            for m in measurements:
                index=int(m[field])
                if index<0 or index>=len(electrodes): raise ValueError(f'{field} electrode index out of range')
                values.append(index)
            scheme.set(field,values)
        world=mt.createWorld(start=p.get('world_start',[-50,0]),end=p.get('world_end',[50,-50]),layers=p.get('layers',[-1,-5]),worldMarker=True)
        for sensor in scheme.sensorPositions(): world.createNode(sensor)
        mesh=mt.createMesh(world,quality=int(p.get('mesh_quality',34)))
        res=p.get('initial_resistivities',[[1,100],[2,100],[3,60]])
        forward=ert.simulate(mesh,res=res,scheme=scheme,verbose=False)
        rhoa=np.asarray(forward.get('rhoa').array(),dtype=float)
        if rhoa.size!=len(measurements): raise RuntimeError('pyGIMLi returned an unexpected measurement count')
        return {
            'method':'pygimli_ert_forward','engine':'pygimli','engine_version':'1.6.1',
            'electrode_count':len(electrodes),'measurement_count':len(measurements),
            'rhoa':rhoa.tolist(),'crs':ds['crs'],'input_hash':ds['input_hash'],
            'initial_resistivities':res,'warnings':list(self.warnings),
        }

class UnavailableAdapter(Engine):
    def __init__(self,name,requires,reason,version='0'): self.name=name; self.requires=requires; self.reason=reason; self.version=version; self.warnings=[reason]
    def validate(self,ds): return [self.reason]

ENGINES={e.name:e for e in (Trend2D(),OrientationMean(),IDW(),DownholeComposite(),PyKrige(),GemPyModel(),LoopStructuralModel(),UnavailableAdapter('pygslib','pygslib','Official OpenGeoStat Conda package is Python 3.8-era and its Linux native runtime failed import validation; source build is incompatible with Python 3.12. See docs/SERVER_ENGINE_DEPLOYMENT_REPORT.md.','0.0.0.7.1.1'),PyGIMLiERT())}

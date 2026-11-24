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

class UnavailableAdapter(Engine):
    def __init__(self,name,requires,reason): self.name=name; self.requires=requires; self.reason=reason; self.warnings=[reason]
    def validate(self,ds): return [self.reason]

ENGINES={e.name:e for e in (Trend2D(),OrientationMean(),IDW(),DownholeComposite(),PyKrige(),UnavailableAdapter('loopstructural','LoopStructural','Adapter inahitaji utekelezaji wa feature/contact constraints na version pin.'),UnavailableAdapter('gempy','gempy','Adapter inahitaji stratigraphic stack, structural groups na fault mapping.'),UnavailableAdapter('pygslib','pygslib','Adapter inahitaji collar-survey-assay compositing na domain QA.'),UnavailableAdapter('pygimli','pygimli','Adapter inahitaji survey-specific sensor/electrode geometry na import formats.'))}

"""Hesabu za jiolojia. Convention: strike kwa right-hand rule (dip_dir = strike + 90)."""
import numpy as np
def _deg(value):
    value=float(value)%360.0
    return 0.0 if abs(value-360.0)<1e-9 or abs(value)<1e-9 else value
def projected_epsg(lon,lat,crs='auto'):
    if str(crs).upper().startswith('EPSG:'): return int(crs.split(':')[1])
    zone=max(1,min(60,int((lon+180)//6)+1))
    if crs=='arc1960':
        if lat>=0: raise ValueError('Arc 1960 UTM 35-37 hapa imekusudiwa maeneo ya kusini mwa ikweta')
        if not 35<=zone<=37: raise ValueError('Arc 1960 UTM inaruhusu zones 35S-37S tu')
        return 21000+zone
    return (32600 if lat>=0 else 32700)+zone               # WGS84 UTM
def to_projected(lat,lon,crs='auto'):
    from pyproj import Transformer
    e=projected_epsg(lon,lat,crs)
    from pyproj import CRS
    target=CRS.from_epsg(e)
    if not target.is_projected: raise ValueError(f'EPSG:{e} si projected CRS; tumia CRS ya mita')
    x,y=Transformer.from_crs(4326,target,always_xy=True).transform(lon,lat)
    return x,y,f'EPSG:{e}'
def fit_plane(pts):
    """pts: Nx3 (E,N,Z) zilizopimwa kwa usahihi. rms_m = kupotoka kwa pointi kutoka kwenye ndege."""
    p=np.asarray(pts,float)
    if len(p)<3: raise ValueError('Pointi 3 au zaidi zinahitajika')
    u,s,vt=np.linalg.svd(p-p.mean(0));
    if len(s)<2 or s[1]<1e-8: raise ValueError('Pointi hazitoshi kufafanua ndege; huenda ziko mstari mmoja')
    n=vt[-1]
    if n[2]<0: n=-n
    dd=float(np.degrees(np.arctan2(n[0],n[1]))%360)
    return {'strike':_deg(dd-90),'dip':float(np.degrees(np.arccos(n[2]/np.linalg.norm(n)))),'dip_dir':dd,'rms_m':float(s[-1]/np.sqrt(len(p)))}
def mean_orientation(meas):
    """meas: [(strike,dip)] kutoka dira. Wastani wa vekta za normal (si wastani wa pembe)."""
    v=[]
    for st,dp in meas:
        dd,d=np.radians((st+90)%360),np.radians(dp); v.append([np.sin(d)*np.sin(dd),np.sin(d)*np.cos(dd),np.cos(d)])
    m=np.mean(v,0); r=float(np.linalg.norm(m))
    if r<1e-8: raise ValueError('Vipimo vya orientation vinapingana; wastani haujafafanuliwa')
    n=m/r
    dd=float(np.degrees(np.arctan2(n[0],n[1]))%360)
    return {'strike':_deg(dd-90),'dip':float(np.degrees(np.arccos(min(1,n[2])))),'dip_dir':dd,'n':len(meas),'consistency':r}
def trend(en,grades):
    """Robust trend ya log1p(g/t), RANSAC + Huber IRLS.
    Hufanya kazi kwa projected metric coordinates na sampuli za aina moja.
    """
    import itertools, random
    en,g=np.asarray(en,float),np.asarray(grades,float); n=len(g)
    if n<4: return {'ok':False,'n':n,'msg':'Sampuli 4 au zaidi za aina moja zenye g/t zinahitajika'}
    if en.shape!=(n,2) or not np.isfinite(en).all() or not np.isfinite(g).all() or (g<0).any():
        return {'ok':False,'n':n,'msg':'Data za trend si sahihi'}
    z=np.log1p(g)
    A=np.c_[np.ones(n),en[:,0]-en[:,0].mean(),en[:,1]-en[:,1].mean()]
    if len({(float(x),float(y)) for x,y in en})<n or np.linalg.matrix_rank(A)<3:
        return {'ok':False,'n':n,'msg':'Trend inahitaji pointi za eneo zisizojirudia na angalau maeneo 3 yasiyokuwa mstari mmoja'}
    triples=list(itertools.combinations(range(n),3)) if n<=12 else []
    if not triples:
        rng=random.Random(271828); triples=[]
        seen=set()
        while len(triples)<min(160,n*(n-1)*(n-2)//6):
            t=tuple(sorted(rng.sample(range(n),3)))
            if t not in seen: seen.add(t); triples.append(t)
    best=None
    for ids in triples:
        try: c0=np.linalg.solve(A[list(ids)],z[list(ids)])
        except np.linalg.LinAlgError: continue
        resid=z-A@c0; med=float(np.median(resid))
        # Fixed log-grade residual gate prevents a high-leverage nugget inflating its own threshold.
        threshold=0.25
        mask=np.abs(resid-med)<=threshold
        score=(int(mask.sum()),-float(np.median(np.abs(resid[mask]-med))) if mask.any() else -1e9)
        if best is None or score>best[0]: best=(score,mask)
    inliers=best[1] if best and best[0][0]>=4 else np.ones(n,dtype=bool)
    Ai=A[inliers]; zi=z[inliers]
    w=np.ones(len(zi)); c=np.linalg.lstsq(Ai,zi,rcond=None)[0]
    for _ in range(30):
        residual=zi-Ai@c; med=np.median(residual); mad=np.median(np.abs(residual-med))*1.4826
        if mad<1e-12: break
        u=np.abs(residual)/(1.345*mad); nw=np.where(u<=1,1,1/np.maximum(u,1e-12))
        aw=Ai*np.sqrt(nw[:,None]); zw=zi*np.sqrt(nw)
        nc=np.linalg.lstsq(aw,zw,rcond=None)[0]
        if np.linalg.norm(nc-c)<1e-10: c=nc; w=nw; break
        c,w=nc,nw
    if np.hypot(c[1],c[2])<1e-12: return {'ok':False,'n':n,'msg':'Hakuna mwelekeo dhahiri'}
    residual=zi-Ai@c; ss=((zi-zi.mean())**2).sum()
    r2=float(1-(residual**2).sum()/max(ss,1e-12))
    bearing=float(np.degrees(np.arctan2(c[1],c[2]))%360)
    conf='chini' if int(inliers.sum())<8 or r2<.2 else 'wastani' if int(inliers.sum())<15 or r2<.5 else 'juu'
    return {'ok':True,'n':n,'n_used':int(inliers.sum()),'bearing':bearing,'r2':r2,'confidence':conf,
            'method':'RANSAC + Huber IRLS on log1p(g/t)','outliers_excluded':int(n-inliers.sum()),
            'msg':'Trend ya uchunguzi; si uthibitisho wa mwendelezo wa mwili wa madini.'}
def compass(b): return ['Kaskazini','Kaskazini-Mashariki','Mashariki','Kusini-Mashariki','Kusini','Kusini-Magharibi','Magharibi','Kaskazini-Magharibi'][int((b+22.5)//45)%8]

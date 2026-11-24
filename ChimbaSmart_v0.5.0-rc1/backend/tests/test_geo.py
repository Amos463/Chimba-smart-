import numpy as np
from app.geo import fit_plane,trend,mean_orientation,projected_epsg
def test_plane():
    t=np.tan(np.radians(30)); r=fit_plane([(0,0,0),(100,0,-100*t),(0,100,0),(100,100,-100*t)])
    assert abs(r['dip']-30)<.01 and abs(r['dip_dir']-90)<.01 and abs(r['strike'])<.01 and r['rms_m']<1e-6
def test_trend():
    en=[(x,y) for x in range(0,50,10) for y in (0,10)]; assert abs(trend(en,[x/10 for x,_ in en])['bearing']-90)<1
    assert not trend(en[:3],[1,2,3])['ok']
def test_mean_orientation():
    r=mean_orientation([(10,40),(10,40)]); assert abs(r['strike']-10)<.01 and abs(r['dip']-40)<.01
def test_epsg(): assert projected_epsg(32.9,-3,'auto')==32736 and projected_epsg(32.9,-3,'arc1960')==21036 and projected_epsg(0,0,'EPSG:32737')==32737


def test_trend_robustly_excludes_extreme_nugget():
    en=[(x,y) for x in range(0,50,10) for y in (0,10)]
    grades=[x/10 for x,y in en]
    grades[-1]=10000.0
    r=trend(en,grades)
    assert r['ok'] and r['outliers_excluded']>=1
    assert abs(r['bearing']-90)<12

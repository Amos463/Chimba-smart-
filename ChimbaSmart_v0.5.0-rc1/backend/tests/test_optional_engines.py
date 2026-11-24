import pytest
from app.engines import ENGINES

def test_pykrige_adapter_runs_when_dependency_is_installed():
    pytest.importorskip("pykrige")
    ds={
      "samples":[
        {"sample_id":f"S{i}","kind":"rock_chip","e":float(i%3)*100.0,"n":float(i//3)*100.0,
         "grade":float(i+1),"assay_unit":"g/t"} for i in range(6)
      ],
      "crs":"EPSG:32736","input_hash":"test-input-hash",
      "collars":[],"surveys":[],"intervals":[],"orientations":[]
    }
    engine=ENGINES["pykrige"]
    assert engine.validate(ds)==[]
    result=engine.run(ds,{"grid_size":5,"variogram_model":"spherical"})
    assert result["method"]=="ordinary_kriging"
    assert len(result["values"])==5 and len(result["variance"])==5

def test_gempy_adapter_runs_builtin_synthetic_model():
    pytest.importorskip("gempy")
    engine=ENGINES["gempy"]
    ds={
      "crs":"EPSG:32736","input_hash":"gempy-test-input",
      "orientations":[{"x":50,"y":50,"z":-20,"pole_gx":0,"pole_gy":0,"pole_gz":1}],
    }
    params={
      "contacts":[{"x":20,"y":50,"z":-20},{"x":50,"y":50,"z":-20},{"x":80,"y":50,"z":-20}],
      "extent":[0,100,0,100,-100,0],"resolution":[10,10,10],"surface_name":"ContactA",
    }
    ds["_contacts"]=params["contacts"]; ds["_gempy_extent"]=params["extent"]
    assert engine.validate(ds)==[]
    result=engine.run(ds,params)
    assert result["method"]=="gempy_implicit_surface"
    assert result["input_hash"]=="gempy-test-input"

def test_loopstructural_adapter_runs_claudius_synthetic():
    pytest.importorskip("LoopStructural")
    from LoopStructural.datasets import load_claudius
    data,bb=load_claudius()
    engine=ENGINES["loopstructural"]
    constraints=[
      {"x":float(bb[0,0]),"y":float(bb[0,1]),"z":float(bb[0,2]),"nx":0,"ny":0,"nz":1},
      {"x":float(bb[1,0]),"y":float(bb[1,1]),"z":float(bb[1,2]),"nx":0,"ny":0,"nz":1},
      {"x":float(data.iloc[len(data)//2]["X"]),"y":float(data.iloc[len(data)//2]["Y"]),"z":float(data.iloc[len(data)//2]["Z"]),"nx":0,"ny":0,"nz":1},
    ]
    ds={"crs":"EPSG:28350","input_hash":"loop-test-input","orientations":[],"_loop_constraints":constraints,"_loop_extent":[bb[0].tolist(),bb[1].tolist()]}
    assert engine.validate(ds)==[]
    result=engine.run(ds,{"constraints":constraints,"extent":[bb[0].tolist(),bb[1].tolist()],"grid_size":5,"nelements":500})
    assert result["finite_value_count"]>0
    assert len(result["values"])==5

def test_pygimli_adapter_runs_ert_synthetic():
    pytest.importorskip("pygimli")
    engine=ENGINES["pygimli"]
    electrodes=[[-2,0,0],[-1,0,0],[0,0,0],[1,0,0],[2,0,0]]
    measurements=[
      {"a":0,"b":1,"m":3,"n":2},
      {"a":0,"b":1,"m":2,"n":3},
      {"a":3,"b":2,"m":1,"n":0},
    ]
    ds={"crs":"EPSG:32736","input_hash":"pygimli-test-input","orientations":[],"_geophysics_electrodes":electrodes,"_geophysics_measurements":measurements}
    assert engine.validate(ds)==[]
    result=engine.run(ds,{"electrodes":electrodes,"measurements":measurements})
    assert len(result["rhoa"])==3
    assert all(v>0 for v in result["rhoa"])

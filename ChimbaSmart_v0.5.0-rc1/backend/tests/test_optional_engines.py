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

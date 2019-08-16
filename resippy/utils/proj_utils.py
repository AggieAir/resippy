import osr
from pyproj import Proj


def wkt_to_proj_string(wkt,            # type: str
                ):              # type: (...) -> Proj
    spatialref = osr.SpatialReference()
    spatialref.ImportFromWkt(wkt)
    proj_string = spatialref.ExportToProj4()
    return proj_string


def wkt_to_proj(wkt,            # type: str
                ):              # type: (...) -> Proj
    proj_string = wkt_to_proj_string(wkt)
    proj = Proj(proj_string)
    return proj


def wkt_to_osr_spatialref(wkt,  # type: str
                          ):              # type: (...) -> Proj
    spatialref = osr.SpatialReference()
    spatialref.ImportFromWkt(wkt)
    return spatialref
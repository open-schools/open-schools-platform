import os
from pathlib import Path

from config.env import env

if env("GEO_DJANGO_CUSTOM_PATHS", default=False):
    if env("GEO_DJANGO_CUSTOM_OSGEO_PATHS", default=False):
        os.environ["OSGEO4W_ROOT"] = env("OSGEO4W_ROOT", default=None)
        os.environ["GDAL_DATA"] = env("GDAL_DATA", default=None)
        os.environ["PROJ_LIB"] = env("PROJ_LIB", default=None)
    GEOS_LIBRARY_PATH = env("GEOS_LIBRARY_PATH", default=None)
    GDAL_LIBRARY_PATH = env("GDAL_LIBRARY_PATH", default=None)

    if GEOS_LIBRARY_PATH is None and GDAL_LIBRARY_PATH is None:
        try:
            from osgeo import gdal
            gdal_path = Path(gdal.__file__)
            OSGEO4W = os.path.join(gdal_path.parent, '')
            os.environ["OSGEO4W_ROOT"] = OSGEO4W
            os.environ["GDAL_DATA"] = os.path.join(OSGEO4W, "data", "gdal")
            os.environ["PROJ_LIB"] = os.path.join(OSGEO4W, "data", "proj")
            os.environ["PATH"] = OSGEO4W + ";" + os.environ["PATH"]
            GEOS_LIBRARY_PATH = str(os.path.join(OSGEO4W, "geos_c.dll"))
            GDAL_LIBRARY_PATH = str(os.path.join(OSGEO4W, "gdal302.dll"))
        except ImportError:
            GEOS_LIBRARY_PATH = None
            GDAL_LIBRARY_PATH = None
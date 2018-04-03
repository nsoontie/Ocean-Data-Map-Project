#!env python
'''
This script creates the base layer Mercator projection for the world.  
Note that at higher zoom levels (8 or higher) this script consumes to much ram for most computers to run. This problem is being worked on. 
'''
import sys
import numpy as np
import math
import pyproj
from netCDF4 import Dataset
from pyresample.geometry import SwathDefinition
from pyresample.kd_tree import resample_custom

if len(sys.argv) != 2:
    print "Usage: %s zoom"
    exit()

zoom = int(sys.argv[1])

numtiles = 2 ** zoom
numpixels = numtiles * 256

wgs84 = pyproj.Proj(init='EPSG:4326')
dest = pyproj.Proj(init='EPSG:3857')

minx, miny = dest(-180.0, -85.06)
maxx, maxy = dest(180.0, 85.06)
print "minx: ", minx, "miny: ", miny
print "maxx: ", maxx, "maxy: ", maxy

dx = (maxx - minx) / numpixels
dy = (maxy - miny) / numpixels
print "dx: ", dx, "dy: ", dy
x = minx + dx * np.indices((numpixels, numpixels), np.float32)[0, :, :]
y = miny + dy * np.indices((numpixels, numpixels), np.float32)[1, :, :]

lon, lat = dest(x, y, inverse=True)
print "lon: ", lon, "lat: ", lat
with Dataset("ETOPO1_Bed_g_gmt4.grd.nc", "r") as ds_in:
    with Dataset("etopo_EPSG:3857_z%d.nc" % zoom, "w", format='NETCDF4') as ds_out:
        ds_out.createDimension('x', numpixels)
        ds_out.createDimension('y', numpixels)

        latvar = ds_out.createVariable('lat', 'f4', ('x', 'y'))
        lonvar = ds_out.createVariable('lon', 'f4', ('x', 'y'))

        latvar[:] = lat
        lonvar[:] = lon

        zvar = ds_out.createVariable('z', 'i4', ('y', 'x'))

        input_lon, input_lat = np.meshgrid(ds_in.variables['x'][:],
                                           ds_in.variables['y'][0:11000:])

        orig_def = SwathDefinition(lons=input_lon, lats=input_lat)
        target_def = SwathDefinition(lons=lon, lats=lat)

        inputdata = ds_in.variables['z'][0:11000, :]

        resampled = resample_custom(
            orig_def,
            inputdata,
            target_def,
            radius_of_influence=50000,
            neighbours=10,
            weight_funcs=lambda r: 1 / r ** 2,
            fill_value=None, nprocs=4)

        zvar[:] = resampled.transpose()[::-1, :]


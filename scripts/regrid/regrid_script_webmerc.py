#!env python
import sys
import numpy as np
import math
import pyproj

if len(sys.argv) != 2:
    print "Usage: %s zoom"
    exit()

zoom = int(sys.argv[1])

numtiles = 2 ** zoom
numpixels = numtiles * 256

maxlat = math.degrees(math.atan(23.140692632779263) * 2 - math.pi / 2.0)

wgs84 = pyproj.Proj(init='EPSG:4326')
webmerc = pyproj.Proj(init='EPSG:3857')

minx, miny = webmerc(-180, -maxlat)
maxx, maxy = webmerc(180, maxlat)
x = np.linspace(minx, maxx, numpixels)
y = np.linspace(maxy, miny, numpixels)

lon, lat = pyproj.transform(webmerc, wgs84, x, y)

print "defdim(\"lat\", %d);\n" % numpixels
print "defdim(\"lon\", %d);\n" % numpixels
print "lon@units=\"degrees_east\";\n"
print "lon@long_name=\"Longitude\";\n"
print "lon[$lon] = {%s};\n" % (
    ", ".join(lon.astype(str))
)
print "lat[$lat] = {%s};\n" % (
    ", ".join(lat.astype(str))
)
print "lat@units=\"degrees_north\";\n"
print "lat@long_name=\"Latitude\";\n"

print "*out[$lat,$lon] = short(0);\n"
print "z = short(bilinear_interp_wrap(z, out, lat, lon, y, x));\n"

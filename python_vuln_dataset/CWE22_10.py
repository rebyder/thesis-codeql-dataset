# repo: vladanti/ndvi_calc
# path: ndvi.py

#!/usr/bin/env python

# Version 0.1
# NDVI automated acquisition and calculation by Vladyslav Popov
# Using landsat-util, source: https://github.com/developmentseed/landsat-util
# Uses Amazon Web Services Public Dataset (Lansat 8)
# Script should be run every day
from os.path import join, abspath, dirname, exists
import os
import errno
import shutil
from tempfile import mkdtemp
import subprocess
import urllib2
import logging
import sys
import datetime
import re
from landsat.search import Search
from landsat.ndvi import NDVIWithManualColorMap

# Enable logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Get current date
current_date = datetime.datetime.now().date()
print 'Current date is:', current_date
# Let`s subtract 1 day from current date
sub_date = current_date - datetime.timedelta(days=1)
print 'Subtract date is:', sub_date

# Scene search by date and WRS-2 row and path
search = Search()

try:
    search_results = search.search(paths_rows='177,025', start_date=sub_date, end_date=current_date)
    search_string = str(search_results.get('results'))
    search_list = re.compile('\w+').findall(search_string)
    scene_id = str(search_list.pop(5))
    print scene_id
    l = len(scene_id)
    print l
#exit if we have no current image
except Exception:
    raise SystemExit('Closing...')

# String concat for building Red Band URL for download
url_red = 'http://landsat-pds.s3.amazonaws.com/L8/177/025/' + scene_id + '/' + scene_id + '_B4.TIF'
# String concat for building NIR Band URL for download
url_nir = 'http://landsat-pds.s3.amazonaws.com/L8/177/025/' + scene_id + '/' + scene_id + '_B5.TIF'

# Build filenames for band rasters and output NDVI file
red_file = scene_id + '_B4.TIF'
nir_file = scene_id + '_B5.TIF'
ndvi_file = scene_id + '_NDVI.TIF'
print 'Filenames builded succsessfuly'

# Create directories for future pssing
base_dir = os.getcwd()
temp_folder = join(base_dir, "temp_folder")
scene_folder = join(temp_folder, scene_id)
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
if not os.path.exists(scene_folder):
    os.makedirs(scene_folder)

# Download section for Band 4 using urllib2
file_name = url_red.split('/')[-1]
u = urllib2.urlopen(url_red)
f = open("temp_folder/"+scene_id+"/"+file_name, 'wb')
meta = u.info()
file_size = int(meta.getheaders("Content-Length")[0])
print "Downloading: %s Bytes: %s" % (file_name, file_size)

file_size_dl = 0
block_sz = 8192
while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()

# Download section for Band 5 using urllib2
file_name = url_nir.split('/')[-1]
u = urllib2.urlopen(url_nir)
f = open("temp_folder/"+scene_id+"/"+file_name, 'wb')
meta = u.info()
file_size = int(meta.getheaders("Content-Length")[0])
print "Downloading: %s Bytes: %s" % (file_name, file_size)

file_size_dl = 0
block_sz = 8192
while True:
    buffer = u.read(block_sz)
    if not buffer:
        break

    file_size_dl += len(buffer)
    f.write(buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print status,

f.close()

# NDVI processing
# Lets create new instance of class
nd = NDVIWithManualColorMap(path=temp_folder+"/"+scene_id, dst_path=temp_folder)
# Start process
print nd.run()

# Create virtual dataset for deviding tiff into tiles
subprocess.call(["gdalbuildvrt", "-a_srs", "EPSG:3857", "NDVImap.vrt", "temp_folder/"+scene_id+"/"+ndvi_file])

# Remove old tiles
shutil.rmtree("ndvi_tiles", ignore_errors=True)

# Start process of deviding with virtual dataset
subprocess.call(["./gdal2tilesp.py", "-w", "none", "-s EPSG:3857", "-p", "mercator", "-z 8-12", "--format=PNG", "--processes=4", "-o", "tms", "NDVImap.vrt", "ndvi_tiles"])

# Let`s clean temporary files (bands, ndvi, vrt)
shutil.rmtree("temp_folder", ignore_errors=True)
os.remove("NDVImap.vrt")

print 'All temporary data was succsessfully removed'

# Close script
raise SystemExit('Closing...')

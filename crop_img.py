import gdal
import pandas as pd
import rasterio
from rasterio.tools.mask import mask
from gdalconst import *
import numpy
import json
from osgeo import gdal, ogr, osr
from scipy.ndimage import imread
import os
import pickle

# record information in Geojson file
# including categorical ids, urls for labeled image, longitude and latitude
ids = [];
urls = [];
longitude = [];
latitude = [];

# my geojson file called harvey_list.geojson, you need to replace it with your file name
with open('harvey_list.geojson') as f:
    data = json.load(f)

for feature in data['features']:
    ids.append(feature['properties']['catalog_id'])
    urls.append(feature['properties']['chip_url'])
    longitude.append(feature['geometry']['coordinates'][0])
    latitude.append(feature['geometry']['coordinates'][1])

# create dataframe to include all information above
# add one column to record possible tif file's name for each observations in geojson
json = pd.DataFrame({'ids': ids, 'urls': urls, 'long': longitude, 'lat': latitude, 'file': '0'})

# set the path to reach the folder which include tif files
# if you have the same directory with geojson file, just ignore this
os.chdir('/Users/ZachCheu/PycharmProjects/DDS/links')


# print out the range of longitutde and latitude of tif file within a square brackets
# gt is the GetGeoTransform()
# cols is the number of columns
# rows is the number of rows
def GetRange(gt, cols, rows):
    ext = []
    ranges = []
    # get corner points
    xarr = [0, cols]
    yarr = [0, rows]
    for px in xarr:
        for py in yarr:
            x = gt[0] + (px * gt[1]) + (py * gt[2])
            y = gt[3] + (px * gt[4]) + (py * gt[5])
            ext.append([y, x])
        yarr.reverse()
    ranges.append([min(ext)[1], max(ext)[1]])
    ranges.append([min(ext)[0], max(ext)[0]])
    return ranges


# create a new dataframe to record name of each tif file and its corresponding ranges
tif_Range = pd.DataFrame(columns=['file_name', 'range'])
for filename in os.listdir(os.getcwd()):
    dataset = gdal.Open(filename, GA_ReadOnly)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    geotransform = dataset.GetGeoTransform()
    result = GetRange(geotransform, cols, rows)
    tif_Range = tif_Range.append({'file_name': filename, 'range': result}, ignore_index=True)

# for each observation in geojson file, check whether its longitude and latitude are within the ranges for each tif file
# if there's a tif's range satisfy, add the name of that tif file under the 'file' column in json dataframe
# if more than one tif file satify, for now, I just used the last one
for i in range(json['file'].size):
    for j in range(tif_Range['range'].size):
        if (tif_Range['range'][j][1][0] < json['lat'][i] < tif_Range['range'][j][1][1] and tif_Range['range'][j][0][0] <
            json['long'][i] < tif_Range['range'][j][0][1]):
            json.loc[i, 'file'] = tif_Range['file_name'][j]

            # function for cropping


def Crop(filename, long, lat, output):
    dataset = gdal.Open(filename, GA_ReadOnly)
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    bands = dataset.RasterCount
    driver = dataset.GetDriver().LongName
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()
    originX = geotransform[0]  # top left x
    originY = geotransform[3]  # top left y
    pixelWidth = geotransform[1]
    pixelHeight = -geotransform[5]
    band = dataset.GetRasterBand(1)

    # want to find raster indexes of top points, p1=[minX,maxY], and p2=[maxX, minY]
    xmin = long - 0.001
    ymax = lat + 0.001
    xmax = long + 0.001
    ymin = lat - 0.001
    geoms = [{'type': 'Polygon', 'coordinates': [[(xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)]]}]
    with rasterio.open(filename) as src:
        out_image, out_transform = mask(src, geoms, crop=True)
    out_meta = src.meta.copy()

    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    # just set the directory to save cropped image
    os.chdir('C:\\Users\\Xiaoyan\\Desktop\\DDS Research\\Crop')
    with rasterio.open(output + ".tif", "w", **out_meta) as dest:
        dest.write(out_image)


# I only download 20 sample tif files
# I pick one available observation for cropping image
# later, just use a for loop to run all observations in same procedure
file = json['file'][64]
long = json['long'][64]
lat = json['lat'][64]
# create name for output
output = 'sample2'
# use the function above to crop
Crop(file, long, lat, output)
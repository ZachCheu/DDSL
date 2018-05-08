from osgeo import gdal
import requests
import shutil
import csv
import json
import pandas as pd

downloaded = True

def main():
	f = open("links", "r")
	urls = f.readlines()
	stripImgArr = []
	idCount = 1
	tif_Range = pd.DataFrame(columns=['file_name', 'range'])
	for url in urls:

		url = url.strip()
		filename = url.split('/')[-1]
		if(not filename.endswith(".ovr")):
			print(url)
			print(filename)
			path = 'images/strip_img/' + filename
			if not downloaded:
				r = requests.get(url, stream=True)
				if r.status_code == 200:  # 200: OK
					with open(path, 'wb+') as f:
						r.raw.decode_content = True
						shutil.copyfileobj(r.raw, f)
					coords = getCoords(path)
					tif_Range = tif_Range.append({'file_name': filename, 'range': coords}, ignore_index=True)
				# stripImg = [idCount, filename, coords]
				# stripImgArr.append(stripImg)
				else:
					print('error:' + r.status_code)
			else:
				coords = getCoords(path)
				tif_Range = tif_Range.append({'file_name': filename, 'range': coords}, ignore_index=True)
			# stripImg = [idCount, filename, coords]
			# stripImgArr.append(stripImg)
			idCount = idCount + 1

	#eprint(tif_Range['range'][0][1])
	tif_Range.to_pickle("tif_range")
	# myFile = open('strip_img_data.csv', 'w')
	# with myFile:
	# 	writer = csv.writer(myFile)
	# 	writer.writerows(stripImgArr)

def getCoords(filename):
	ds = gdal.Open(filename)
	width = ds.RasterXSize
	height = ds.RasterYSize
	gt = ds.GetGeoTransform()

	coord = [] # mixmiymxxmxy
	coord.append(gt[0])
	coord.append(gt[3] + width*gt[4] + height*gt[5])
	coord.append(gt[0] + width*gt[1] + height*gt[2])
	coord.append(gt[3])

	return coord

def associateJsonCsv():
	tif_Range = pd.read_pickle("tif_range")

	with open('harvey_list.geojson') as f:
		data = json.load(f)

	ids = [];
	urls = [];
	longitude = [];
	latitude = [];

	for feature in data['features']:
		ids.append(feature['properties']['catalog_id'])
		urls.append(feature['properties']['chip_url'])
		longitude.append(feature['geometry']['coordinates'][0])
		latitude.append(feature['geometry']['coordinates'][1])

	jsonDF = pd.DataFrame({'ids': ids, 'urls': urls, 'long': longitude, 'lat': latitude, 'file': '0'})

	for i in range(jsonDF['file'].size):
		for j in range(tif_Range['range'].size):
			if (tif_Range['range'][j][1] < jsonDF['lat'][i] < tif_Range['range'][j][3] and tif_Range['range'][j][0] < jsonDF['long'][i] < tif_Range['range'][j][2]):
				jsonDF.loc[i, 'file'] = tif_Range['file_name'][j]

	jsonDF.to_pickle("associateJSON")
	jsonDF.to_csv("associateJSON.csv", columns=['ids','urls','long','lat','file'])


if __name__ == '__main__':
	associateJsonCsv()
import geopandas as gpd

data = gpd.read_file('harvey_raws.geojson')
cat_out = open('catalogid.txt', 'w')
unique_ids = []

print(data)

for cat_id in data['catalog_id'].tolist():
	if cat_id not in unique_ids:
		unique_ids.append(cat_id)

for cat_id in unique_ids:
	cat_out.write(cat_id + '\n')

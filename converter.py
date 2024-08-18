import json

with open("Indian_States.txt", "r") as file:
    data = file.read()

geojson_data = json.loads(data)

with open("Indian_States.geojson", "w") as geojson_file:
    json.dump(geojson_data, geojson_file)

print("Converted TXT to GeoJSON successfully!")

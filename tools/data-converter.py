import json
import gzip
import os

import yaml

print("Loading File")
with open("./sde/bsd/invNames.yaml", "r") as stream:
    try:
        contents = yaml.safe_load(stream)
    except yaml.YAMLError as ex:
        print(ex)

print("Selecting System Names")
count = 0
systems = {}
for item in contents:
    count += 1
    if 30000000 < item['itemID'] < 33000000:
        systems[int(item['itemID'])] = {'name': item['itemName']}

print("loading system info")
for region in os.listdir('./sde/fsd/universe/eve/'):
    if 'staticdata' in region: continue
    for constellation in os.listdir(f'./sde/fsd/universe/eve/{region}'):
        if 'staticdata' in constellation: continue
        for solar_system in os.listdir(f'./sde/fsd/universe/eve/{region}/{constellation}'):
            if 'staticdata' in solar_system: continue
            with open(f"./sde/fsd/universe/eve/{region}/{constellation}/{solar_system}/solarsystem.staticdata", "r") as stream:
                contents = yaml.safe_load(stream)
                itemID = int(contents['solarSystemID'])
                print(f"{region} - {constellation} - {solar_system} - {itemID} - {contents['security']:.1f}")
                systems[itemID]['region'] = region
                systems[itemID]['constellation'] = constellation
                systems[itemID]['security'] = float(f"{contents['security']:.1f}")


json_object = json.dumps(systems, indent=None, separators=(',', ':') ).strip('\n')
print(f"System Count {count}")

print("Writing compressed json")
with gzip.open("./data/systems.json.gz", "wb") as stream:
    stream.write(json_object.encode('utf-8'))
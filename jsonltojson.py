import jsonlines
import json

def jsonltojson():
    listings = {}
    #  OLD
    with open('olx.json') as o:
        olx_json = json.load(o)
        for listing in olx_json:
            listings[listing['id']] = listing
    #  INCOMING
    with jsonlines.open('olx.jl') as reader:
        for obj in reader:
            listings[obj['id']] = obj
    #  NEW
    json_object = json.dumps(list(listings.values()), indent=4, ensure_ascii=False)
    with open('olx.json', 'w') as olx:
        olx.write(json_object)

jsonltojson()

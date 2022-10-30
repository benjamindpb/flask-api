from flask import Flask
import requests 
import json
from utils import *

app = Flask(__name__)

WDQS_ENDPOINT = 'https://query.wikidata.org/sparql'
WD_API_ENNPOINT = 'https://www.wikidata.org/w/api.php'
USER_AGENT = "wd-atlas/0.1 (benjamin.delpino@ug.uchile.cl; benjamin.dpb@gmail.com) [python-requests/2.28.1 python-flask/2.2.2]"
WD_QUERY = '''
    SELECT DISTINCT ?item ?label ?desc ?thumb ?image ?lat ?lon WHERE {{
  ?item wdt:P31/wdt:P279* wd:{} .
  ?item rdfs:label ?label .		
  optional {{?item wdt:P18 ?image .}}
  ?item wdt:P625 ?coord .  
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "en" .    
    ?item schema:description ?desc .
   }}
  # Get coordinates
  BIND(geof:longitude(?coord) AS ?lon)
  BIND(geof:latitude(?coord)  AS ?lat)
  # Generate thumbnail image
  BIND(REPLACE(wikibase:decodeUri(STR(?image)), "http://commons.wikimedia.org/wiki/Special:FilePath/", "") as ?fileName) .
  BIND(REPLACE(?fileName, " ", "_") as ?safeFileName)
  BIND(MD5(?safeFileName) as ?fileNameMD5) .
  BIND(CONCAT("https://upload.wikimedia.org/wikipedia/commons/thumb/", SUBSTR(?fileNameMD5, 1, 1), "/", SUBSTR(?fileNameMD5, 1, 2), "/", ?safeFileName, "/350px-", ?safeFileName) as ?thumb)
  
  FILTER (lang(?label)="en")  
  
}}
  '''
NO_IMAGE_SRC = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/195px-No-Image-Placeholder.svg.png'
@app.route('/data/<search>')
def data(search: str):
  qid = get_qid(search)
  Q = WD_QUERY.format(qid)
  req = requests.get(
    WDQS_ENDPOINT, 
    params={'format': 'json', 'query': Q}, 
    headers={
      'User-Agent': USER_AGENT
    }
  )
  json_ = req.json()
  results = json_["results"]["bindings"]
  L = []
  for r in results:
    try:
      d = {
          'label': r['label']['value'],
          'entity': r['item']['value'],
          'image': r['image']['value'] if 'image' in r else NO_IMAGE_SRC, 
          'thumbnail': r['thumb']['value'] if 'thumb' in r else NO_IMAGE_SRC,
          'description': r['desc']['value'],
          'lon': r['lon']['value'],
          'lat': r['lat']['value']
        }
      L.append(d)
    except:
      print("Error.", end='\r')
  return {
    'results': L,
    'count': len(L)
  }


@app.route('/autocomplete/<search>')
def autocomplete_results(search: str):
  with open('p31/1022_types.json', 'r') as f:
    jf = json.load(f) 
    # jf := {'types': {"Q123":{'label': "123", 'description': "one two three"}, "Q456": {label:..., 'description':...}, ...}, 'count':...}
    L = {}
    for item in jf["types"].items():
      label = item[1]['label']
      percentage = item[1]['percentage']
      if label!='no label' and label.lower().startswith(search.lower()) and percentage >= 0.01:
        d = {
          item[0] : item[1]
        }
        L |= d
    # This dict contains the results for the search, orderer by his "ranking" defined by the percentage of entitites with coordinates of that type of the the total of entities of that type. The order is desc.
    sorted_dict = sorted(L.items(), key=lambda item: (item[1]['entitiesWithCoords'], item[1]['percentage']), reverse=True)
    return {
      "search": search,
      "types": sorted_dict[:7]
    }




if __name__ == "__main__":
    app.run(debug=True)

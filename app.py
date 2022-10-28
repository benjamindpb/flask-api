from http.client import responses
from flask import Flask
import requests 
import json
import time
from utils import *

app = Flask(__name__)

WDQS_ENDPOINT = 'https://query.wikidata.org/sparql'
WD_API_ENNPOINT = 'https://www.wikidata.org/w/api.php'
USER_AGENT = "wd-atlas/0.1 (benjamin.delpino@ug.uchile.cl; benjamin.dpb@gmail.com) [python-requests/2.28.1 python-flask/2.2.2]"
WD_QUERY = '''
    SELECT DISTINCT ?item ?label ?desc ?thumb ?image ?lat ?lon WHERE {{
  ?item wdt:P31/wdt:P279* wd:{} .
  ?item rdfs:label ?label .		
  ?item wdt:P18 ?image .
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
  
}} limit 2000
  '''

@app.route('/data/<search>')
def data(search):
  qid = get_qid(search)
  Q = WD_QUERY.format(qid)
  req = requests.get(
    WDQS_ENDPOINT, 
    params={'format': 'json', 'query': Q}, 
    headers={
      'User-Agent': USER_AGENT
    }
  )
  json = req.json()
  results = json["results"]["bindings"]
  L = []
  for r in results:
    try:
      d = {
          'label': r['label']['value'],
          'entity': r['item']['value'],
          'image': r['image']['value'], 
          'thumbnail': r['thumb']['value'],
          'description': r['desc']['value'],
          'lon': r['lon']['value'],
          'lat': r['lat']['value']
        }
      L.append(d)
    except:
      print("Error.", end='\r')
  return {
    'results': L
  }


@app.route('/autocomplete/<search>')
def get_p31_list(search):
  with open('p31/types.json', 'r') as f:
    jf = json.load(f) # {'types': {"Q123":{'label': "123", 'description': "one two three"}}}
    L = []
    for item in jf["types"].items():
      label = item[1]['label']
      if label.lower().startswith(search.lower()):
        L.append(item)
    return {
      "search": search,
      "types": L
    }




if __name__ == "__main__":
    app.run(debug=True)

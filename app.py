from http.client import responses
from flask import Flask
import requests 
import json
import time

app = Flask(__name__)

# Wikidata Query Service endpoint
WDQS_ENDPOINT = 'https://query.wikidata.org/sparql'
# MediaWiki API endpoint
WD_API_ENNPOINT = 'https://www.wikidata.org/w/api.php'
MAGNUS_API = 'https://magnus-toolserver.toolforge.org/commonsapi.php'
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

def get_qid(search):
  qid = requests.get(WD_API_ENNPOINT, 
    params={
      'action': 'wbsearchentities',
      'search': search, 
      'language': ['en'],
      'format': 'json'
      })
  return qid.json()['search'][0]['id']


@app.route('/data2/<search>')
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
  

  

@app.route("/data1/<search>")
def get_format_data(search):
  qid = get_qid(search)
  query = '''
  SELECT ?item ?itemLabel ?itemDescription ?lon ?lat ?image
  WHERE{{
  ?item  wdt:P31/wdt:P279* wd:{}; 
    wdt:P625 ?coord; wdt:P17 ?country. 
  ?item wdt:P18 ?image . 
  BIND(geof:longitude(?coord) AS ?lon)
  BIND(geof:latitude(?coord)  AS ?lat)
  SERVICE wikibase:label {{bd:serviceParam wikibase:language "en".}}
  }} limit 1000'''.format(qid)
  response = requests.get(WDQS_ENDPOINT, params={'format': 'json', 'query': query}).content
  decode_data = json.loads(response.decode())
  L = []
  for d in decode_data["results"]["bindings"]:
    try:
      e = {
        "itemLabel": d["itemLabel"]["value"],
        "wikidataUrl": d["item"]["value"],
        "image": d["image"]["value"],
        "itemDescription": d["itemDescription"]["value"],
        "lon": d["lon"]["value"],
        "lat": d["lat"]["value"]
      }
      L.append(e)
    except:
      pass
  return {
    "results": L
  }



@app.route('/entity_type/<search>')
def get_p31_list(search):
  with open('p31/p31_types.json', 'r') as f:
    jf = json.load(f) # {'types': ["type":{'label':{..}, 'type':{...}}]}
    L = []
    for t in jf["types"]:
      if t.lower().startswith(search.lower()):
        L.append(t)
    return {
      "search": search,
      "types": L
    }
    

@app.route('/p31-ids')
def get_p31_ids():
  query = '''
  SELECT DISTINCT ?type 
  WHERE { 
    ?entity wdt:P31 ?type .
  }
  '''
  req = requests.get(WDQS_ENDPOINT, params={'format':'json', 'query':query}, 
    headers={
      'User-Agent': USER_AGENT
    })
  res = req.json() # "http://www.wikidata.org/entity/Q3" response
  L=[]
  for r in res['results']['bindings']:
    try:
      qid = r['type']['value'].split('Q')[1]
      L.append(f'Q{qid}')

    except:
      pass

  return {
    'types': L
  }

@app.route('/ask/<search>')
def ask_wd(search):
  qid = get_qid(search)
  Q = '''
  ask {{
    ?item wdt:P31/wdt:P279* wd:{} .
    ?item wdt:P625 ?coord
  }}
  '''.format(qid)

  res = requests.get(WDQS_ENDPOINT, params={'format':'json', 'query': Q})
  json = res.json()

  return {
    'boolean': json['boolean'],
    'id': qid,
    'search': search
    }




@app.route('/types2/wdqs')
def get_p31_info_wdqs():
  # get types list
  data = get_p31_ids() # {'types':['Q1','Q2',...]}
  start = time.time()
  n = 0
  values = []
  types_list = []
  N = 0
  for v in data['types']:
    values.append(f'wd:{v}')
    n += 1
    if(n == 200):
      _query = '''SELECT DISTINCT ?type ?label WHERE {{?type rdfs:label ?label . FILTER(lang(?label)='en') VALUES ?type {{{}}}}}'''.format(" ".join(values))
      response = requests.get(
        url=WDQS_ENDPOINT, 
        params={'format':'json', 'query':_query}, 
        headers={'User-Agent': USER_AGENT}
      )
      try:
        json_ = response.json()
        types_list += json_["results"]["bindings"]
        n = 0
        N += 1
        values.clear()
        print('OK.') 
      except:
        n = 0
        values.clear()
        print("Error status: ", response.status_code)
        break

  L = [t["label"]["value"] for t in types_list]  
  data = {"types": L}
  
  with open('p31/p31_types.json', 'w') as f:
    json.dump(data, f)

  print("Saved json file.")
  
  end = time.time()

  return {
    "time": {
      "value": end-start,
      "unit": "seconds"
    },
    "types": N*200,
  }

@app.route('/types2/wd-api')
def get_p31_info_wdapi():
  data = get_p31_ids() # {'types':['Q1','Q2',...]}
  n = 0
  idsList = []
  ids = ''
  for t in data["types"]:
    idsList.append(t)
    n += 1
    if n == 50:
      ids = '|'.join(idsList)
      _req = requests.get(WD_API_ENNPOINT, params={
        'action': 'wbgetentities',
        'ids': ids, # 'Q3|Q4|Q5'
        'languages': 'en',
        'props': 'labels|descriptions',
        'format': 'json'
      })
      n = 0
      ids = ''
      idsList.clear()
      print('OK')
  return 0

if __name__ == "__main__":
    app.run(debug=True)

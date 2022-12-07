from flask import Flask
from utils import *
from settings import *

app = Flask(__name__)

json_file = {}

@app.route('/data/<search>/<int:limit>')
def data(search: str, limit: int):
  try:
    qid = get_qid(search)
  except:
    print(f'QID ERROR. Search: {search}')
    return {
      'search': search,
      'error_type': 'qid not found',
      'count': -2
    }
  limit = 10**6 if limit == 0 else 10**limit
  Q = WD_QUERY.format(qid, limit)
  L = []
  try:
    response = requests.get(
      WDQS_ENDPOINT, 
      params={'format': 'json', 'query': Q}, 
      headers={
        'User-Agent': USER_AGENT,
        'Retry-After': '60'
      }
    )
    print(f'{search}/{response.status_code}')
    json_response = response.json()
    # return json_response
    results = json_response["results"]["bindings"]
    for r in results:
      if 'lon' in r and 'lat' in r:
        d = {
            'label': r['label']['value'],
            'entity': r['item']['value'],
            'image': r['image']['value'] if 'image' in r else 'no-image.png', 
            'thumbnail': r['thumb']['value'] if 'thumb' in r else 'no-image.png',
            'description': r['description']['value'] if 'description' in r else 'No description defined',
            'lon': r['lon']['value'],
            'lat': r['lat']['value'],
            'countryCode': r['countryCode']['value'] if 'countryCode' in r else 'xx'
          }
        L.append(d)
        
    return {
      'results': L,
      'count': len(L)
    }
  except:
    print(f'WDQS ERROR.')
    time.sleep(60)
    return {
      'search': search,
      'count': -1,
      'status': 500
    }


@app.route('/autocomplete/<search>')
def autocomplete_results(search: str): 
  # jf := {'types': {"Q123":{'label': "123", 'description': "one two three"}, "Q456": {label:..., 'description':...}, ...}, 'count':...}
  L = {}
  for item in json_file["types"].items():
    label = item[1]['label']
    if label!='no label' and (label.startswith(search) or search in label):
      d = {
        item[0] : item[1]
      }
      L |= d
  sorted_dict = sorted(L.items(),
    key=lambda item: (item[1]['entitiesWithCoords'], item[1]['percentage']), 
    reverse=True
  )
  
  return {
    "search": search,
    "types": sorted_dict[:7],
    "count": len(sorted_dict)
  }

if __name__ == "__main__":
  with open('p31/types.json', 'r') as f:
    json_file = json.load(f)
    app.run(debug=True)
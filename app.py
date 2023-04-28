from flask import Flask
from utils import *
from settings import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # activate CORS policy

json_file = {}
JSON_OPENED = False

@app.route('/data/<search>/<int:limit>')
def data(search: str, limit: int):
  """
    This function runs the SPARQL query to get all georeferenced instances of a type given by its label. 
    This query is found in the project's *setting.py* file and receives as arguments the label 
    to search for and the number of results to return.

    Args:
		search (str): label of the entity to search
		limit (int): integer to define the number of results to obtain 

	Returns:
		dict: if in the retrieved dictionary *count* is < 0 an error occurred. Specifically, 
    if it is equal to -2, the ID to search for is incorrect, that is, the label entered is not in Wikidata.
    On the other hand, if *count* is equal to -1, it is an error propagated by an internal 
    Wikidata Query Service error (timeout error).

  """
  try:
    qid = get_qid(search)
  except:
    print(f'QID ERROR. Search: {search}')
    return {
      'search': search,
      'error_type': 'qid not found',
      'count': -2
    }
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
    results = json_response["results"]["bindings"]
    ids = []
    for r in results:
      if 'lon' in r and 'lat' in r:
        entity = r['item']['value']
        if entity not in ids:
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
          ids.append(entity)
        
    return {
      'results': L,
      'count': len(L)
    }
  except:
    print(f'WDQS ERROR.')
    return {
      'search': search,
      'count': -1,
      'status': 500
    }


@app.route('/types')
def types():
  """
    Returns: 
      dict: with all the georeferenceable types of the database with their info.
  """
  return json_file

@app.route('/type/<id>')
def type_id(id: str):
  """
    Arg:
      id (str): identifier of a Wikidata entity.

    Returns:
      dict: with type information such as its label, description, number of instances, etc.
  """
  entity_info = json_file["types"][id]
  return entity_info


@app.route('/autocomplete/<search>')
def autocomplete_results(search: str):
  """
    This function performs a search for all georeferenced instances of a type.
    This function is very important for the autocompletion of the system. It is based on the percentage 
    of georeferenceable instances of the searched type to return first (in order) the types 
    that have more georeferenceable instances in relation to the total results.

    Arg:
      search (str): label to search

    Returns:
      dict: with all georeferenced instances of the searched type.
  """
  global JSON_OPENED, json_file
  if not JSON_OPENED:
    f = open('p31/types.json', 'r') 
    json_file = json.load(f)
    JSON_OPENED = True

  L = {}
  for item in json_file["types"].items():
    label = item[1]['label']
    # words = label.split(' ')
    # words = [l.lower() for l in]
    if label.lower().startswith(search) or search in label.split(' '):
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
    "types": sorted_dict[:],
    "count": len(sorted_dict)
  }

if __name__ == "__main__":
  app.run(host="localhost", port=5000, debug=True)

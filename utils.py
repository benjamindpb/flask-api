import bz2
import gzip
import time
import json
import requests

DUMPS_URL = 'https://dumps.wikimedia.org/wikidatawiki/entities/'

def get_new_dump(n=10000, complete_dump=False, filename='0522-latest-truthy.nt', format_str='gz'):
    """
        This function creates a new dump file in nt format.
        This new dump contains the nriples that in his Predicates contains
        the 'coordinate location' property P625 or the 'instance of property' P31.

        Args:
            n (str): number of entitites to obtain/evaluate/read
            complete_dump (bool): if this value is True the complete dump is read
            filename (str): name of the dump file. 
            format_str (str): the compression format of the dump file to read. 
            This string only can be 'gz' for gzip format or 'bz2' for bzip2 format. 

        Returns:
            list: a list with the execution time, the number of P625 triples and P31
            triples added to the new dump; and the total of triples readed.
    """
    print("Executing get_new_dump()...")
    start = time.time()

    if format_str=='gz':
        format=gzip
    elif format_str=='bz2':
        format=bz2
    else: print("Format error.")         

    n_p625, n_p31, total = [0,0,0]
    with format.open(f'dump/{filename}.{format_str}', 'rt', encoding='utf8') as dump_file, open('dump/new_dump.nt', 'wt') as new_dump:
        for ntriple in dump_file:
            total += 1
            if n_p625 == n and not complete_dump: break
            split = ntriple.split(' ')
            if ('/P625>' in split[1] or '/P31>' in split[1]) and len(split) <= 5:
                new_dump.write(ntriple)
                if '/P625>' in split[1]: n_p625 += 1
                if '/P31>' in split[1]: n_p31 += 1       
    end = time.time()
    _time = round(end-start, 2)
    print(f"Exec time: {_time} seconds.\ntotal ntriples: {total}\nn_p625: {n_p625}\nn_p31: {n_p31}.")
    print("Created and saved new_dump.nt file in /dump folder.\n")
    return [_time, n_p625, n_p31, total]


def entities_with_coords():
    print('Executing entities_with_coords...')
    start = time.time()
    entity_dict = {}
    with open('dump/new_dump.nt', 'rt') as new_dump:
        for ntriple in new_dump:
            split = ntriple.split(' ')
            if '/P625>' in split[1]:
                try:
                    qid = 'Q' + split[0].split('Q')[1][:-1]
                    entity_dict[qid] = 1
                except:
                    # print(ntriple)
                    pass
    end = time.time()
    _time = round(end-start, 2)
    print(f"Exec time: {_time} seconds.\n")
    return entity_dict, _time


def instances_of_entities(entities_dict: dict):
    print('Executing instances_of_entities()...')
    start = time.time()
    types_with_coords = {}
    types_without_coords = {}
    types_set = set()
    with open('dump/new_dump.nt', 'rt') as new_dump, open('dump/exceptions.nt', 'wt') as ex:
        for ntriple in new_dump:
            split = ntriple.split(' ')[:-1] # excludes the '.' element from the list
            if '/P31>' in split[1]:
                try: 
                    entity_id = 'Q' + split[0].split('Q')[1][:-1] # entity (Object) id
                    type_id = 'Q' + split[-1].split('Q')[1][:-1] # type (Subject) id
                    if entity_id in entities_dict:
                        types_set.add(type_id)
                        if type_id in types_with_coords:
                            types_with_coords[type_id] +=1
                        else:
                            types_with_coords[type_id] = 1 # base case
                    else: 
                        if type_id in types_without_coords:
                            types_without_coords[type_id] += 1
                        else:
                            types_without_coords[type_id] =  1 # base case    
                except:
                    print(ntriple)
                    pass
    types_dict = {}
    for _id in types_set:
        wc = types_with_coords[_id] if _id in types_with_coords else 0
        nc = types_without_coords[_id] if _id in types_without_coords else 0
        types_dict[_id] = {
            'entitiesWithCoords': wc,
            'entitiesWithoutCoords': nc
        }

    end = time.time()
    _time = round(end-start, 2)
    print(f"Exec time: {_time} seconds.\n")

    return types_dict, list(types_set), _time


def get_json(types_dict: dict, filename: str):
    types_dict = {
        "count": len(types_list),
        "types": types_dict
    }
    with open(f'p31/{filename}', 'w') as _json:
        json.dump(types_dict, _json)

    print(f"Created and saved {filename} in /p31 folder.\n")
            
def get_tsv(types_dict: dict, types_list: list, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        D = get_label_and_desc(types_list) 
        f.write(f'id\tlabel\twith_coords\twithout_coords\ttotal\n')
        for key in types_dict:
            wc = types_dict[key]['entitiesWithCoords']
            nc = types_dict[key]['entitiesWithoutCoords']
            total = wc+nc
            label = D['types'][key]['label']
            f.write(f'{key}\t{label}\t{wc}\t{nc}\t{total}\n')
    print(f'Created and save {filename} file.\n')

USER_AGENT = "wd-atlas/0.1 (benjamin.delpino@ug.uchile.cl; benjamin.dpb@gmail.com) [python-requests/2.28.1 python-flask/2.2.2]"

def get_label_and_desc(ids: list):
    print("Executing get_label_and_desc()...")
    start = time.time()
    L = []
    wbgetentities_dict = {}
    for id_ in ids:
        L.append(id_)
        if len(L) == 50:
            ids_join = "|".join(L)
            L.clear()
            fifty_entities = get_entities(ids_join)
            wbgetentities_dict |= fifty_entities
    ids_join = "|".join(L)
    wbgetentities_dict |= get_entities(ids_join)
    types_dict = {}
    for key, values in wbgetentities_dict.items():
        d = {
            key: {
                'label': values['labels']['en']['value'] if values['labels'] else 'no label',
                'description': values['descriptions']['en']['value'] if values['descriptions'] else 'no description.'
            }
        }
        types_dict |= d

    D = {
        "types": types_dict,
        "count": len(types_dict)
    }

    with open('p31/types.json', 'w') as f:
        json.dump(D, f)

    end = time.time()
    _time = round(end-start, 2)
    print(f"Exec time: {_time} seconds.\n")
    return D
    

def get_entities(join: str):
    res = requests.get('https://www.wikidata.org/w/api.php', params={
        'action': 'wbgetentities',
        'ids': join, 
        'languages': 'en',
        'props': 'labels|descriptions',
        'format': 'json'
    }, headers={'User-Agent': USER_AGENT})
    return res.json()['entities']

def get_qid(search):
  res = requests.get('https://www.wikidata.org/w/api.php', 
    params={
      'action': 'wbsearchentities',
      'search': search, 
      'language': ['en'],
      'format': 'json'
      })
  return res.json()['search'][0]['id']
        
        
if __name__ == '__main__':
    get_new_dump(n=100000)
    entity_dict, _ = entities_with_coords()
    types_dict, types_list, _ = instances_of_entities(entity_dict)
    get_tsv(types_dict, types_list, "test/content/content.tsv")



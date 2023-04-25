import bz2, gzip
import time
import json
import requests
from settings import *

def get_new_dump(n=10000, complete_dump=False, filename='0522-latest-truthy.nt', format_str='gz'):
    """
        This function creates a new dump file in nt format.
        This new dump contains the nriples that in his Predicates contains
        the 'coordinate location' property P625 or the 'instance of property' P31.

        Args:
            n (str): number of entities to obtain/evaluate/read
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

    format_lib = gzip

    if format_str=='bz2':
        format_lib=bz2      

    n_p625, n_p31, total = [0,0,0]
    with format_lib.open(f'dump/{filename}.{format_str}', 'rt', encoding='utf8') as dump_file, open('dump/new_dump.nt', 'wt') as new_dump:
        for ntriple in dump_file:
            total += 1
            if n_p625 == n and not complete_dump: break
            split = ntriple.split(' ')
            if ('/P625>' in split[1] or '/P31>' in split[1]) and len(split) <= 5:
                new_dump.write(ntriple)
                if '/P625>' in split[1]: n_p625 += 1
                if '/P31>' in split[1]: n_p31 += 1       
    end = time.time()
    _time = end-start
    print(f"Exec time: {_time} seconds.\ntotal ntriples: {total}\nn_p625: {n_p625}\nn_p31: {n_p31}.")
    print("Created and saved new_dump.nt file in /dump folder.\n")
    return [_time, n_p625, n_p31, total]
      
def entities_with_coords():
    """
        This function generates an entity dictionary 
        that stores the entities with coordinate location property.
        key: entity id (Object), value: 1 (true)

        Returns:
            dict: a dict with key: entity id (Object) & value: 1 (true)
            float: execution time
    """
    print('Executing entities_with_coords...')
    start = time.time()
    entity_dict = {}
    with open('dump/1022_new_dump.nt', 'rt') as new_dump:
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
    _time = end-start
    print(f"Exec time: {_time} seconds.\n")
    return entity_dict, _time


def instances_of_entities(entities_dict: dict, get_json=True, get_tsv=False):
    """
        This is the main function to obtain the P31 types of the entities 
        with coordinate location (P625) and the number of entities that are instances of that type with coordinates and with not coordiates.

        Args:
            entities_dict (dict): a dict with the ids of the entities with P625 property

        Returns:
            dict: with the ids of the P31 types with the count of entities related
            list: with all the P31 ids of the entities (no repeated)
            float: time execution
    """
    print('Executing instances_of_entities()...')
    start = time.time()
    types_with_coords = {}
    types_without_coords = {}
    types_set = set()
    with open('dump/new_dump.nt', 'rt') as new_dump:
        for ntriple in new_dump:
            split = ntriple.split(' ')[:-1] # [:-1] excludes the '.' object from the list
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
                    # ex.write(ntriple)
                    pass
    D = get_label_and_desc(types_set)
    types_dict = {}
    for t_id in types_set:
        if t_id in D['types']:
            label = D['types'][t_id]['label']
            if label != 'No label defined':
                wc = types_with_coords[t_id] if t_id in types_with_coords else 0
                nc = types_without_coords[t_id] if t_id in types_without_coords else 0
                total = wc + nc 
                percentage = wc / total
                if percentage >= 0.01:
                    types_dict[t_id] = {
                        'entitiesWithCoords': wc,
                        'entitiesWithoutCoords': nc,
                        'total': total,
                        'percentage': percentage,
                        'label': label,
                        'description': D['types'][t_id]['description']
                    }
    if get_json:
        D = {
            'types': types_dict,
            'count': len(types_dict)
        }
        # Save the json file in local storage
        with open('p31/types.json', 'w') as f:
            json.dump(D, f)

    end = time.time()
    _time = end-start
    print(f"Exec time: {_time} seconds.\n")

    return types_dict, _time

def get_entities(join: str):
    """
        This function make a GET request to Wikidata API to obtain
        the labels and description of entities.

        Args:
            join (str): a string with the QID's separate by "|".
            for example: Q1|Q2|Q3|...
        Returns:
            dict: Wikidata API response
    """
    res = requests.get(WD_API_ENNPOINT, params={
        'action': 'wbgetentities',
        'ids': join, 
        'languages': 'en',
        'props': 'labels|descriptions',
        'format': 'json'
    }, headers={'User-Agent': USER_AGENT})
    return res.json()['entities']


def get_qid(search):
    """
        This function returns the ID of a Wikidata entity label.

        Args:
            search (str): entity label to search 
        Returns:
            str: ID of the entity
    """
    res = requests.get(WD_API_ENNPOINT, 
    params={
        'action': 'wbsearchentities',
        'search': search, 
        'language': ['en'],
        'format': 'json'
        })
    return res.json()['search'][0]['id']

def get_label_and_desc(ids: set):
    """
        Returns the complete dict (object) with all georeferenced Wikidata instances.

        Args: 
            ids (set): set with the Wikidata georreferenced QID's
        
        Returns:
            dict: with all the georreferenced entities

    """
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
    if len(L) != 0:
        ids_join = "|".join(L)
        wbgetentities_dict |= get_entities(ids_join)
        
    types_dict = {}
    for key, values in wbgetentities_dict.items():
        if 'labels' in values:
            d = {
                key: {
                    'label': values['labels']['en']['value'] if values['labels'] else 'No label defined',
                    'description': values['descriptions']['en']['value'] if values['descriptions'] else 'No description defined'
                }
            }
            types_dict |= d
        else: print(f'{key} entity does not exist.')

    D = {
        "types": types_dict,
        "count": len(types_dict)
    }

    end = time.time()
    _time = end-start
    print(f"Exec time: {_time} seconds.\n")
    return D

def get_tsv(types_dict: dict, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'id\tlabel\twith_coords\twithout_coords\ttotal\tpercentage\n')
        for key in types_dict:
            wc = types_dict[key]['entitiesWithCoords']
            nc = types_dict[key]['entitiesWithoutCoords']
            total = wc+nc
            percentage = round(wc/total, 3)
            label = types_dict[key]['label']
            f.write(f'{key}\t{label}\t{wc}\t{nc}\t{total}\t{percentage}\n')
    print(f'Created and save {filename} file.\n')


def getjson(types_dict: dict):
    with open('p31/types.json', 'w') as f:
        json.dump(types_dict, f)


        
        
if __name__ == '__main__':
    # get_new_dump(complete_dump=True)
    # entity_dict, _ = entities_with_coords()
    # instances_of_entities(entity_dict)
    pass
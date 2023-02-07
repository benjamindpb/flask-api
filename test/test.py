
from utils import *
from app import *
import time

def performance_test():
    """
        This function is used to get information about the two dump formats that Wikidata offers (gzip and bzip2). 
        It generates tsv files that will be used to perform an analysis of the performance of these two files in being preprocessed.
    """
    N = [10**2, 10**3, 10**4, 10**5, 10**6, 10**7]
    formats = ['gz', 'bz2']
    with open('performance/performance.tsv', 'w') as perf:
        perf.write('cf\ttime\tn_p625\tn_p31\ttotal\n')
        for f in formats:
            print(f'Results for **{f}** dump file format:n')
            for k in N:
                print(f"For k = {k}", end='\n')
                _time, n_p625, n_p31, total = get_new_dump(n=k, format_str=f)
                perf.write(f'{f}\t{_time}\t{n_p625}\t{n_p31}\t{total}\n')
                print(f'Time: {_time}, n_625: {n_p625}, n_p31: {n_p31}, total: {total}')

def content_test():
    """
        To evaluate the content of timeless Wikidata dumps, a pre-processing of the May and October Wikidata dumps is performed 
        to obtain information about the content they contain. Specifically, for each georeferenced type found in each dump,
        its id, label, number of georeferenced and non-georeferenced instances, and the percentage of georeferenced instances of 
        the type are obtained, along with the total types found. The latter will be important to see how much the number 
        of georeferenceable types grows for each dump.
                
    """
    dates = ['0522', '1022'] # May, October
    for d in dates:
        get_new_dump(filename=d+'-latest-truthy.nt', complete_dump=True)
        entity_dict, _ = entities_with_coords()
        types_dict, types_list, _ = instances_of_entities(entity_dict)  # type: ignore
        get_tsv(types_dict, types_list, f'content/{d}-types.tsv')  # type: ignore
        time.sleep(600)
        
def search_label_test():
    """
        This function performs all possible searches of Wikidata georeferenceable types.
        It is obtained for each entity its id, its label, the time it takes to process it and the number of results obtained for that search. 
        This, to evaluate the performance offered by system searches.
    """
    print("Executing search_label_test()...")
    _start = time.time()
    with open('../p31/types.json', 'r') as f, open('labels/labels_perf.tsv', 'w', encoding="utf-8") as lp:
        tjson = json.loads(f.read(), strict=False)
        lp.write('id\tlabel\ttime\tresults\n')
        # n = 0
        for item in tjson["types"].items():
            # if n == 20: break
            label = item[1]['label']
            start = time.time()
            results = data(label, 0)
            end = time.time()
            search_time = round(end-start, 3)
            count = results["count"] if 'count' in results else 0
            lp.write(f'{item[0]}\t{label}\t{search_time}\t{count}\n')
            # n += 1
    _end = time.time()
    total_time = round(_end-_start, 3)
    print(f"\nTotal exec time: {total_time}")

json_file = {}
def autocomplete(search, json_file):
    """
        This is a helper function that performs the individual search for a georeferenceable type found from the preprocessing 
        and retrieval of a new Wikidata dump. Read the json file with the types and look for the type tag in it.

        Args:
            search (str): label to search
            json_file (str): json file containing the georeferenceable types

        Returns:
            double: search time
            int: number of instances of type *search* found

    """
    start = time.time()
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
    end = time.time()
    ttime = end-start
    return ttime, len(sorted_dict)


def autocomplete_test():
    """
        This function performs the search for all possible combinations of the alphabet for words of length 1, 2 and 3. 
        This will be important to evaluate the autocompletion of the system.
        
    """
    start = time.time()
    print('Execution of autocomplete_test()...')
    abc = 'abcdefghijklmnopqrstuvwxyz'
    with open('../p31/types.json', 'r') as f, open('performance/autocomplete.tsv', 'w') as auto:
        auto.write(f'search\ttime\tresults\tlength\n')
        json_file = json.load(f)
        for l1 in abc:
            t1, r1 = autocomplete(l1, json_file)
            auto.write(f'{l1}\t{t1}\t{r1}\t{len(l1)}\n')
            print(f'search: {l1}, results: {r1}, time: {t1}')
            for l2 in abc:
                ll = l1+l2
                t2, r2 = autocomplete(ll, json_file)
                auto.write(f'{ll}\t{t2}\t{r2}\t{len(ll)}\n')
                print(f'search: {ll}, results: {r2}, time: {t2}')
                for l3 in abc:
                    lll = ll+l3
                    t3, r3 = autocomplete(lll, json_file)
                    auto.write(f'{lll}\t{t3}\t{r3}\t{len(lll)}\n')
                    print(f'search: {lll}, results: {r3}, time: {t3}')
    end = time.time()
    total_time = round(end - start, 3)
    print(f"\nTotal exec time: {total_time}")

def compare_content_test():
    """
        This function performs a comparison of the rates obtained from the May and October Wikidata dump preprocesses. 
        It is used to see if there is any change in the information of some kind, such as the modification of its label 
        for example, or its deletion in the database.
    """
    print("Execution of dump content test...")
    with open("../p31/0522_types.json", "r") as types_05, open("../p31/1022_types.json", "r") as types_10:
        json_05 = json.load(types_05)
        json_10 = json.load(types_10)
        json_10_types = json_10['types']
        not_found_qid = 0
        entities_wc = []
        entities_nc = []
        for qid, values in json_05['types'].items():
            if qid not in json_10_types:
                not_found_qid += 1
                entities_wc.append(values['entitiesWithCoords'])
                entities_nc.append(values['entitiesWithoutCoords'])
                print(qid, values['label'], values['entitiesWithCoords'], end='\n')
                not_found_qid += 1
            else: # el id está en el json -> verificar label
                label_05 = values['label']
                label_10 = json_10_types[qid]['label']
                if label_05 != label_10:
                    print(f'ID: {qid}, label_05: {label_05}, label_10: {label_10}')
    print(f"Not found QIDs: {not_found_qid}")


if __name__ == '__main__':
    compare_content_test()
    
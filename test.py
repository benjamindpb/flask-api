from utils import *
from app import *
import time
import pandas as pd

def performance_test():
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
    dates = ['0522', '1022'] # May, October
    for d in dates:
        get_new_dump(filename=d+'-latest-truthy.nt', complete_dump=True)
        entity_dict, _ = entities_with_coords()
        types_dict, types_list, _ = instances_of_entities(entity_dict)  # type: ignore
        get_tsv(types_dict, types_list, f'test/content/{d}-types.tsv')  # type: ignore
        time.sleep(600)
        
def search_label_test():
    print("Executing search_label_test()...")
    _start = time.time()
    with open('p31/types.json', 'r') as f, open('test/labels/labels_perf.tsv', 'w', encoding="utf-8") as lp:
        tjson = json.loads(f.read(), strict=False)
        lp.write('id\tlabel\ttime\tresults\n')
        # n = 0
        for item in tjson["types"].items():
            # if n == 20: break
            label = item[1]['label']
            start = time.time()
            results = data(label)
            end = time.time()
            search_time = round(end-start, 3)
            count = results["count"] if 'count' in results else 0
            lp.write(f'{item[0]}\t{label}\t{search_time}\t{count}\n')
            # n += 1
    _end = time.time()
    total_time = round(_end-_start, 3)
    print(f"\nTotal exec time: {total_time}")




if __name__ == '__main__':
    # search_label_test()
    df = pd.read_csv("test/labels/labels_perf.tsv", sep='\t')
    errors = df[df['results'] < 0]
    with open('test/labels/errors.tsv', 'w') as f:
        for 
    print(errors.head())
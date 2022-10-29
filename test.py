from datetime import date
from utils import *

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
        types_dict, types_list, _ = instances_of_entities(entity_dict)
        get_tsv(types_dict, types_list, f'test/content/{d}-types.tsv')
        time.sleep(600)
        

if __name__ == '__main__':
    content_test()
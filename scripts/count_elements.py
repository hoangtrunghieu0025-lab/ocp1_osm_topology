"""Bài 2.1: đếm node, way, relation trong một file .osm.pbf.

Chạy:
    python scripts/count_elements.py                       # dùng file mặc định
    python scripts/count_elements.py data/ocp1.osm.pbf     # chỉ định file

Kết quả mong đợi với data/ocp1.osm.pbf hiện tại:
    node = 29175, way = 3955, relation = 14
"""
import sys

import osmium

DEFAULT_PBF = "data/ocp1.osm.pbf"


def make_counter():
    return {"node": 0, "way": 0, "relation": 0}


def count_elements(path):
    
    counter = make_counter()
    for o in osmium.FileProcessor(path):
        if o.is_node():
            counter["node"] += 1
        elif o.is_way():
            counter["way"] += 1
        elif o.is_relation():
            counter["relation"] += 1
    return counter



def print_report(counter, path):
    
    print(f"File: {path}")
    print(f"node = {counter['node']:,}, way = {counter['way']:,}, relation = {counter['relation']:,}")
    print(f"Total = {sum(counter.values()):,}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PBF
    counter = count_elements(path)
    print_report(counter, path)


if __name__ == "__main__":
    main()

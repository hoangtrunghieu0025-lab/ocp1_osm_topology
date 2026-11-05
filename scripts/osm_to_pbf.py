"""Đổi file .osm (XML) sang .osm.pbf.  Dùng: python scripts/osm_to_pbf.py SRC.osm DST.osm.pbf"""
import sys
import osmium

src, dst = sys.argv[1], sys.argv[2]
count = {"node": 0, "way": 0, "relation": 0}
with osmium.SimpleWriter(dst) as writer:
    for o in osmium.FileProcessor(src):
        writer.add(o)
        count["node" if o.is_node() else "way" if o.is_way() else "relation"] += 1
print(count)

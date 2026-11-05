"""Cắt một vùng bbox từ file .osm.pbf lớn, giữ way và multipolygon đầy đủ.

Cách làm (giống chiến lược "complete_ways" của osmium extract):
  P1  node nằm trong bbox
  P2  way có ít nhất 1 node trong bbox  -> lấy toàn bộ node của way đó
  P3  relation có ít nhất 1 member (node/way) nằm trong tập đã chọn
      relation type=multipolygon: kéo thêm mọi way thành viên
  P4  tính node của các way kéo thêm
  P5  ghi file: node -> way -> relation

Dùng:
  python scripts/extract_bbox.py SRC.osm.pbf DST.osm.pbf S W N E
"""
import sys

import osmium


def main(src, dst, s, w, n, e):
    in_bbox = set()          # node id nằm trong bbox
    ways = set()             # way id được chọn
    nodes = set()            # node id cần ghi
    rels = set()             # relation id được chọn
    extra_ways = set()       # way kéo thêm từ multipolygon

    print("P1: node trong bbox ...", flush=True)
    for o in osmium.FileProcessor(src, osmium.osm.NODE):
        loc = o.location
        if loc.valid() and s <= loc.lat <= n and w <= loc.lon <= e:
            in_bbox.add(o.id)
    print(f"    {len(in_bbox)} node", flush=True)

    print("P2: way chạm bbox ...", flush=True)
    for o in osmium.FileProcessor(src, osmium.osm.WAY):
        refs = [nd.ref for nd in o.nodes]
        if any(r in in_bbox for r in refs):
            ways.add(o.id)
            nodes.update(refs)
    print(f"    {len(ways)} way", flush=True)

    print("P3: relation liên quan ...", flush=True)
    for o in osmium.FileProcessor(src, osmium.osm.RELATION):
        hit = False
        for m in o.members:
            if (m.type == "w" and m.ref in ways) or (m.type == "n" and m.ref in nodes):
                hit = True
                break
        if hit:
            rels.add(o.id)
            if o.tags.get("type") == "multipolygon":
                for m in o.members:
                    if m.type == "w" and m.ref not in ways:
                        extra_ways.add(m.ref)
    print(f"    {len(rels)} relation, kéo thêm {len(extra_ways)} way", flush=True)

    if extra_ways:
        print("P4: node của way kéo thêm ...", flush=True)
        for o in osmium.FileProcessor(src, osmium.osm.WAY):
            if o.id in extra_ways:
                nodes.update(nd.ref for nd in o.nodes)
        ways |= extra_ways

    print("P5: ghi file ...", flush=True)
    count = {"node": 0, "way": 0, "relation": 0}
    with osmium.SimpleWriter(dst) as writer:
        for o in osmium.FileProcessor(src):
            if o.is_node():
                if o.id in nodes or o.id in in_bbox:
                    writer.add(o)
                    count["node"] += 1
            elif o.is_way():
                if o.id in ways:
                    writer.add(o)
                    count["way"] += 1
            elif o.is_relation():
                if o.id in rels:
                    writer.add(o)
                    count["relation"] += 1
    print("Xong:", count, flush=True)


if __name__ == "__main__":
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    src, dst = sys.argv[1], sys.argv[2]
    s, w, n, e = map(float, sys.argv[3:7])
    main(src, dst, s, w, n, e)

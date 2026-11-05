from collections import Counter

import osmium

from common import get_path, write_csv


def is_building_multipolygon(rel):
    return rel.tags.get("type") == "multipolygon" and "building" in rel.tags


def count_roles(rel):
    roles = Counter()
    for member in rel.members:
        roles[(member.type, member.role)] += 1
    return roles


def make_row(rel):
    roles = count_roles(rel)
    outer = roles[("w", "outer")]
    inner = roles[("w", "inner")]
    return [
        rel.id,
        rel.tags.get("building"),
        rel.tags.get("name", ""),
        rel.tags.get("building:levels", ""),
        rel.tags.get("height", ""),
        outer,
        inner,
        len(rel.members),
    ]


def read_rows(path):
    rows = []
    for rel in osmium.FileProcessor(path, osmium.osm.RELATION):
        if is_building_multipolygon(rel):
            rows.append(make_row(rel))
    return rows


def main():
    path = get_path()
    rows = read_rows(path)
    header = ["relation_id", "building", "name", "building_levels", "height", "outer", "inner", "members"]
    out = write_csv("mp_buildings.csv", header, rows)
    kinds = Counter(r[1] for r in rows)
    print(f"multipolygon relations with building tag: {len(rows):,}")
    for kind, count in kinds.most_common():
        print(f"  building={kind}: {count}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()

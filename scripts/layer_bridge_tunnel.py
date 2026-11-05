from collections import Counter

import osmium

from common import get_path, write_csv

KEYS = ("layer", "bridge", "tunnel")


def has_any_key(way):
    return any(key in way.tags for key in KEYS)


def make_row(way):
    return [
        way.id,
        way.tags.get("highway", ""),
        way.tags.get("layer", ""),
        way.tags.get("bridge", ""),
        way.tags.get("tunnel", ""),
        way.tags.get("name", ""),
        len(way.nodes),
    ]


def read_rows(path):
    rows = []
    for way in osmium.FileProcessor(path, osmium.osm.WAY):
        if has_any_key(way):
            rows.append(make_row(way))
    return rows


def summarize(rows):
    counts = Counter()
    for row in rows:
        for key, value in zip(KEYS, row[2:5]):
            if value != "":
                counts[key] += 1
    return counts


def main():
    path = get_path()
    rows = read_rows(path)
    header = ["way_id", "highway", "layer", "bridge", "tunnel", "name", "node_count"]
    out = write_csv("layer_bridge_tunnel.csv", header, rows)
    counts = summarize(rows)
    print(f"ways with layer, bridge or tunnel: {len(rows):,}")
    for key in KEYS:
        print(f"  {key}: {counts[key]}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()

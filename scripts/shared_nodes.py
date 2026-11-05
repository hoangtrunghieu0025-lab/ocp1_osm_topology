from collections import defaultdict

import osmium

from common import get_path, write_csv


def collect_highway_ways(path):
    node_ways = defaultdict(list)
    way_types = {}
    for way in osmium.FileProcessor(path, osmium.osm.WAY):
        highway = way.tags.get("highway")
        if highway is None:
            continue
        way_types[way.id] = highway
        for ref in {n.ref for n in way.nodes}:
            node_ways[ref].append(way.id)
    return node_ways, way_types


def select_shared(node_ways):
    return {ref: ways for ref, ways in node_ways.items() if len(ways) >= 2}


def read_locations(path, wanted):
    locations = {}
    for node in osmium.FileProcessor(path, osmium.osm.NODE):
        if node.id in wanted:
            locations[node.id] = (node.location.lat, node.location.lon)
    return locations


def build_rows(shared, locations, way_types):
    rows = []
    for ref in sorted(shared):
        ways = shared[ref]
        lat, lon = locations.get(ref, ("", ""))
        types = sorted({way_types[w] for w in ways})
        rows.append([ref, lat, lon, len(ways), " ".join(map(str, ways)), " ".join(types)])
    return rows


def main():
    path = get_path()
    node_ways, way_types = collect_highway_ways(path)
    shared = select_shared(node_ways)
    locations = read_locations(path, set(shared))
    rows = build_rows(shared, locations, way_types)
    header = ["node_id", "lat", "lon", "way_count", "way_ids", "highway_types"]
    out = write_csv("shared_nodes.csv", header, rows)
    print(f"highway ways: {len(way_types):,}")
    print(f"nodes in highway ways: {len(node_ways):,}")
    print(f"nodes shared by >= 2 highway ways: {len(shared):,}")
    print(f"max ways on one node: {max((len(w) for w in shared.values()), default=0)}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()

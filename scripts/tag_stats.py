import json
from collections import Counter, defaultdict

import osmium

from common import get_path, write_csv

KEYS = ["building", "highway", "layer", "height", "building:levels", "bridge", "tunnel", "area"]
INDOOR_KEYS = ["indoor", "level", "level:ref", "repeat_on", "door", "entrance", "room", "buildingpart"]


def new_stats():
    return {
        "elements": Counter(),
        "closed_ways": 0,
        "tagged": Counter(),
        "values": defaultdict(Counter),
        "by_type": defaultdict(Counter),
        "relation_types": Counter(),
        "roles": Counter(),
    }


def observe(stats, obj, kind):
    stats["elements"][kind] += 1
    if len(obj.tags):
        stats["tagged"][kind] += 1
    if kind == "way" and obj.nodes[0].ref == obj.nodes[-1].ref:
        stats["closed_ways"] += 1
    if kind == "relation":
        stats["relation_types"][obj.tags.get("type", "")] += 1
        if obj.tags.get("type") == "multipolygon":
            for member in obj.members:
                stats["roles"][(member.type, member.role)] += 1
    for key in KEYS + INDOOR_KEYS:
        if key in obj.tags:
            stats["values"][key][obj.tags[key]] += 1
            stats["by_type"][key][kind] += 1


def kind_of(obj):
    return "node" if obj.is_node() else "way" if obj.is_way() else "relation"


def collect(path):
    stats = new_stats()
    for obj in osmium.FileProcessor(path):
        observe(stats, obj, kind_of(obj))
    return stats


def to_jsonable(stats, top=15):
    out = {
        "elements": dict(stats["elements"]),
        "closed_ways": stats["closed_ways"],
        "tagged": dict(stats["tagged"]),
        "relation_types": dict(stats["relation_types"].most_common()),
        "roles": {f"{t}:{r}": c for (t, r), c in stats["roles"].items()},
        "by_type": {k: dict(v) for k, v in stats["by_type"].items()},
        "top_values": {k: dict(v.most_common(top)) for k, v in stats["values"].items()},
        "distinct_values": {k: len(v) for k, v in stats["values"].items()},
    }
    return out


def main():
    path = get_path()
    stats = collect(path)
    data = to_jsonable(stats)
    rows = []
    for key, counter in stats["values"].items():
        for value, count in counter.most_common():
            rows.append([key, value, count])
    out = write_csv("tag_values.csv", ["key", "value", "count"], rows)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"written: {out}")


if __name__ == "__main__":
    main()

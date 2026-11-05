from collections import Counter

import osmium

from common import get_path, parse_number, write_csv


def is_target(obj):
    return "building" in obj.tags and ("building:levels" in obj.tags or "height" in obj.tags)


def make_row(obj, kind):
    levels = obj.tags.get("building:levels")
    height = obj.tags.get("height")
    return [
        kind,
        obj.id,
        obj.tags.get("building"),
        obj.tags.get("name", ""),
        levels if levels is not None else "",
        parse_number(levels),
        height if height is not None else "",
        parse_number(height),
    ]


def read_rows(path):
    rows = []
    for obj in osmium.FileProcessor(path, osmium.osm.WAY | osmium.osm.RELATION):
        if not is_target(obj):
            continue
        kind = "way" if obj.is_way() else "relation"
        rows.append(make_row(obj, kind))
    return rows


def summarize(rows):
    summary = Counter()
    for row in rows:
        summary["total"] += 1
        summary[f"kind_{row[0]}"] += 1
        if row[4] != "":
            summary["has_levels"] += 1
        if row[6] != "":
            summary["has_height"] += 1
        if row[4] != "" and row[6] != "":
            summary["has_both"] += 1
        if row[4] != "" and row[5] == "":
            summary["levels_not_numeric"] += 1
        if row[6] != "" and row[7] == "":
            summary["height_not_numeric"] += 1
    return summary


def main():
    path = get_path()
    rows = read_rows(path)
    header = ["osm_type", "osm_id", "building", "name", "building_levels", "levels_num", "height", "height_m"]
    out = write_csv("building_levels_height.csv", header, rows)
    summary = summarize(rows)
    for key in sorted(summary):
        print(f"{key}: {summary[key]:,}")
    print(f"written: {out}")


if __name__ == "__main__":
    main()

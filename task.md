# Phân tích dữ liệu OSM khu Vinhomes Ocean Park 1 (OCP1)

## Nhiệm vụ

1. Lấy dữ liệu OSM của OCP1: định dạng `osm.pbf`.
2. Viết scripts để đếm, list danh sách:
   - node, way, relation
   - node dùng chung từ 2 way `highway` trở lên
   - relation `type=multipolygon` có tag `building`
   - way có `layer`, `bridge` hoặc `tunnel`
   - building có `levels`, `height`
3. Viết báo cáo về quy ước tag:
   - Elements: Node, Way, Relation:multipolygon
   - Map features: Key:building, Key:highway, Key:layer, Key:height, Key:building:levels
   - Simple Indoor Tagging (chuẩn bị cho phần mở rộng)

## Cấu trúc thư mục

```
ocp1-osm/
├── task.md        # file này
├── .venv/         # môi trường Python
├── data/          # ocp1.osm.pbf
├── scripts/       # các script đếm / list
├── output/        # kết quả CSV
└── report/        # báo cáo quy ước tag
```

## Phần 0 — Môi trường (đã làm)

```bash
cd ~/ocp1-osm
source .venv/bin/activate
python -c "import osmium; print(osmium.__version__)"
```

Thư viện: `osmium` (pyosmium) để đọc PBF, `requests` để tải dữ liệu.

## Phần 1 — Lấy dữ liệu `osm.pbf`

Mục tiêu: có file `data/ocp1.osm.pbf`.

Lựa chọn:
- A. Tải extract Việt Nam từ Geofabrik, cắt theo bbox bằng `osmium extract` (cần osmium-tool).
- B. Overpass API xuất `.osm` rồi chuyển sang PBF.
- C. Export bbox từ openstreetmap.org (`.osm`) rồi chuyển sang PBF.

Câu hỏi cho bạn: chọn cách nào, và bbox hay ranh giới landuse?

## Phần 2 — Scripts đếm và list

Mỗi script ghi kết quả vào `output/`.

| # | Script | Nội dung | Đầu ra |
|---|--------|----------|--------|
| 2.1 | `count_elements.py` | Đếm node, way, relation | in ra màn hình |
| 2.2 | `shared_nodes.py` | Node dùng chung bởi ≥ 2 way `highway` | `shared_nodes.csv` |
| 2.3 | `multipolygon_buildings.py` | Relation `type=multipolygon` có tag `building` | `mp_buildings.csv` |
| 2.4 | `layer_bridge_tunnel.py` | Way có `layer`, `bridge` hoặc `tunnel` | `layer_bridge_tunnel.csv` |
| 2.5 | `building_levels_height.py` | Building có `building:levels` hoặc `height` | `building_levels_height.csv` |

Điểm cần chú ý:
- 2.2 cần hai lượt đọc: lượt 1 đếm số way highway chứa mỗi node, lượt 2 lọc node đếm ≥ 2.
- 2.3 relation chỉ có member (ref), tag `building` nằm trên relation.
- 2.5 cần quyết định: building là way, relation hay cả hai; `height` có đơn vị.

## Phần 3 — Báo cáo quy ước tag

File: `report/tag_conventions.md`

1. Elements: Node, Way, Relation (`type=multipolygon`: outer/inner).
2. Map features: `building`, `highway`, `layer`, `height`, `building:levels`.
3. Simple Indoor Tagging (`indoor=*`, `level=*`, `repeat_on=*`...) — chuẩn bị cho phần mở rộng.

Mỗi mục: định nghĩa, giá trị thường gặp, ví dụ lấy từ dữ liệu OCP1, lưu ý khi xử lý.

## Tiến độ

- [x] Phần 0: môi trường
- [ ] Phần 1: dữ liệu
- [ ] Phần 2: scripts
- [ ] Phần 3: báo cáo

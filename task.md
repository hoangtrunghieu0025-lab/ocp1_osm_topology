# Phân tích dữ liệu OSM khu Vinhomes Ocean Park 1 (OCP1)

## Nhiệm vụ

1. Lấy dữ liệu OSM của OCP1: định dạng `osm.pbf`.
2. Viết scripts để đếm, list danh sách:
   - node, way, relation
   - node dùng chung từ 2 way `highway` trở lên
   - relation `type=multipolygon` có tag `building`
   - way có `layer`, `bridge` hoặc `tunnel`
   - building có `levels`, `height`
3. Viết báo cáo về quy ước tag (nay là LT3):
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

## LT1 — Lý thuyết: OSM topology (làm trước)

Mục tiêu: hiểu OSM biểu diễn quan hệ không gian (nối, giao, chứa) bằng cấu trúc dữ liệu nào, để các phần 2 và 3 làm có cơ sở.

Câu hỏi cần trả lời:
1. Topology trong OSM là gì? OSM không lưu hình học riêng, chỉ lưu node / way / relation tham chiếu nhau qua id. Điều này khác gì với mô hình simple features (point / line / polygon)?
2. Kết nối (connectivity): hai way nối nhau khi nào? Vì sao phải dùng chung node, và vì sao hai đường chỉ cắt nhau về mặt hình học mà không dùng chung node thì không được coi là giao nhau?
3. Giao lộ, cầu, hầm: `layer`, `bridge`, `tunnel` giải quyết trường hợp đường cắt nhau không giao nhau (cầu vượt) thế nào?
4. Way khép kín (closed way) và vùng (area): khi nào closed way là đường, khi nào là vùng? Vai trò của `area=yes`.
5. Relation: cấu trúc member + role; `type=multipolygon` với `outer` / `inner` biểu diễn vùng có lỗ ra sao; quy tắc vòng đóng, không cắt nhau, không chồng lên nhau.
6. Các lỗi topology thường gặp: way hở không khép, đường không nối do thiếu node chung (dangling / disconnected), node trùng vị trí nhưng khác id, multipolygon sai vai trò.
7. Từ đó: vì sao script 2.2 (node dùng chung ≥ 2 way highway) chính là cách tìm giao lộ và điểm nối của mạng đường?

Sản phẩm: `report/theory.md` — mỗi câu 1 mục, viết theo các tag `[concept]`, `[example:data]`, `[example:imagination]`, `[example:In-Out process]`, `[example:other]`, `[common-misconception]`; dẫn chứng bằng id thật trong khu OCP1 (bổ sung sau khi có dữ liệu ở Phần 1).

Tài liệu nên đọc (wiki.openstreetmap.org):
- Elements, Node, Way, Relation
- Relation:multipolygon
- Key:layer, Key:bridge, Key:tunnel
- Key:area, Highway tag usage

Cách làm: từng câu một, tôi giải thích ngắn rồi bạn tóm lại bằng lời của mình vào báo cáo.

## LT2 — Lý thuyết: IMDF (Indoor Mapping Data Format)

Mục tiêu: hiểu một chuẩn dữ liệu bản đồ trong nhà (IMDF) và so sánh cách tổ chức với OSM. Ví dụ xuyên suốt: AEON Mall (mock); mỗi câu lấy một lát cắt riêng của ví dụ này.

Câu hỏi cần trả lời:
1. IMDF là gì, ai đặt ra, dùng để làm gì? Khác gì OSM về mục đích và cách tổ chức dữ liệu?
2. Định dạng lưu trữ: một bộ IMDF gồm những file nào (GeoJSON, manifest, cấu trúc thư mục / gói nén)? Mỗi feature có những trường chung nào (`id`, `feature_type`, `geometry`, `properties`)?
3. Các loại feature chính và quan hệ phân cấp: venue, building, footprint, level, unit, opening, amenity, occupant, fixture, section, kiosk, anchor, address, relationship... cái nào chứa cái nào?
4. Tham chiếu giữa các feature: dùng id (UUID) thay cho node/way/relation. So sánh với topology của OSM.
5. Cách biểu diễn tầng (level), phòng (unit), cửa (opening) và đường đi trong nhà.

Sản phẩm: bổ sung vào `report/theory.md` thành phần riêng "IMDF", mỗi câu 1 mục, cùng bộ tag như LT1.

Tài liệu nên đọc (chưa kiểm tra liên kết; cần tìm bản mới nhất):
- Tài liệu IMDF của Apple (Apple Developer: Indoor Mapping Data Format)
- Đặc tả IMDF do OGC công bố

Cách làm: giống LT1. Tôi giải thích ngắn, bạn review, ghi `[common-misconception]` khi có chỗ hiểu sai.

## Phần 1 — Lấy dữ liệu `osm.pbf`

Mục tiêu: có file `data/ocp1.osm.pbf`.

Lựa chọn:
- A. Tải extract Việt Nam từ Geofabrik, cắt theo bbox bằng `osmium extract` (cần osmium-tool).
- B. Overpass API xuất `.osm` rồi chuyển sang PBF.
- C. Export bbox từ openstreetmap.org (`.osm`) rồi chuyển sang PBF.

Câu hỏi cho bạn: chọn cách nào, và bbox hay ranh giới landuse?

## Phần 2 — Scripts đếm và list

Bản notebook (có giải thích và biểu đồ): `ocp1_osm_analysis.ipynb`. Mở bằng `.venv/bin/jupyter lab` hoặc VS Code.

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

## LT3 — Báo cáo quy ước tag (gộp vào theory.md)

File: `report/theory.md`, mục LT3. Các khái niệm đã nói ở LT1 không nhắc lại.

1. Elements: Node, Way, Relation (`type=multipolygon`: outer/inner).
2. Map features: `building`, `highway`, `layer`, `height`, `building:levels`.
3. Simple Indoor Tagging (`indoor=*`, `level=*`, `repeat_on=*`...) — chuẩn bị cho phần mở rộng.

Mỗi mục: định nghĩa, giá trị thường gặp, ví dụ lấy từ dữ liệu OCP1, lưu ý khi xử lý.

## Tiến độ

- [x] Phần 0: môi trường
- [x] LT1: lý thuyết OSM topology (làm trước)
- [x] LT2: lý thuyết IMDF
- [x] Phần 1: dữ liệu (`data/ocp1.osm.pbf` cắt từ Geofabrik Việt Nam 2026-11-04 theo bbox; bản Overpass cũ ở `data/ocp1_overpass.osm.pbf`)
- [x] Phần 2: scripts (2.1 đến 2.5; thêm `tag_stats.py`) và notebook `ocp1_osm_analysis.ipynb` (cùng kết quả, có biểu đồ; hình lưu ở `output/figures/`)
- [x] LT3: quy ước tag (`report/theory.md`, mục LT3)

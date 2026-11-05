# Báo cáo lý thuyết: LT1 (OSM topology), LT2 (IMDF) và LT3 (Quy ước tag)

## Quy ước các tag trong báo cáo

| Tag | Nội dung |
|-----|----------|
| `[concept]` | Khái niệm, định nghĩa, quy tắc |
| `[example:data]` | Mẫu dữ liệu thật hoặc mock để  hiểu rõ **cấu trúc dữ liệu** |
| `[example:imagination]` | Ví dụ đời thường, hình ảnh gần gũi với người|
| `[example:In-Out process]` | Ví dụ từ đầu đến cuối: đầu vào → các giai đoạn biến đổi → đầu ra (có sơ đồ) |
| `[example:other]` | Ví dụ ngắn, nhỏ lẻ, tự do |
| `[common-misconception]` | Nhật ký hỏi-đáp khi review |
| `[values]` | (chỉ LT3) Giá trị thường gặp, đếm trên dữ liệu OCP1 |
| `[handling]` | (chỉ LT3) Lưu ý khi xử lý bằng code |

Cách ghi `[common-misconception]`, mỗi lần một mục:

```
- Hiểu của người học: <nguyên văn ý hiểu>
  Đánh giá: đúng / đúng một phần / sai
  Phần sai và giải thích: <...>
  Cách nhớ đúng: <...>
```

Dữ liệu mẫu thật nằm ở `data/samples/` (lấy từ Overpass API và OSM API ngày 2026-11-05, bbox OCP1).

---

# LT1 — OSM topology

Tương ứng mục LT1 trong `task.md`.

## LT1.1 — Topology trong OSM là gì

**[concept]**
OSM không lưu hình học trực tiếp. Dữ liệu gồm 3 loại phần tử, tham chiếu nhau qua id:

- **Node:** một điểm (id, lat, lon, tag). Chỉ là một điểm, không mặc định là tâm của đối tượng nào.
- **Way:** danh sách có thứ tự các node id, tạo thành đường hoặc vùng.
- **Relation:** danh sách member (node, way hoặc relation khác), mỗi member có một `role`.

Topology ở đây là quan hệ qua tham chiếu: way dùng node nào, relation chứa phần tử nào. Mô hình simple features (point / line / polygon, như PostGIS) thì ngược lại: mỗi đối tượng mang hình học riêng, quan hệ chỉ tính ra từ tọa độ.

**[example:data] — cấu trúc đầy đủ (ví dụ minh họa, id tự đặt, không phải dữ liệu thật)**

Một khu nhỏ gồm: 2 con đường cắt nhau, 1 tòa nhà có sân trong. Viết theo định dạng XML của OSM, đủ mọi trường:

```xml
<!-- ===== NODE: một điểm ===== -->
<node id="9" version="3" timestamp="2024-05-01T08:00:00Z"
      changeset="1000" uid="42" user="nguyenvana"
      lat="21.00000" lon="105.95000">
  <tag k="highway" v="traffic_signals"/>      <!-- node 9 = ngã tư, có đèn -->
</node>
<node id="10" version="1" timestamp="2024-05-01T08:00:00Z" changeset="1000" uid="42" user="nguyenvana" lat="21.00000" lon="105.94900"/>
<node id="11" version="1" timestamp="2024-05-01T08:00:00Z" changeset="1000" uid="42" user="nguyenvana" lat="21.00000" lon="105.95100"/>
<node id="12" version="1" timestamp="2024-05-01T08:00:00Z" changeset="1000" uid="42" user="nguyenvana" lat="21.00100" lon="105.95000"/>
<!-- nodes 1-4: bốn góc tường ngoài; nodes 5-8: bốn góc sân trong (cùng cấu trúc, bỏ bớt) -->

<!-- ===== WAY: danh sách node + tag ===== -->
<way id="101" version="2" timestamp="2024-05-01T08:05:00Z"
     changeset="1001" uid="42" user="nguyenvana">
  <nd ref="10"/> <nd ref="9"/> <nd ref="11"/>   <!-- Đường A: đi qua node 9 -->
  <tag k="highway" v="residential"/>
  <tag k="name"    v="Đường A"/>
</way>
<way id="102" version="1" timestamp="2024-05-01T08:06:00Z"
     changeset="1001" uid="42" user="nguyenvana">
  <nd ref="9"/> <nd ref="12"/>                  <!-- Đường B: cũng đi qua node 9 -->
  <tag k="highway" v="residential"/>
  <tag k="name"    v="Đường B"/>
</way>
<way id="103" version="1" timestamp="2024-05-02T09:00:00Z"
     changeset="1002" uid="43" user="tranthib">
  <nd ref="1"/> <nd ref="2"/> <nd ref="3"/> <nd ref="4"/> <nd ref="1"/>  <!-- đầu = cuối => khép kín -->
</way>
<way id="104" version="1" timestamp="2024-05-02T09:00:00Z"
     changeset="1002" uid="43" user="tranthib">
  <nd ref="5"/> <nd ref="6"/> <nd ref="7"/> <nd ref="8"/> <nd ref="5"/>  <!-- sân trong, khép kín -->
</way>

<!-- ===== RELATION: nhóm các phần tử, mỗi member có role ===== -->
<relation id="201" version="1" timestamp="2024-05-02T09:01:00Z"
          changeset="1002" uid="43" user="tranthib">
  <member type="way" ref="103" role="outer"/>   <!-- vòng ngoài -->
  <member type="way" ref="104" role="inner"/>   <!-- lỗ (sân trong) -->
  <tag k="type"            v="multipolygon"/>
  <tag k="building"        v="apartments"/>
  <tag k="building:levels" v="5"/>
  <tag k="height"          v="18"/>
</relation>
```

Các trường chia 2 nhóm:

| Nhóm | Trường | Ý nghĩa |
|------|--------|---------|
| Định danh + cấu trúc (dùng cho topology) | `id` | Mã duy nhất trong từng loại phần tử |
| | `lat`, `lon` | Tọa độ (chỉ node có) |
| | `<nd ref>` | Way trỏ tới node nào, theo thứ tự |
| | `<member type ref role>` | Relation trỏ tới phần tử nào, vai trò gì |
| | `<tag k v>` | Cặp khóa-giá trị mô tả ý nghĩa |
| Lịch sử chỉnh sửa (metadata) | `version`, `timestamp`, `changeset`, `uid`, `user` | Ai sửa, khi nào, lần thứ mấy |

Đọc ví dụ này: node `9` nằm trong cả way `101` và `102` → đó là ngã tư (LT1.2). Way `103` và `104` đều khép kín, và không có tag riêng; tag `building` nằm trên relation `201` (LT1.5).

**[example:data] — dữ liệu thật trích từ OCP1**
Một way thật (nguồn: OSM API, `way/1222467961/full`): thân nhà trường, vòng ngoài của một tòa nhà. Way chỉ chứa **danh sách id**, tọa độ nằm ở các node:

```json
// WAY 1222467961  (không có tag; tag nằm trên relation, xem LT1.5)
"nodes": [11337999601, 11337999602, 11337999603, 11337999604, 11337999605,
          11337999606, 11337999607, 11337999608, 11337999609, 11337999610,
          11337999601]          // <- đầu = cuối  => way khép kín

// NODE 11337999601
{ "type": "node", "id": 11337999601, "lat": 20.9938205, "lon": 105.9387248 }
// NODE 11337999602
{ "type": "node", "id": 11337999602, "lat": 20.9935909, "lon": 105.9389278 }
// NODE 11337999603
{ "type": "node", "id": 11337999603, "lat": 20.9939186, "lon": 105.9391385 }
```

Nhận xét: 10 node khác nhau, id cuối lặp lại id đầu để khép vòng. Muốn vẽ tòa nhà phải tra tọa độ từng id.

**[example:imagination]**
Node giống **cây cột mốc** cắm trên đất. Way giống **tờ danh sách** "đi từ cột số 1 → 2 → 3 …". Relation giống **hồ sơ** gom nhiều tờ danh sách và ghi chú "tờ này là ranh ngoài, tờ kia là lỗ bên trong". Mọi thứ chỉ nói "cột nào", không tự chứa tọa độ trên tờ danh sách.

**[example:In-Out process]**
```
Vào: file .osm.pbf  (node + way + relation)
  │
  ├─ đọc node   → bảng  id → (lat, lon)
  ├─ đọc way    → bảng  id → [node id ...] + tags
  └─ đọc relation → bảng id → [(member, role) ...] + tags
  │
  ▼
Ra: dựng lại hình học bằng cách tra id qua các bảng
```

**[example:other]**
Tòa nhà thường là một way khép kín, node của nó là các **góc tường**, không phải tâm. Nếu tòa nhà chỉ là một node đơn (`building=yes` trên node) thì node đó chỉ đánh dấu vị trí xấp xỉ.

**[common-misconception]**
- Hiểu của người học: node của một tòa nhà có phải là vị trí tâm của tòa nhà không?
  Đánh giá: sai một phần.
  Phần sai và giải thích: node là một điểm thuần, không tự mang nghĩa "tâm". Tòa nhà thường là way khép kín, các node là góc tường.
  Cách nhớ đúng: node = một điểm trên bản đồ; ý nghĩa của nó do way/relation/tag dùng nó quyết định.

- Hiểu của người học: tag giúp truy vấn (tra `highway` ra mọi node/way/relation có key đó); key `highway` là một "không gian", value là các đối tượng nhỏ trong đó như cái cây, mailbox, cột đèn.
  Đánh giá: đúng một phần.
  Phần sai và giải thích: (1) Ý truy vấn theo key là đúng. (2) Key là nhóm chủ đề phân loại, không phải không gian chứa đồ vật; value của `highway` chủ yếu là loại đường (`motorway`, `residential`...) và vài điểm gắn với đường (`traffic_signals`, `crossing`, `bus_stop`, `street_lamp`). Cây là `natural=tree`, hòm thư là `amenity=post_box`, thuộc nhóm khác. 

- Hiểu của người học: ý nghĩa của key/value là tùy người định nghĩa; có người muốn `highway` trả về loại đường, có người muốn trả về vật thể tại chỗ đó (`highway:traffic-light`, `highway:barriers`), hay `hotel:pool` thay vì `hotel:luxury`.
  Đánh giá: đúng một phần.
  Phần sai và giải thích: (1) Về kỹ thuật tag tự do, nhưng ý nghĩa thực tế do quy ước cộng đồng (OSM Wiki, taginfo) quyết định; tag tự chế thì phần mềm không hiểu. (2) `highway` đã gồm cả loại đường lẫn vật thể bên đường (`traffic_signals`, `street_lamp`, `bus_stop`) theo quy ước, không phải hai trường phái. (3) Cú pháp là `key=value`; dấu `:` nằm trong key để chia nhánh (`building:levels=5`), nên `highway:traffic-light` và `hotel:pool` không phải dạng chuẩn. Khách sạn là `tourism=hotel` + `stars=5`; bể bơi là `leisure=swimming_pool` hoặc `swimming_pool=yes`.
  Cách nhớ đúng: viết thì tự do, nhưng hiểu thì phải theo chuẩn chung; `=` ngăn key với value, `:` chỉ chia nhánh trong key.

---

## LT1.2 — Kết nối (connectivity)

**[concept]**
Hai way chỉ nối nhau khi **dùng chung một node** (cùng id). Hai đường cắt nhau trên bản đồ mà không chung node thì với bộ định tuyến vẫn là hai đường rời. Hai node trùng tọa độ nhưng khác id cũng không phải là kết nối.

Hệ quả: node có mặt trong ≥ 2 way `highway` là giao lộ hoặc điểm nối của mạng đường.

**[example:data]**
Đường Trâu Quỳ (way `50535542`, `highway=tertiary`) có 111 node. Kiểm tra từng node với Overpass (`way(bn)`), một số node được các way highway khác dùng chung:

```
node 642954579 -> thuộc 4 way highway:
    50535542    tertiary     "Đường Trâu Quỳ"
    50535563    residential
    1080457686  secondary    "Phố Ngô Xuân Quảng"
    1124954935  residential
node 642954600 -> 50535542 (tertiary)  +  244380031 (residential, "Ngõ 257 Đường Trâu Quỳ")
node 642954607 -> 50535542 (tertiary)  +  1051033278 (service)
node 642954610 -> 50535542 (tertiary)  +  1040451801 (primary, "Đường Lý Thánh Tông")
```

Nhận xét: node `642954579` là một ngã nhiều nhánh (4 way). Trong số node của Đường Trâu Quỳ tôi chỉ kiểm tra 9 node, nên đây chưa phải danh sách đầy đủ giao lộ của đường này.

**[example:imagination]**
Hai con đường giống hai sợi dây thừng. Muốn người đi chuyển từ dây này sang dây kia thì phải **buộc chúng tại một nút**. Hai dây chỉ vắt chéo nhau, không buộc, thì người đi không sang được.

**[example:In-Out process]**
```
Vào : tất cả way có tag highway
Giai đoạn 1: với mỗi way, mỗi node id trong way → đếm[node id] += 1
Giai đoạn 2: lọc đếm[node id] >= 2
Ra  : danh sách node giao lộ / điểm nối   (script 2.2)

Ví dụ:  Way A=[1,2,3]  Way B=[2,4]  Way C=[2,5]
        đếm: 1→1, 2→3, 3→1, 4→1, 5→1   =>  ra: node 2 (3 way)
```

**[common-misconception]** (chưa có mục nào)

---

## LT1.3 — Cầu, hầm, layer

**[concept]**
Cầu vượt cắt ngang đường bên dưới nhưng **không được dùng chung node**, nếu không hai đường sẽ bị coi là thông nhau. Biểu diễn bằng:

- `bridge=yes` / `tunnel=yes`: đánh dấu đoạn vượt hoặc chui.
- `layer=*`: thứ tự chồng nhau theo chiều dọc (mặc định 0; cầu thường 1, hầm thường -1).

`layer` chỉ nói cái nào nằm trên cái nào, không gán chiều cao thực.

**[example:data]**
Hai way thật trong khu OCP1 (nguồn: Overpass):

```json
// WAY 761986897 : cầu B1-05 (đường cao tốc)
{ "nodes": [3878471251, 7119403368],
  "tags": { "bridge": "yes", "layer": "2", "highway": "motorway",
            "name": "Cầu B1-05", "name:en": "B1-05 Bridge",
            "ref": "CT.04", "lanes": "3", "maxspeed": "120", "oneway": "yes" } }

// WAY 896461935 : đoạn đường hẻm đi qua cầu nhỏ
{ "nodes": [8333375525, 8333375524],
  "tags": { "bridge": "yes", "layer": "1", "highway": "service", "service": "alley" } }
```

Nhận xét: `bridge`, `layer` và `highway` nằm chung trên một way. Cầu B1-05 có `layer=2`, đường hẻm có `layer=1`: số lớn hơn nằm trên.

**[example:imagination]**
Cầu vượt giống **tầng 2 của một tòa nhà**: đứng ngay trên đầu tầng 1 nhưng không có cầu thang thông giữa hai tầng. `layer` là số tầng; node chung là cầu thang.

**[common-misconception]** (chưa có mục nào)

---

## LT1.4 — Way khép kín và vùng (area)

**[concept]**
Closed way là way có node đầu trùng node cuối. OSM không có kiểu "polygon" riêng. Closed way là đường hay vùng phụ thuộc vào tag:

- `building=*` → vùng.
- `highway=*` → thường là đường (bùng binh `junction=roundabout` là đường vòng).
- Khi mơ hồ, `area=yes` / `area=no` ép cách hiểu.

**[example:data]**
Way `1222467961` ở LT1.1: `nodes[0] == nodes[-1] == 11337999601` → closed way. Tag của nó nằm ở relation cha có `building=school`, nên nó là một vòng của vùng nhà trường.

**[example:imagination]**
Một sợi dây thừng có đầu buộc vào cuối thành vòng: nếu đặt trên sân là **chiếc nhẫn** (vòng đua, đường vòng) hay là **ranh giới sân** (vùng) tùy tấm biển (tag) treo kèm.

**[example:other]**
Way [1, 2, 3, 4, 1] + `building=yes` → một tòa nhà. Cùng way đó + `highway=service` → một đường vòng.

**[common-misconception]** (chưa có mục nào)

---

## LT1.5 — Relation và multipolygon

**[concept]**
Relation nhóm các phần tử có quan hệ logic (tuyến bus, hạn chế rẽ, vùng có lỗ). Mỗi member có `role`.

`type=multipolygon`:

- `outer`: vòng ngoài.
- `inner`: lỗ bên trong (sân trong tòa nhà, hồ trong công viên).

Quy tắc: mỗi vòng khép kín (có thể ghép từ nhiều way), `inner` nằm trong `outer`, các vòng không cắt và không chồng nhau.

Vị trí đặt tag: multipolygon một vòng thường để tag trên way; nhiều vòng hoặc có lỗ thì để tag (như `building`) trên relation. Vì vậy script 2.3 phải quét relation.

**[example:data]**
Relation thật trong OCP1 (nguồn: Overpass), một tòa nhà trường học có 4 sân trong:

```json
// RELATION 16676566
{ "tags": { "type": "multipolygon", "building": "school" },
  "members": [
    { "type": "way", "ref": 1222467961, "role": "outer" },
    { "type": "way", "ref": 1222467964, "role": "inner" },
    { "type": "way", "ref": 1222467962, "role": "inner" },
    { "type": "way", "ref": 1222467963, "role": "inner" },
    { "type": "way", "ref": 1222467965, "role": "inner" } ] }

// WAY inner 1222467964 : 7 node phân biệt, khép kín
"nodes": [11337999621, 11337999622, 11337999623, 11337999624,
          11337999625, 11337999626, 11337999627, 11337999621]
```

Nhận xét: tag `building=school` nằm trên **relation**, không nằm trên các way thành viên. Một relation tương tự là `16676568` (1 outer + 6 inner).

**[example:imagination]**
Chiếc **bánh donut**: vòng ngoài là mép bánh (`outer`), lỗ ở giữa là chỗ trống (`inner`). Nếu chỉ vẽ mép ngoài mà quên lỗ thì phần lỗ cũng bị tính là bánh. Tòa nhà trường có 4 sân trong giống chiếc bánh có 4 lỗ.

**[example:In-Out process]**
```
Vào : tất cả relation
Giai đoạn 1: giữ relation có type=multipolygon
Giai đoạn 2: giữ relation có tag building
Giai đoạn 3: đếm member theo role (outer / inner)
Ra  : bảng  relation id | building | số outer | số inner   (script 2.3)

Ví dụ: 16676566 | school | 1 | 4
```

**[common-misconception]** (chưa có mục nào)

---

## LT1.6 — Lỗi topology thường gặp

**[concept]**

| Lỗi | Hậu quả |
|-----|---------|
| Đường cắt nhau không chung node | Không rẽ được, định tuyến sai |
| Đường dừng gần đường khác nhưng không chạm (dangling) | Đường cụt giả |
| Hai node cùng tọa độ, khác id | Trông nối nhưng không nối |
| Way vùng không khép kín | Không vẽ được thành polygon |
| Role `outer` / `inner` sai hoặc thiếu | Lỗ không hiện hoặc vùng sai |
| Cầu dùng chung node với đường dưới | Bị coi là giao nhau |

**[common-misconception]** (chưa có mục nào)

---

## LT1.7 — Liên hệ với nhiệm vụ

**[concept]**
- Script 2.2: tìm giao lộ bằng đếm số way `highway` trên mỗi node.
- Script 2.3: liệt kê building dạng multipolygon.
- Script 2.4: tìm đối tượng có `layer` / `bridge` / `tunnel` (topology theo chiều dọc).
- Script 2.5: building có `building:levels`, `height`.

---

### Nguồn tham khảo LT1 (OSM Wiki)

Nội dung các trang này đã tải về được ngày 2026-11-05.

- Elements: https://wiki.openstreetmap.org/wiki/Elements
- Node: https://wiki.openstreetmap.org/wiki/Node
- Way: https://wiki.openstreetmap.org/wiki/Way
- Relation: https://wiki.openstreetmap.org/wiki/Relation
- Relation:multipolygon: https://wiki.openstreetmap.org/wiki/Relation:multipolygon
- Key:layer: https://wiki.openstreetmap.org/wiki/Key:layer
- Key:bridge: https://wiki.openstreetmap.org/wiki/Key:bridge
- Key:tunnel: https://wiki.openstreetmap.org/wiki/Key:tunnel
- Key:area: https://wiki.openstreetmap.org/wiki/Key:area
- Key:highway: https://wiki.openstreetmap.org/wiki/Key:highway

---

# LT2 — IMDF (Indoor Mapping Data Format)

Tương ứng mục LT2 trong `task.md`. Nội dung đã được **đối chiếu với đặc tả IMDF 1.0.0** do OGC công bố (docs.ogc.org/cs/20-094, tải ngày 2026-11-05); dữ liệu AEON Mall vẫn là mock.

### Kết quả đối chiếu đặc tả (đã sửa trong LT2)

| Điểm | Bản nháp ban đầu | Theo đặc tả | Đã sửa |
|------|------------------|-------------|--------|
| Category của unit "Siêu thị" | `retail` | **Không có** `retail` trong danh sách category của unit (và cũng không có category riêng cho cửa hàng). Ví dụ dùng `room` cho gian hàng; tên cửa hàng nằm ở `occupant` | Đổi sang `room` |
| Phần mở rộng tên gói | `.imdf` | Gói là file **`.zip`** | Đổi |
| Tệp bắt buộc | chỉ nói có `manifest.json` | `manifest.json`, `address.geojson`, `venue.geojson` **bắt buộc**; các file còn lại tùy chọn; chỉ **một** venue | Bổ sung ở LT2.2 |
| Nối tầng bằng thang cuốn / thang máy | chưa biết | Mỗi tầng có một `unit` (`escalator` / `elevator`), nối bằng feature **`relationship`** | Bổ sung ở LT2.5 |
| `building.category` | thiếu | **Bắt buộc** (`parking`, `transit`, `transit.bus`, `transit.train`, `unspecified`) | Thêm `unspecified` |
| `venue.display_point` | thiếu | Có trong thuộc tính của venue, kiểu không null | Thêm |
| Quan hệ venue ↔ building | ghi là suy đoán | **Theo hình học**: mọi feature khác phải nằm trong đa giác của venue; không có trường `venue_id` | Ghi rõ ở LT2.3 |
| OGC "chuẩn hóa" | nói mơ hồ | Là **OGC Community Standard**: duyệt 2021-02-02, xuất bản 2021-02-18, phiên bản 1.0.0 (do Apple, Autodesk, Esri, Google, NYC DoITT, Ordnance Survey, Safe Software đề xuất) | Sửa ở LT2.1 |

Điểm **đã đúng** ngay từ đầu: 16 loại feature; mỗi feature có `id` (UUID), `type`, `feature_type`, `geometry`, `properties`; building có `geometry: null` (hình dạng ở `footprint`); occupant có `geometry: null` và trỏ qua `anchor_id`; anchor là Point có `unit_id`; amenity là Point có `unit_ids`; opening là LineString có `door` và `level_id`; `footprint.building_ids`; `level.ordinal` (0 là tầng mặt đất, -1 là tầng ngay dưới), `outdoor`, `building_ids`; `venue.category = shoppingcenter`, `opening.category = pedestrian`, `occupant.category = supermarket`, `amenity.category = atm`, `unit.category` gồm `walkway`, `restroom`, `escalator`, `elevator`, `foodservice`.

## LT2.0 — Ví dụ xuyên suốt: AEON Mall (mock)

Toàn bộ LT2 dùng một ví dụ giả lập: trung tâm thương mại **"AEON Mall Mock"**. Đây là dữ liệu **tự bịa để minh họa**, không phải dữ liệu thật của AEON. Tên trường và giá trị `category` đã đối chiếu với đặc tả IMDF 1.0.0 (xem bảng ở đầu LT2).

### a) Nhìn từ bên ngoài

**[example:imagination]**
Đứng ngoài đường, bạn thấy một khu trung tâm thương mại:
- Một **khu đất** rộng gồm tòa nhà chính và bãi xe (đây là *venue*).
- Một **tòa nhà chính** ba tầng: một tầng hầm để xe, tầng 1, tầng 2 (đây là *building*).
- **Dấu chân** của tòa nhà trên mặt đất, như khi nhìn từ máy bay (đây là *footprint*).
- Một **địa chỉ** ghi trên cổng (*address*).

Bước vào trong, mỗi tầng chia thành:
- Các **không gian**: siêu thị, cửa hàng thời trang, nhà vệ sinh, sảnh, thang cuốn, thang máy, khu ăn uống (*unit*).
- Các **cửa** nối chúng (*opening*).
- Các **tiện ích**: cây ATM (*amenity*).
- Các **đơn vị thuê** gắn tên: "Siêu thị" (*occupant*).

### b) Mặt bằng tầng 1 (mock, không theo tỷ lệ)

```
┌─────────────────────────────────────────────────────┐
│  Cửa hàng thời trang A  │   Nhà vệ sinh  │ Thang máy│
│        (unit 02)        │    (unit 03)   │ (unit 06)│
│─────────[cửa 03]────────┴────────────────┴──────────│
│                  Sảnh trung tâm (unit 04)    ATM    │
│                                           Thang cuốn│
│─────[cửa 02]────────────────────────────── (unit 05)│
│                                                     │
│           Siêu thị (unit 01)                        │
│                                                     │
└──────────────────[cửa 01 = cửa chính]───────────────┘
```

### c) Cây file trong gói IMDF

```
aeon_mock.zip   (giải nén ra các file bên dưới)
├─ manifest.json
├─ address.geojson       (1 feature)
├─ venue.geojson         (1 feature)
├─ building.geojson      (1 feature)
├─ footprint.geojson     (1 feature)
├─ level.geojson         (3 feature: B1, 1F, 2F)
├─ unit.geojson          (8 feature: 6 ở tầng 1 + 2 ở tầng 2)
├─ opening.geojson       (3 feature)
├─ amenity.geojson       (1 feature: ATM)
├─ anchor.geojson        (1 feature)
├─ relationship.geojson  (1 feature: thang cuốn 1F → 2F)
└─ occupant.geojson      (1 feature: "Siêu thị")
```

Một **file** = một **loại** (feature type); mỗi **dòng/phần tử** trong file = một **feature** (xem LT2.2).

### d) Sơ đồ phân cấp và id dùng trong ví dụ

Id được đặt dễ đọc (đúng dạng UUID nhưng số cuối là số thứ tự) để dễ theo dõi:

```
venue      10000000-0000-4000-8000-000000000001  "AEON Mall Mock"
└─ building 20000000-0000-4000-8000-000000000001  "Tòa chính"
    ├─ footprint 21000000-...-000000000001
    ├─ level 30000000-...-000000000001  "B1"  ordinal -1
    ├─ level 30000000-...-000000000002  "1F"  ordinal  0
    │   ├─ unit 40000000-...-000000000001  Siêu thị
    │   ├─ unit 40000000-...-000000000002  Cửa hàng thời trang A
    │   ├─ unit 40000000-...-000000000003  Nhà vệ sinh
    │   ├─ unit 40000000-...-000000000004  Sảnh trung tâm
    │   ├─ unit 40000000-...-000000000005  Thang cuốn
    │   ├─ unit 40000000-...-000000000006  Thang máy
    │   ├─ opening 50000000-...-000000000001..3  (3 cửa)
    │   └─ amenity 90000000-...-000000000001  ATM
    └─ level 30000000-...-000000000003  "2F"  ordinal  1
        ├─ unit 40000000-...-000000000007  Khu ăn uống
        └─ unit 40000000-...-000000000008  Thang cuốn (2F)
address  60000000-...-000000000001
anchor   70000000-...-000000000001   (nằm trong unit Siêu thị)
occupant 80000000-...-000000000001   "Siêu thị"
relationship 95000000-...-000000000001  thang cuốn 1F (unit ...0005) → 2F (unit ...0008)
```

### e) Dữ liệu từng file, đi từ ngoài vào trong

Tọa độ và hình học được rút gọn (đa giác chỉ vài điểm). Dấu `...` nghĩa là bỏ bớt phần lặp.

**manifest.json**: mô tả gói.
```json
{ "version": "1.0.0", "created": "2026-11-05T00:00:00Z",
  "language": "vi", "generated_by": "mock" }
```

**address.geojson**: địa chỉ cổng chính.
```json
{ "id": "60000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "address", "geometry": null,
  "properties": { "address": "1 Đường Mock", "locality": "Hà Nội", "country": "VN" } }
```

**venue.geojson**: cả khu đất.
```json
{ "id": "10000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "venue",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9500,21.0000],[105.9520,21.0000],[105.9520,21.0020],[105.9500,21.0020],[105.9500,21.0000]]] },
  "properties": { "category": "shoppingcenter",
                  "name": { "vi": "AEON Mall Mock" },
                  "display_point": { "type": "Point", "coordinates": [105.9510, 21.0010] },
                  "address_id": "60000000-0000-4000-8000-000000000001" } }
```

**building.geojson**: tòa nhà chính.
```json
{ "id": "20000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "building", "geometry": null,
  "properties": { "category": "unspecified",
                  "name": { "vi": "Tòa chính" },
                  "address_id": "60000000-0000-4000-8000-000000000001" } }
```

**footprint.geojson**: hình chiếu mặt đất của tòa nhà, trỏ tới tòa nhà.
```json
{ "id": "21000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "footprint",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0003],[105.9517,21.0003],[105.9517,21.0017],[105.9503,21.0017],[105.9503,21.0003]]] },
  "properties": { "category": "ground",
                  "building_ids": ["20000000-0000-4000-8000-000000000001"] } }
```

**level.geojson**: ba tầng (chỉ in 1F; B1 và 2F cấu trúc giống, khác `ordinal`, `name`).
```json
{ "id": "30000000-0000-4000-8000-000000000002", "type": "Feature",
  "feature_type": "level",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0003],[105.9517,21.0003],[105.9517,21.0017],[105.9503,21.0017],[105.9503,21.0003]]] },
  "properties": { "category": "unspecified", "ordinal": 0, "outdoor": false,
                  "name": { "vi": "Tầng 1" }, "short_name": { "vi": "1F" },
                  "building_ids": ["20000000-0000-4000-8000-000000000001"] } }
```

**unit.geojson**: các không gian trên tầng. In hai unit:
```json
{ "id": "40000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "unit",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0003],[105.9517,21.0003],[105.9517,21.0008],[105.9503,21.0008],[105.9503,21.0003]]] },
  "properties": { "category": "room",
                  "name": { "vi": "Siêu thị" },
                  "level_id": "30000000-0000-4000-8000-000000000002" } }

{ "id": "40000000-0000-4000-8000-000000000004", "type": "Feature",
  "feature_type": "unit",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0008],[105.9514,21.0008],[105.9514,21.0012],[105.9503,21.0012],[105.9503,21.0008]]] },
  "properties": { "category": "walkway",
                  "name": { "vi": "Sảnh trung tâm" },
                  "level_id": "30000000-0000-4000-8000-000000000002" } }
```
Còn lại: `...0002` (room, Cửa hàng thời trang A), `...0003` (restroom), `...0005` (escalator, 1F), `...0006` (elevator), `...0007` (foodservice, 2F), `...0008` (escalator, 2F). Hai unit `...0007` và `...0008` có `level_id` = `...0003` (tầng 2F).

**opening.geojson**: cửa là một **đoạn thẳng** nằm trên ranh giới giữa hai không gian. In cửa vào siêu thị:
```json
{ "id": "50000000-0000-4000-8000-000000000002", "type": "Feature",
  "feature_type": "opening",
  "geometry": { "type": "LineString", "coordinates": [[105.9508,21.0008],[105.9510,21.0008]] },
  "properties": { "category": "pedestrian",
                  "door": { "type": "sliding", "automatic": true },
                  "level_id": "30000000-0000-4000-8000-000000000002" } }
```
Hai cửa còn lại: `...0001` (cửa chính tòa nhà, nối bên ngoài với siêu thị) và `...0003` (cửa vào cửa hàng thời trang A).

**amenity.geojson**: cây ATM nằm trong sảnh.
```json
{ "id": "90000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "amenity",
  "geometry": { "type": "Point", "coordinates": [105.9512,21.0010] },
  "properties": { "category": "atm", "name": { "vi": "ATM" },
                  "unit_ids": ["40000000-0000-4000-8000-000000000004"] } }
```

**anchor.geojson**: điểm neo (vị trí gắn tên cửa hàng) nằm trong unit siêu thị.
```json
{ "id": "70000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "anchor",
  "geometry": { "type": "Point", "coordinates": [105.9510,21.0005] },
  "properties": { "unit_id": "40000000-0000-4000-8000-000000000001" } }
```

**occupant.geojson**: đơn vị thuê, trỏ tới điểm neo.
```json
{ "id": "80000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "occupant", "geometry": null,
  "properties": { "category": "supermarket",
                  "name": { "vi": "Siêu thị" },
                  "anchor_id": "70000000-0000-4000-8000-000000000001" } }
```

**relationship.geojson**: nối thang cuốn tầng 1 với thang cuốn tầng 2. Hai unit `escalator` (mỗi tầng một cái) được nối bằng một feature `relationship`:
```json
{ "id": "95000000-0000-4000-8000-000000000001", "type": "Feature",
  "feature_type": "relationship", "geometry": null,
  "properties": { "category": "escalator", "direction": "directed", "hours": null,
                  "origin":      { "id": "40000000-0000-4000-8000-000000000005", "feature_type": "unit" },
                  "intermediary": null,
                  "destination": { "id": "40000000-0000-4000-8000-000000000008", "feature_type": "unit" } } }
```

### f) Cách đọc: lần theo chuỗi id từ "Siêu thị" ra ngoài

```
occupant 80..01 "Siêu thị"
   │ anchor_id
   ▼
anchor 70..01
   │ unit_id
   ▼
unit 40..01 (room)
   │ level_id
   ▼
level 30..02 "Tầng 1" (ordinal 0)
   │ building_ids
   ▼
building 20..01 "Tòa chính"
   │ address_id
   ▼
address 60..01 "1 Đường Mock"
```

Nhận xét:
- Hình học nằm **ngay trong feature**; quan hệ nằm ở các trường `*_id`.
- Muốn biết "Siêu thị ở tầng nào" phải đi theo chuỗi id, giống tra khóa ngoại trong cơ sở dữ liệu.
- Một vài chi tiết (như `geometry` của `anchor`, quan hệ `venue` ↔ `building`) trong ví dụ này là suy đoán, cần đối chiếu đặc tả.

---

## LT2.1 — IMDF là gì (lát cắt: nhìn từ bên ngoài)

**[concept]**
- IMDF là một định dạng dữ liệu bản đồ **trong nhà** (tòa nhà, trung tâm thương mại, sân bay...), do **Apple** tạo ra. Năm 2021, OGC duyệt nó làm **OGC Community Standard** (duyệt 2021-02-02, xuất bản 2021-02-18, phiên bản 1.0.0). Community Standard nghĩa là tiêu chuẩn phát triển ngoài quy trình của OGC rồi được hội viên OGC chứng thực; bản OGC được giữ cố định, còn bản mới do Apple tiếp tục cập nhật.
- Dữ liệu viết bằng **GeoJSON** (RFC 7946): mỗi đối tượng là một feature có hình học và thuộc tính.
- Một gói IMDF mô tả đúng **một venue** và gồm tối đa **16 loại feature**.
- Mục đích: để ứng dụng bản đồ hiển thị phòng, tầng, lối đi và dẫn đường trong nhà một cách thống nhất.
- Khác OSM: OSM là cơ sở dữ liệu mở, tag tự do, đối tượng nối nhau qua node/way/relation. IMDF là **đặc tả chặt**: danh sách loại feature và trường cố định, đối tượng nối nhau qua `id`.

**[example:imagination]**
Đứng trước cổng AEON Mall (mock), bạn thấy **tấm bảng chỉ dẫn tổng thể**: tên khu, địa chỉ, sơ đồ tòa nhà nhìn từ trên xuống. IMDF trước hết là dữ liệu cho tấm bảng đó: *khu này tên gì, ở đâu, tòa nhà nằm chỗ nào*, rồi mới đến chi tiết từng phòng.

Còn OSM giống một cuốn **sổ tay ghi chú tự do** ai cũng thêm được; IMDF giống một **biểu mẫu in sẵn**, từng ô có tên cố định.

**[example:data]**
Lát cắt "bên ngoài" của AEON Mall (mock), chỉ gồm ba file: `venue`, `footprint`, `address` (các file khác chưa cần):

```json
// venue.geojson : cả khu đất
{ "id": "10000000-0000-4000-8000-000000000001", "feature_type": "venue",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9500,21.0000],[105.9520,21.0000],[105.9520,21.0020],[105.9500,21.0020],[105.9500,21.0000]]] },
  "properties": { "category": "shoppingcenter",
                  "name": { "vi": "AEON Mall Mock" },
                  "display_point": { "type": "Point", "coordinates": [105.9510, 21.0010] },
                  "address_id": "60000000-0000-4000-8000-000000000001" } }

// footprint.geojson : dấu chân tòa chính, NHỎ HƠN venue
{ "id": "21000000-0000-4000-8000-000000000001", "feature_type": "footprint",
  "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0003],[105.9517,21.0003],[105.9517,21.0017],[105.9503,21.0017],[105.9503,21.0003]]] },
  "properties": { "category": "ground",
                  "building_ids": ["20000000-0000-4000-8000-000000000001"] } }

// address.geojson : địa chỉ cổng chính
{ "id": "60000000-0000-4000-8000-000000000001", "feature_type": "address", "geometry": null,
  "properties": { "address": "1 Đường Mock", "locality": "Hà Nội", "country": "VN" } }
```

Phân tích:
- `venue` là vùng lớn (có cả bãi xe, vườn); `footprint` chỉ là phần tòa nhà. Hình học của `footprint` nằm **trong** hình học của `venue`.
- `venue` không chứa danh sách tòa nhà; nó chỉ trỏ tới địa chỉ qua `address_id`. Tòa nhà gắn vào footprint qua `building_ids`.
- `address` không có hình học (`geometry: null`), chỉ là thông tin chữ.

**[example:In-Out process]**
```
Vào : venue + footprint + address của AEON Mall (mock)
  1. App đọc venue → tên "AEON Mall Mock", loại shoppingcenter, vẽ viền khu
  2. App đọc footprint → vẽ hình tòa nhà bên trong viền
  3. App đọc address qua address_id → hiện "1 Đường Mock, Hà Nội"
Ra  : thẻ thông tin của địa điểm trên bản đồ (chưa có phòng nào)
```

**[common-misconception]** (chưa có mục nào)

---

## LT2.2 — Định dạng lưu trữ (lát cắt: một file `unit.geojson`)

**[concept]**
Một bộ IMDF là một gói nén **`.zip`** gồm:
- `manifest.json` (**bắt buộc**): thông tin chung. Bắt buộc có `version` (hiện chỉ nhận `"1.0.0"`), `created` (ngày giờ tạo gói) và `language` (ngôn ngữ mặc định, ví dụ `"vi"`); tùy chọn `generated_by`, `extensions`.
- Mỗi **loại đối tượng** (*feature type*) có **một file** `.geojson` riêng, là một `FeatureCollection` chỉ chứa feature cùng loại: `venue.geojson`, `building.geojson`, `level.geojson`, `unit.geojson`, `opening.geojson`...
- Chỉ **`manifest.json`, `address.geojson` và `venue.geojson` là bắt buộc**. Các file còn lại (`building`, `footprint`, `level`, `unit`, `opening`, `amenity`, `anchor`, `occupant`, `relationship`, `fixture`, `detail`, `kiosk`, `section`, `geofence`) là tùy chọn.
- `venue.geojson` chỉ chứa **đúng một** venue.

Hai cấp cần phân biệt:

| Cấp | Gọi là | Ví dụ |
|-----|--------|-------|
| Loại đối tượng | *feature type* (giá trị của trường `feature_type`) | `unit` (phòng), `level` (tầng) |
| Một đối tượng cụ thể | *feature* (một phần tử trong mảng `features` của file) | "Siêu thị", "Tầng 1" |

Một file `unit.geojson` chứa nhiều feature, tất cả cùng feature type `unit`.

**Mỗi feature (mỗi đối tượng cụ thể)** có 5 trường chung:

| Trường | Ý nghĩa |
|--------|---------|
| `id` | UUID phiên bản 4, định danh duy nhất của đối tượng này |
| `type` | Luôn là `"Feature"` (theo chuẩn GeoJSON, không liên quan loại phòng/tầng) |
| `feature_type` | Loại của đối tượng: `venue`, `level`, `unit`... (trùng với tên file chứa nó) |
| `geometry` | Hình học (điểm, đường, đa giác) |
| `properties` | Các trường riêng, khác nhau tùy feature type (ví dụ `unit` có `category`, `level_id`) |

Cần phân biệt `type` (cố định, của GeoJSON) với `feature_type` (thay đổi, của IMDF).

**[example:imagination]**
Gói IMDF là **một tủ hồ sơ**. Mỗi **ngăn kéo** là một file theo loại: ngăn "unit", ngăn "level", ngăn "opening". Mỗi **tờ hồ sơ** trong ngăn là một feature. Mọi tờ đều có cùng ô ở đầu (số hồ sơ `id`, loại `feature_type`), còn phần nội dung bên dưới (`properties`) tùy loại.

**[example:data]**
Lát cắt: **mở riêng ngăn `unit.geojson`** của AEON Mall (mock), chỉ xem hai tờ (Siêu thị và Sảnh) trong tổng số 7.

```json
{ "type": "FeatureCollection",                       // bọc ngoài cả file (chuẩn GeoJSON)
  "features": [                                      // mảng chứa 8 feature, đây là 2 trong số đó
    { "id": "40000000-0000-4000-8000-000000000001",  // tờ 1: Siêu thị
      "type": "Feature",
      "feature_type": "unit",
      "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0003],[105.9517,21.0003],[105.9517,21.0008],[105.9503,21.0008],[105.9503,21.0003]]] },
      "properties": { "category": "room",
                      "name": { "vi": "Siêu thị" },
                      "level_id": "30000000-0000-4000-8000-000000000002" } },

    { "id": "40000000-0000-4000-8000-000000000004",  // tờ 2: Sảnh trung tâm
      "type": "Feature",
      "feature_type": "unit",
      "geometry": { "type": "Polygon", "coordinates": [[[105.9503,21.0008],[105.9514,21.0008],[105.9514,21.0012],[105.9503,21.0012],[105.9503,21.0008]]] },
      "properties": { "category": "walkway",
                      "name": { "vi": "Sảnh trung tâm" },
                      "level_id": "30000000-0000-4000-8000-000000000002" } } ] }
```

Phân tích:
- Hai tờ khác nhau ở `id`, `geometry`, `category`, `name`; giống nhau ở `type`, `feature_type` và `level_id` (cùng tầng 1).
- Tọa độ nằm ngay trong feature. Trong OSM, way chỉ chứa danh sách node id và phải tra tọa độ ở nơi khác (LT1.1).
- Chỉ có `level_id` là chỗ nối ra ngoài file; quan hệ giữa các file xem LT2.4.

**[example:In-Out process]**
```
Vào : aeon_mock.zip
  1. Giải nén → manifest.json + 11 file *.geojson
  2. Mở unit.geojson → mảng features (8 phần tử)
  3. Với mỗi feature: đọc id, geometry, properties
Ra  : bảng 8 dòng  id | category | name | level_id
        ...0001 | room    | Siêu thị       | ...0002
        ...0004 | walkway | Sảnh trung tâm | ...0002
        (và 6 dòng còn lại)
```

**[common-misconception]** (chưa có mục nào)

---

## LT2.3 — Các loại feature và quan hệ phân cấp (lát cắt: đi dạo một vòng trong mall)

**[concept]**
Các loại feature chính (tên theo hiểu biết hiện tại):

| Loại | Ý nghĩa |
|------|---------|
| `venue` | Địa điểm lớn (khu mua sắm, sân bay). Có hình học là đa giác bao **mọi feature khác** (xem bên dưới); mỗi gói có đúng một venue |
| `building` | Một tòa nhà. **Không có hình học** (`geometry: null`); hình dạng nằm ở `footprint` |
| `footprint` | Hình chiếu mặt bằng của tòa nhà |
| `level` | Một tầng |
| `unit` | Một không gian trên một tầng (phòng, hành lang, thang máy, cầu thang), do vật cản (tường), ranh giới vật lý hoặc ranh giới pháp lý xác định |
| `opening` | Lối vào (cửa, cổng, ngưỡng); hình học là đoạn thẳng, rộng bằng chiều rộng lối vào |
| `amenity` | Tiện ích (nhà vệ sinh, ATM) |
| `occupant` | Đơn vị chiếm dụng (cửa hàng, văn phòng) |
| `anchor` | Điểm neo (Point), nơi đặt tên cửa hàng hoặc địa chỉ; nằm trong một unit |
| `address` | Địa chỉ bưu chính (không có hình học) |
| `relationship` | Quan hệ giữa hai feature, có thể kèm feature trung gian (ví dụ nối thang máy giữa các tầng, cửa một chiều) |
| `fixture`, `detail`, `section`, `kiosk`, `geofence` | Đồ cố định / vật cản, chi tiết hình học, vùng con, quầy, vùng rào |

Hai loại quan hệ khác nhau (xem thêm LT2.4):

```
1) Chứa theo HÌNH HỌC:   venue  ⊃  mọi feature khác (nằm trong đa giác của venue)

2) Tham chiếu bằng ID (feature con trỏ lên feature cha):
   footprint ──building_ids──► building
   level     ──building_ids──► building
   unit      ──level_id──────► level
   opening   ──level_id──────► level
   anchor    ──unit_id───────► unit
   amenity   ──unit_ids──────► unit
   occupant  ──anchor_id─────► anchor
   venue / building / level ──address_id──► address
```

Không có trường `venue_id`: building thuộc venue vì **nằm trong** đa giác của venue.

**[example:imagination]**
Bạn đi dạo một vòng AEON Mall (mock) và hỏi mỗi thứ nhìn thấy là loại feature nào:
- Cả khu có bãi xe, vườn → `venue`.
- Tòa nhà chính → `building`; bóng của nó trên mặt đất → `footprint`.
- Tầng 1 → `level`.
- Gian siêu thị, sảnh, nhà vệ sinh, thang cuốn → `unit`.
- Cánh cửa tự động vào siêu thị → `opening`.
- Cây ATM ở sảnh → `amenity`.
- Biển hiệu "Siêu thị" (tên người thuê gian đó) → `occupant`.

**[example:data]**
Cùng vòng đi dạo, nhìn dưới dạng dữ liệu:

| Thấy gì | feature type | File | `category` (nếu có) | id trong ví dụ |
|---------|--------------|------|---------------------|----------------|
| Cả khu | `venue` | `venue.geojson` | `shoppingcenter` | `10..01` |
| Tòa chính | `building` | `building.geojson` | | `20..01` |
| Dấu chân tòa nhà | `footprint` | `footprint.geojson` | `ground` | `21..01` |
| Tầng 1 | `level` | `level.geojson` | | `30..02` |
| Gian siêu thị | `unit` | `unit.geojson` | `room` | `40..01` |
| Sảnh | `unit` | `unit.geojson` | `walkway` | `40..04` |
| Thang cuốn | `unit` | `unit.geojson` | `escalator` | `40..05` |
| Cửa tự động vào siêu thị | `opening` | `opening.geojson` | `pedestrian` | `50..02` |
| Cây ATM | `amenity` | `amenity.geojson` | `atm` | `90..01` |
| Tên người thuê "Siêu thị" | `occupant` | `occupant.geojson` | `supermarket` | `80..01` |

Phân tích ba cặp dễ nhầm:
- **`building` và `footprint`:** building là *thông tin* về tòa nhà (tên, địa chỉ); footprint là *hình dạng trên mặt đất*. Hai feature riêng, nối bằng `footprint.building_ids`.
- **`level` và `unit`:** level là một tầng nói chung; unit là một không gian cụ thể trên tầng đó. Siêu thị là unit, "Tầng 1" là level.
- **`unit` và `occupant`:** unit là *chỗ* (không gian vật lý, còn đó dù cửa hàng dọn đi); occupant là *ai đang ở chỗ đó*.

**[common-misconception]** (chưa có mục nào)

---

## LT2.4 — Tham chiếu giữa các feature (lát cắt: lần theo id của "Siêu thị")

**[concept]**
IMDF nối feature bằng trường `*_id` hoặc `*_ids` chứa UUID của feature khác (ví dụ `unit.level_id`, `level.building_ids`). Hình học tự chứa trong feature; không có khái niệm "dùng chung node".

So với OSM:
- OSM: kết nối (nối đường, vùng) thể hiện bằng **dùng chung node**.
- IMDF: quan hệ (thuộc tầng nào, thuộc tòa nào) thể hiện bằng **id tham chiếu**; kết nối đi lại giữa các phòng suy từ `opening` và hình học.

**[example:imagination]**
Mỗi feature là **một người có số căn cước**. Hồ sơ của "Siêu thị" ghi: *"tôi thuộc tầng có căn cước ...0002"*. Muốn biết tầng đó là gì phải mang số ra phòng hồ sơ khác để tra. Giống tra khóa ngoại trong cơ sở dữ liệu.

**[example:data]**
Lát cắt: **đúng một sợi dây** từ tên cửa hàng ra tới địa chỉ. Chỉ in trường tham chiếu, bỏ các trường khác:

```json
// occupant "Siêu thị"
{ "id": "80..01", "feature_type": "occupant", "properties": { "name": {"vi":"Siêu thị"}, "anchor_id": "70..01" } }
// anchor (điểm neo) - nằm trong unit nào?
{ "id": "70..01", "feature_type": "anchor",   "properties": { "unit_id": "40..01" } }
// unit "Siêu thị" - ở tầng nào?
{ "id": "40..01", "feature_type": "unit",     "properties": { "level_id": "30..02" } }
// level "Tầng 1" - thuộc tòa nào?
{ "id": "30..02", "feature_type": "level",    "properties": { "building_ids": ["20..01"] } }
// building "Tòa chính" - địa chỉ nào?
{ "id": "20..01", "feature_type": "building", "properties": { "address_id": "60..01" } }
```

(`..` là cách viết tắt của phần giữa UUID trong ví dụ, để dễ đọc.)

Phân tích:
- Mỗi mũi tên là một trường chứa UUID; đọc 5 lần là từ "Siêu thị" ra tới địa chỉ.
- Dây có thể **đọc ngược**: muốn liệt kê mọi phòng của tầng 1 thì lọc `unit` có `level_id == 30..02`.
- `building_ids` là một **mảng**, nên về nguyên tắc một tầng có thể trỏ tới nhiều tòa nhà (cần kiểm tra đặc tả).

**[example:In-Out process]**
```
Câu hỏi: "Siêu thị ở tầng nào của tòa nào?"
Vào : id của occupant "Siêu thị" = 80..01
  1. occupant 80..01 → anchor_id = 70..01
  2. anchor   70..01 → unit_id   = 40..01
  3. unit     40..01 → level_id  = 30..02
  4. level    30..02 → name "Tầng 1", building_ids = [20..01]
  5. building 20..01 → name "Tòa chính"
Ra  : "Siêu thị, Tầng 1, Tòa chính"
```

**[common-misconception]** (chưa có mục nào)

---

## LT2.5 — Tầng, phòng, cửa, đường đi trong nhà (lát cắt: hành trình của một khách)

**[concept]**
- Tầng: feature `level` có số thứ tự `ordinal` (0 mặt đất, 1, 2...; âm cho tầng hầm) và cờ `outdoor`.
- Phòng: feature `unit`, thuộc một `level`, có `category` (room, restroom, walkway, elevator, stairs...).
- Cửa: feature `opening` có hình học dạng đường, đặt giữa các unit, có thông tin cửa (loại, tự động hay không).
- Nối tầng (thang máy, thang cuốn, cầu thang): mỗi tầng có một `unit` riêng (`category` là `elevator`, `escalator`, `stairs`...). Các unit này được nối bằng feature **`relationship`**, có `origin`, `destination` và tùy chọn `intermediary`, mỗi cái là một tham chiếu `{ "id": ..., "feature_type": ... }`. Đặc tả khuyên dùng `relationship` cho đường đi qua unit có khả năng đi dọc, nối các unit `elevator` ở các tầng khác nhau, và cho cửa một chiều (qua `opening` với `direction: directed`).
- Đường đi: không có một lớp "đường" riêng; suy ra từ các unit, opening và relationship. Một `relationship` còn có thể mang hình học đường thẳng nếu muốn mô tả một tuyến cụ thể.
- Thuộc tính cửa: `opening.door` gồm `type` (ví dụ `sliding`, `swinging`, `revolving`, `open`...), `automatic` (true/false) và `material`.

**[example:imagination]**
Một khách vào AEON Mall (mock): qua cửa chính vào siêu thị, đi qua cửa tự động sang sảnh, rút tiền ở ATM, đi thang cuốn lên tầng 2, đến khu ăn uống. Mỗi bước đi qua một **không gian** (unit) và một **cánh cửa** (opening).

**[example:data]**
Lát cắt: **những feature mà khách này chạm vào**, chỉ in các trường liên quan đến đi lại.

| Bước | Feature | Trường quan trọng |
|------|---------|--------------------|
| Vào cổng | opening `50..01` | cửa chính tòa nhà |
| Trong siêu thị | unit `40..01` | `category: room`, `level_id: 30..02` |
| Qua cửa tự động | opening `50..02` | `LineString`, `door.automatic: true` |
| Sảnh | unit `40..04` | `category: walkway` |
| ATM | amenity `90..01` | `unit_ids: [40..04]` |
| Thang cuốn tầng 1 | unit `40..05` | `category: escalator`, `level_id: 30..02` |
| Lên tầng 2 | relationship `95..01` | `category: escalator`, `origin: 40..05`, `destination: 40..08` |
| Thang cuốn tầng 2 | unit `40..08` | `category: escalator`, `level_id: 30..03` |
| Khu ăn uống | unit `40..07` | `category: foodservice`, `level_id: 30..03` |

Ba tầng của tòa chính:

| Tầng | `level` id | `ordinal` | `outdoor` |
|------|------------|-----------|-----------|
| B1 | `30..01` | -1 | false |
| 1F | `30..02` | 0 | false |
| 2F | `30..03` | 1 | false |

Phân tích:
- `ordinal` chỉ là thứ tự: -1 < 0 < 1. Tên hiển thị ("1F", "Tầng 1") lưu riêng trong `name`.
- Siêu thị và sảnh cùng `level_id` (`30..02`); khu ăn uống khác (`30..03`). Đó là cách biết khách đã lên tầng.
- Cửa `50..02` là đoạn thẳng nằm trên ranh giới giữa siêu thị và sảnh.
- Thang cuốn nối hai tầng bằng **hai unit** (`40..05` ở 1F, `40..08` ở 2F) và **một relationship** (`95..01`); không có unit nào trải qua hai tầng.

**[example:In-Out process]**
```
Vào : điểm A = cửa chính (opening 50..01), điểm B = khu ăn uống (unit 40..07)
  1. A → unit 40..01 (siêu thị), tầng 1
  2. qua opening 50..02 → unit 40..04 (sảnh), tầng 1
  3. đến unit 40..05 (thang cuốn), tầng 1
  4. relationship 95..01 (origin 40..05 → destination 40..08): sang tầng 2
  5. từ unit 40..08 (thang cuốn, tầng 2) → unit 40..07 (khu ăn uống)
Ra  : đường đi gồm chuỗi  unit → opening → unit → ... , mỗi bước biết tầng
```

**[common-misconception]** (chưa có mục nào)

---

### Nguồn tham khảo LT2

Các trang đã tải về và đối chiếu ngày 2026-11-05 (bản IMDF 1.0.0).

- Đặc tả IMDF (OGC Community Standard): https://docs.ogc.org/cs/20-094/
  - Reference (gói, kiểu dữ liệu): https://docs.ogc.org/cs/20-094/Reference/index.html
  - Manifest, Venue, Building, Footprint, Level, Unit, Opening, Amenity, Anchor, Occupant, Address, Relationship: `https://docs.ogc.org/cs/20-094/<Tên>/index.html`
  - Categories (danh sách giá trị `category`): https://docs.ogc.org/cs/20-094/Categories/index.html
  - Hướng dẫn Shopping Center: https://docs.ogc.org/cs/20-094/Shopping_Center/index.html
- Apple (nguồn của các bản IMDF mới hơn): https://register.apple.com/resources/imdf/

---

# LT3 — Quy ước tag và dữ liệu OCP1

Tương ứng mục LT3 trong `task.md`. LT3 chỉ bổ sung quy ước của OSM Wiki và số liệu thật của khu OCP1. Hai nhãn dùng thêm ở LT3: `[values]` (giá trị thường gặp, đếm trên OCP1) và `[handling]` (lưu ý khi xử lý bằng code).

**Nguồn số liệu**
- Dữ liệu: `data/ocp1.osm.pbf` = bản cắt từ Geofabrik Việt Nam (`vietnam-261103`, cập nhật 2026-11-04) theo bbox OCP1 `S=20.9840728 W=105.9334479 N=21.0047847 E=105.9628773`. Gồm **31.117 node, 3.951 way, 89 relation**. Way chạm bbox được giữ nguyên nên có node nằm ngoài bbox.
- Số liệu tag: notebook `ocp1_osm_analysis.ipynb`, phần 6 (kết quả `output/nb/tag_values.csv`); script tương đương `scripts/tag_stats.py`.
- Định nghĩa: nội dung OSM Wiki tải ngày 2026-11-05; wiki có thể đổi theo thời gian.

## LT3.1 — Elements trong dữ liệu OCP1

**[concept]**
Chỉ phần bổ sung so với LT1.1, LT1.4, LT1.5:
- Một way có từ 1 đến **2.000 node**. Vùng có quá 2.000 node hoặc có lỗ phải dùng multipolygon.
- Relation **bắt buộc có tag `type`**; các tag còn lại hiểu theo `type`. Một phần tử có thể xuất hiện nhiều lần làm member tùy loại relation.
- Node và way có thể không có tag (khi chỉ là thành phần của way hoặc relation); relation thì phải có.
- Trên trang mô tả tag, multipolygon được coi là *vùng*, không phải relation, vì cùng một tag dùng cho closed way và cho multipolygon. Vì vậy trang Key:building ghi "không dùng trên relation" nhưng OCP1 vẫn có `building` trên multipolygon (LT3.2).

**[values]**

| Loại | Số lượng | Có tag | Ghi chú |
|------|----------|--------|---------|
| Node | 31.117 | 4.472 (14,4%) | phần còn lại chỉ là điểm hình học của way |
| Way | 3.951 | 3.914 | 2.102 closed way (53%); 1.371 way có `building`, tất cả đều khép kín; 27 way có `area=yes` |
| Relation | 89 | 89 | `route` 48, `boundary` 18, `multipolygon` 14, `restriction` 9 |

Multipolygon: 14 relation, tổng member: `outer` 19, `inner` 42, đều là way. Chỉ **2 trong 14** có `building`. Mười hai cái còn lại: `leisure=track`, `natural=sand`, `amenity=school`, 5 relation `highway=pedestrian`/`footway` (4 cái có `area=yes`), `landuse=grass`, `landuse=forest`, `natural=water`, `landuse=residential`.

**[example:data]**
Cùng khu trường học có **hai relation** khác nhau về nội dung:
```json
// relation 16676566 : mô tả TÒA NHÀ (xem cấu trúc đầy đủ ở LT1.5)
{ "type": "multipolygon", "building": "school" }

// relation 16676567 : mô tả MỤC ĐÍCH SỬ DỤNG
{ "type": "multipolygon", "amenity": "school", "education": "school",
  "name": "Brighton College Vietnam", "grades": "1-12",
  "addr:subdistrict": "Đa Tốn", "website": "https://brightoncollege.edu.vn" }
```
Tòa nhà (`building=school`) và cơ sở giáo dục (`amenity=school`) là hai đối tượng riêng, vì wiki nói `building` chỉ loại kiến trúc, không phải mục đích dùng.

**[handling]**
- Lọc relation theo `type` trước khi làm gì khác (script 2.3).
- Member của relation có thể trỏ tới phần tử nằm ngoài file (way bị cắt biên); không giả định mọi `ref` đều có mặt.
- Muốn tìm "tòa nhà" phải xét cả way và relation (script 2.5).

**[common-misconception]** (chưa có mục nào)

---

## LT3.2 — Key:building

**[concept]**
- Đánh dấu một đối tượng là tòa nhà: công trình nhân tạo có mái, đứng yên tương đối lâu dài.
- `building=yes` là tối thiểu; giá trị khác phân loại **kiểu kiến trúc**, không nhất thiết trùng mục đích hiện tại (mục đích dùng `building:use`, hoặc `amenity=*`). Ví dụ bệnh viện bỏ hoang vẫn là `building=hospital`.
- Vẽ bằng closed way hoặc multipolygon; vẽ bằng node chỉ được chấp nhận tạm khi chưa có hình dạng.
- Wiki xem `building=no` và `building=maybe` là lỗi; trong OCP1 không gặp.

**[values]**
- 1.371 way + 2 relation có `building`, **16 giá trị**: `yes` 604, `house` 501, `terrace` 140, `apartments` 46, `industrial` 20, `university` 17, `school` 12, `construction` 11, `commercial` 6, `temple` 5, `roof` 3, `dormitory` 3, `kindergarten` 2.

**[example:data]**
```json
// way 530485741 : giảng đường, building=yes cùng nhiều tag mô tả
{ "building": "yes", "building:levels": "2", "name": "Giảng đường C",
  "building:colour": "yellow", "roof:shape": "gabled", "roof:material": "roof_tiles",
  "roof:height": "0.14", "ele": "9", "operator": "Học viện Nông nghiệp Việt Nam",
  "addr:district": "Gia Lâm", "addr:subdistrict": "Trâu Quỳ" }
```

**[handling]**
- `building=yes` chiếm khoảng 44%, nên nhóm theo loại phải chấp nhận nhiều tòa không rõ kiểu.
- `building=roof` (3 cái, ví dụ "Bãi gửi xe sau B4") là mái che, không phải nhà đầy đủ.

---

## LT3.3 — Key:highway

**[concept]**
- Khóa chính cho mọi loại đường và các tiện ích gắn với đường (trạm xe buýt, vạch qua đường, đèn giao thông).
- Giá trị thể hiện **vai trò và tầm quan trọng** trong mạng đường, từ `motorway` (quan trọng nhất) đến `service`. Nó **không** phản ánh chất lượng mặt đường, trừ `motorway` và `motorway_link`; chất lượng ghi bằng `surface`, `tracktype`...
- Dùng được trên node, way, vùng; không dùng trực tiếp trên relation (multipolygon được tính là vùng, xem LT3.1).

**[values]**
- Node 879; way **1.960**; relation 5 (các multipolygon `highway=pedestrian`/`footway`). **24 giá trị** khác nhau.
- Way: `footway` 1.144, `service` 323, `residential` 270, `tertiary` 74, `secondary` 58, `pedestrian` 21, `motorway` 14, `primary` 13, `secondary_link` 12, `construction` 9, `motorway_link` 5, `tertiary_link` 5.
- Node: `crossing` 802, `bus_stop` 47, `turning_circle` 24, `traffic_signals` 3, `mini_roundabout` 2, `motorway_junction` 1.

**[example:data]**
Cùng khóa `highway` nhưng ý nghĩa khác nhau tùy loại phần tử (giao lộ giữa các way highway xem LT1.2):
```json
// way 50535542 : ĐƯỜNG (111 node)
{ "highway": "tertiary", "name": "Đường Trâu Quỳ", "oneway": "no", "sidewalk": "both",
  "surface": "asphalt", "source": "survey" }
// node 4258046064 : vạch qua đường, một điểm
{ "highway": "crossing" }
// node 481836768 : trạm xe buýt
{ "highway": "bus_stop", "bus": "yes", "name": "Cổng Ga Phú Thị", "public_transport": "platform" }
```

**[handling]**
- Lọc "là đường" phải xét loại phần tử: `highway` trên node thường là tiện ích, không phải đường. Script 2.2 chỉ xét **way**.
- Kết quả phần 2.2: 1.960 way highway chứa 11.666 node khác nhau; **3.621 node** dùng chung từ 2 way highway trở lên, nhiều nhất 6 way trên một node.
- `footway` chiếm hơn một nửa số way highway; lối đi bộ cũng là `highway`.

**[common-misconception]** (chưa có mục nào)

---

## LT3.4 — Key:layer

**[concept]**
Khái niệm `layer` với `bridge` / `tunnel` xem LT1.3. Chỉ bổ sung quy tắc của wiki:
- Giá trị thông dụng từ **-5 đến 5**; không ghi `layer=0` tường minh; không cần dấu `+` (viết `1`, không viết `+1`).
- Thứ tự chỉ đúng **tại chỗ hai đối tượng giao nhau**; không dùng để mô tả quan hệ giữa đối tượng ở xa hoặc kề nhau. Gán `layer` cho way dài có thể làm hỏng các giao lộ ở xa.
- Dùng giá trị nhỏ nhất đủ dùng: `layer=2` chỉ khi cầu vượt qua đối tượng đã ở `layer=1`.
- Chỉ gắn `layer` cho way có `bridge` / `tunnel` / `highway=steps` / `highway=elevator` / `covered`. Rãnh, đê, đoạn đường đào dùng `embankment` / `cutting`, không dùng `layer`.
- Giá trị âm **không** có nghĩa dưới lòng đất (dùng `location=underground`); `layer` cũng không cho biết độ cao thực.
- Tầng trong tòa nhà dùng `level`, không dùng `layer` (xem LT3.7).
- Nên ghi tường minh `layer` cho mọi cầu và hầm, dù một số phần mềm mặc định cầu là +1 và hầm là -1.

**[values]**
- 36 way có `layer`, chỉ **3 giá trị**: `1` (18), `-1` (12), `2` (6).
- Theo tag đi kèm: `bridge` 19, `tunnel` 5 (2 cái `yes`, 3 cái `culvert`); **12 way có `layer` mà không có `bridge`/`tunnel`**.

| Nhóm | Số way | Ví dụ |
|------|--------|-------|
| `bridge` + `layer=1` | 14 | `service` 6, `residential` 2, `footway` 2, `motorway` 2, `proposed` 2 |
| `bridge` + `layer=2` | 5 | `motorway` 4, `motorway_link` 1 |
| `tunnel` + `layer=-1` | 5 | `secondary_link` 2, ống cống (`culvert`) 3 |
| `layer=-1`, không `bridge`/`tunnel` | 7 | `highway=footway` |
| `layer=1`, `layer=2`, không `bridge`/`tunnel` | 5 | nhà để xe, mái che, cầu `man_made=bridge` |

**[example:data]**
```json
// way 761986897 : cầu B1-05 trên đường cao tốc, layer 2
{ "bridge": "yes", "layer": "2", "highway": "motorway", "name": "Cầu B1-05",
  "lanes": "3", "maxspeed": "120", "oneway": "yes" }

// way 1223678105 : nhà để xe nhiều tầng, layer 1, KHÔNG có bridge
{ "amenity": "parking", "parking": "multi-storey", "building": "yes",
  "building:levels": "5", "layer": "1", "name": "Ruby Parking Garage" }

// way 1431631668 : cầu, nhưng là vùng man_made=bridge
{ "man_made": "bridge", "layer": "1", "name": "Cầu B1-06" }
```

**[handling]**
- Không suy luận "có `layer` thì là cầu/hầm": chỉ 24 trên 36 way có `bridge` hoặc `tunnel`.
- `layer` có thể nằm trên tòa nhà và vùng (`man_made=bridge`), không chỉ trên đường.
- Giá trị là chuỗi; đọc thành số nguyên khi so sánh (có số âm).
- 6 way `layer=2` (5 đường cầu và 1 mái che) cần xem lại theo nguyên tắc "giá trị nhỏ nhất đủ dùng"; tôi chưa kiểm tra.

---

## LT3.5 — Key:height

**[concept]**
- Chiều cao **thực** theo phương thẳng đứng. Dùng được trên node, way, vùng, relation.
- Đơn vị mặc định là **mét**. Viết `height=4` hoặc `height=4 m` (có dấu cách). Đơn vị khác phải ghi kèm; dấu thập phân là dấu chấm.
- Với tòa nhà: **chiều cao tối đa** (từ điểm thấp nhất chạm đất đến mép trên mái, không tính ăng-ten), không phải trung bình. Chiều cao bao gồm cả mái; `building:levels` thì không.
- Sai thường gặp: `4m` (thiếu dấu cách), `0,8` (dấu phẩy), `11' 4"` (có dấu cách giữa feet và inch).
- Không dùng cho độ cao so với mực nước biển (dùng `ele`) hay giới hạn chiều cao gầm cầu (dùng `maxheight`).

**[values]**
- 31 way có `height`; tất cả là số thuần (không có đơn vị hay dấu phẩy).
- Theo loại: 14 `building`, 13 `building:part=yes`, 4 `barrier=wall`.
- Giá trị nhỏ: `1.5`, `3`, `8`, `12`, `15`, `21`, `25`. Nhóm rất lớn trên `building:part`: `196`, `201`, `206`, `211`, `216`, `226` mét, kèm `building:levels` từ 39 đến 45.

**[example:data]**
```json
// way 589659626 : mái che bãi xe
{ "building": "roof", "height": "3", "name": "Bãi gửi xe sau B4" }
// way 1225581665 : một phần của tòa tháp, cao 216 m với 43 tầng
{ "building:part": "yes", "height": "216", "building:levels": "43" }
```

**[handling]**
- Đọc `height` bằng hàm chuyển số hiểu đơn vị `m` (`parse_number` trong `common.py`); giá trị lạ trả rỗng, không gây lỗi.
- Phải xét cả `building:part`, vì chiều cao tháp nằm ở các phần chứ không ở thân `building`.
- Tháp trên có khoảng **5 m mỗi tầng** (216 / 43), cao hơn mức 3 m mà wiki dùng làm mặc định cho một tầng; khi dùng vào tính toán cần kiểm tra.

---

## LT3.6 — Key:building:levels

**[concept]**
- Số tầng **trên mặt đất**, không tính tầng hầm và tầng mái. Tầng nửa hầm vẫn tính.
- Giá trị phải là **số nguyên dương**; không dùng số lẻ như `1.5` (muốn chiều cao lẻ thì dùng `height`).
- Yêu cầu có `building` hoặc `building:part`. Đi cùng `building:levels:underground` (hầm), `roof:levels` (tầng mái).
- Khi không có `height`, phần mềm dựng 3D thường mặc định 3 m một tầng.
- Khác `level` (LT3.7): `level` là tầng nơi một đối tượng nằm; `building:levels` là tổng số tầng của tòa nhà.

**[values]**
- 117 way có `building:levels`: **85 kèm `building`**, **32 kèm `building:part=yes`** (không có `building`).
- 24 giá trị khác nhau, đều là số nguyên. Phổ biến: `4` (27), `26` (18), `5` (13), `3` (11), `27` (8), `1` (7), `2` (6), `31` (5), `42` (2).

**[example:data]**
```json
// way 530485741 (mục LT3.2): building=yes, building:levels=2
// way 1223678105 (mục LT3.4): nhà để xe Ruby, building:levels=5
```

**[handling]**
- Script 2.5 chọn theo `building`, nên 32 way `building:part` có `building:levels` **không** nằm trong 99 kết quả của phần đó. Muốn thống kê đầy đủ phải xét cả `building:part`.
- Trong 99 building của phần 2.5, không cái nào có cả `building:levels` và `height` (85 có levels, 14 có height). Với `building:part` thì có.
- Đọc bằng `int()`; giá trị như `1;2` (wiki coi là sai) cần xử lý riêng.

**[common-misconception]** (chưa có mục nào)

---

## LT3.7 — Simple Indoor Tagging (chuẩn bị cho phần mở rộng)

**[concept]**
Simple Indoor Tagging (SIT) là bộ quy ước tag để vẽ **bên trong tòa nhà** bằng chính node/way/relation của OSM, không phải một định dạng dữ liệu riêng (khác IMDF ở LT2). Mục tiêu: dẫn đường trong nhà, sơ đồ tầng, bản đồ 3D. Tương thích với Simple 3D Buildings (dùng chung `building:part`, `building:levels`, `height`). Bản chuẩn lập từ 2014, cập nhật đến 2026.

Nguyên tắc: gắn phần tử vào từng tầng bằng tag `level`; vẽ phòng và hành lang như **vùng** (closed way hoặc multipolygon); dùng lại các tag OSM sẵn có. Tường và phòng **dùng chung node** nơi tiếp giáp, cửa là node dùng chung giữa các phòng và tường: đây là quy tắc kết nối của LT1.2 áp dụng trong nhà.

| Nhóm | Tag | Ý nghĩa |
|------|-----|---------|
| Không gian | `indoor=room` | Phòng có tường bao kín |
| | `indoor=area` | Khu vực không bao kín hoàn toàn bằng tường |
| | `indoor=corridor` | Hành lang (loại `area` đặc biệt) |
| | `indoor=wall` | Bức tường riêng, không đi qua được |
| | `indoor=level` | Đường viền một tầng (tùy chọn) |
| Tầng | `level=*` | **Bắt buộc**. Tầng của phần tử: 0 mặt đất, -1 tầng hầm đầu |
| | `level:ref=*` | Số hiệu tầng hiển thị trong nhà (B1, G, 1...) |
| | `min_level`, `max_level`, `non_existent_levels` | Tầng thấp nhất, cao nhất của tòa nhà; tầng không tồn tại (13, 4...) |
| Thuộc tính | `name`, `ref`, `height`, `room=*` | Tên, số phòng, chiều cao, công năng |
| Cửa, cửa sổ | `indoor=door` + `door=*` | Cửa nằm trong tường (node) |
| | `entrance=*` + `door=*` | Cửa ra vào tòa nhà |
| | `window=*` | Cửa sổ (node) |
| Nối tầng | `stairs=yes` + `indoor=room`/`area` | Cầu thang |
| | `highway=elevator` + `indoor=room` | Thang máy |
| | `highway=steps` (+ `conveying=yes`) | Bậc thang, thang cuốn |
| Nhiều tầng | `level=1;2`, `level=0-1` | Đối tượng trải qua nhiều tầng |
| | `repeat_on=1;3` | Một node lặp lại ở các tầng khác (không tính tầng gốc) |

**[values]**
- OCP1 **không có** `indoor=*`, `door=*`, `repeat_on`, `min_level`, `max_level`, `level:ref`.
- Chỉ có `level` trên **6 phần tử** và `entrance` trên 23 node.

| Tag | Số lượng | Nội dung |
|-----|----------|----------|
| `level` | 4 node | `-1` (2 điểm sạc VinFast) và `-1,-2` (2 lối vào bãi xe "The Pavilion Parking") |
| `level` | 2 way | `5` (hai hồ bơi "Ruby Four Season Pool" và "Sapphire Four Season Pool") |
| `entrance` | 23 node | `yes` 22, `main` 1 |

**[example:data]**
```json
// way 1294910436 : hồ bơi, level=5
{ "leisure": "sports_centre", "sport": "swimming", "level": "5",
  "name": "Ruby Four Season Pool", "operator": "Vinhomes Ocean Park" }
// node 11346010702 : cửa chính
{ "entrance": "main" }
```
Hồ bơi dùng `level=5` theo kiểu "POI đơn giản" của chuẩn: gắn tầng lên đối tượng mà chưa vẽ phòng. OCP1 không có `min_level` / `max_level` nên người dùng dữ liệu không có cách nhanh để biết tòa nào có dữ liệu trong nhà.

**[handling]**
- Lọc đối tượng trong nhà bằng `indoor=*` và `level=*`. OCP1 chỉ có `level` lẻ tẻ, nên muốn mở rộng sang SIT phải vẽ thêm.
- `level=-1,-2` trong dữ liệu dùng dấu phẩy, còn chuẩn dùng dấu chấm phẩy (`-1;-2`) hoặc khoảng (`-2--1`). Khi đọc phải chuẩn hóa: tách theo `;` và `,`, rồi mới chuyển số.

**[common-misconception]**
- Hiểu của người học: SIT về cơ bản là OSM được làm giàu thông tin lên với nhiều tag unique hơn.
  Đánh giá: đúng phần lớn.
  Phần sai và giải thích: (1) Không chỉ là tag "unique": SIT cố ý **dùng lại tag có sẵn** cho thứ có cả ngoài trời lẫn trong nhà (`name`, `height`, `ref`, `highway=steps`, `highway=elevator`, `entrance`). Tag mới thực sự chỉ là nhóm nhỏ: `indoor`, `level`, `level:ref`, `repeat_on`, `min_level`/`max_level`. (2) Ngoài tag còn có **quy tắc mô hình hóa**: phòng và hành lang vẽ như vùng; tường và phòng dùng chung node nơi tiếp giáp; cửa là node dùng chung giữa các phòng; đối tượng nhiều tầng ghi `level=1;2`, node lặp lại ở nhiều tầng dùng `repeat_on`.
  Cách nhớ đúng: SIT = OSM + bộ tag trong nhà + quy ước cách vẽ. Cấu trúc dữ liệu vẫn là node/way/relation (khác IMDF ở LT2 có schema riêng). Phần "quy ước cách vẽ" chính là quy tắc kết nối của LT1.2 áp dụng trong nhà.

---

## LT3.8 — Tổng hợp

**[concept]**
Phân biệt các khóa dễ nhầm:

| Khóa | Trả lời câu hỏi | Kiểu giá trị | Phần tử thường gặp | OCP1 (số phần tử) |
|------|-----------------|--------------|--------------------|-------------------|
| `building` | Tòa nhà kiểu gì? | chuỗi (`yes`, `house`...) | closed way, multipolygon | 1.373 (1.371 way + 2 relation) |
| `highway` | Đường hay tiện ích gì? | chuỗi | way, node | 2.844 (1.960 way + 879 node + 5 relation) |
| `layer` | Cái nào nằm trên cái nào tại chỗ giao? | số nguyên (-5..5) | way cầu/hầm, vài vùng | 36 way |
| `height` | Cao bao nhiêu mét? | số (mét) | way, vùng | 31 way |
| `building:levels` | Bao nhiêu tầng trên mặt đất? | số nguyên dương | `building` hoặc `building:part` | 117 way |
| `level` | Phần tử này ở tầng nào? | số hoặc danh sách | phần tử trong nhà | 6 (4 node + 2 way) |

**[example:other]**
Phát hiện chính từ dữ liệu OCP1:
1. Chỉ 14,4% node có tag; 53% way là closed way, trong đó mọi building đều là closed way.
2. 12 trên 14 multipolygon **không** phải tòa nhà.
3. `layer` xuất hiện cả khi không có `bridge`/`tunnel` (12 way): không dùng nó để nhận ra cầu hầm.
4. 32 way `building:part` có `building:levels` nằm ngoài kết quả phần 2.5.
5. Tháp 196–226 m có khoảng 5 m mỗi tầng, cao hơn mức 3 m mặc định.
6. Không có dữ liệu Simple Indoor Tagging đầy đủ; chỉ có `level` lẻ tẻ.

---

### Nguồn tham khảo LT3 (OSM Wiki, tải ngày 2026-11-05)

- Key:building: https://wiki.openstreetmap.org/wiki/Key:building
- Key:highway: https://wiki.openstreetmap.org/wiki/Key:highway
- Key:layer: https://wiki.openstreetmap.org/wiki/Key:layer
- Key:height: https://wiki.openstreetmap.org/wiki/Key:height
- Key:building:levels: https://wiki.openstreetmap.org/wiki/Key:building:levels
- Simple Indoor Tagging: https://wiki.openstreetmap.org/wiki/Simple_Indoor_Tagging
- Các trang Elements, Node, Way, Relation, Relation:multipolygon: xem nguồn LT1

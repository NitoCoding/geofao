# Dokumentasi Alur Sistem Analisis Kesesuaian Lahan

## Daftar Isi
1. [Arsitektur Sistem](#1-arsitektur-sistem)
2. [Alur User](#2-alur-user)
3. [Alur Data](#3-alur-data)
4. [Alur Analisis Detail](#4-alur-analisis-detail)
5. [Model Database](#5-model-database)
6. [API Endpoints](#6-api-endpoints)

---

## 1. Arsitektur Sistem

### Teknologi yang Digunakan
- **Backend**: Django 5.2.5 dengan PostGIS database
- **Spatial**: GeoServer untuk WMS services
- **Frontend**: HTML5, HTMX, jQuery, Bootstrap 5, Leaflet.js
- **Authentication**: Django Auth dengan custom User model
- **API**: Django REST Framework

### Django Apps dan Tanggung Jawab

#### **core** - Autentikasi dan Model Base
```
core/
├── models.py          # Custom User dengan UserProfile
├── views.py           # Login/logout views
└── urls.py            # Authentication URLs
```

#### **master_data** - Manajemen Data Master
```
master_data/
├── models.py
│   ├── CommodityGroup          # Grup: Pangan, Hortikultura, dll
│   ├── Commodity               # Komoditas pertanian
│   ├── DataYear                # Tahun data spasial
│   └── SuitabilityCharacteristic# Kriteria FAO (S1, S2, S3, N)
└── views.py                    # CRUD master data
```

#### **spatial** - Manajemen Data Spasial dan Analisis
```
spatial/
├── models.py
│   ├── MasterLayer              # Layer spasial
│   ├── FeatureData              # Fitur dengan geometri & atribut JSON
│   ├── SuitabilityAnalysisResult# Hasil analisis
│   └── GeoServerPublishing      # Status publish GeoServer
├── utils/
│   ├── suitability_analysis.py  # Core analysis engine
│   ├── limiting_factors.py      # Analisis faktor pembatas
│   ├── geoserver.py             # Integrasi GeoServer
│   └── style_generator.py       # Generate SLD style
└── views.py                     # Layer management views
```

#### **dashboard** - UI Utama
```
dashboard/
├── views.py     # Main routing
└── templates/   # HTML templates
```

#### **analysis** - Modul Analisis (Update)
```
analysis/
├── views.py                    # Halaman analisis
├── suitability_api.py          # API endpoints
└── templates/
    └── analysis/
        └── land_suitability.html # Form analisis + peta
```

---

## 2. Alur User

### 2.1 Login dan Akses Sistem

```
User kunjungi sistem
    ↓
Halaman Login (/accounts/login/)
    ↓
Input username & password
    ↓
Django auth validasi
    ↓
Sukses → UserProfile di-load
    ↓
Set active_data_year & kabupaten di session
    ↓
Dashboard ditampilkan
```

**Detail Autentikasi:**
- Custom User model extends `AbstractUser`
- UserProfile menyimpan preferensi user
- Session untuk menyimpan data year dan kabupaten aktif

### 2.2 Manajemen Layer

#### **Upload Layer Baru**
```
Menu: Layers → Upload
    ↓
Pilih file shapefile/geospatial
    ↓
Upload file
    ↓
Sistem proses file:
    1. Validasi format
    2. Create MasterLayer
    3. Extract features → FeatureData
    4. Store geometri di PostGIS
    5. Store atribut di JSONField
    6. Auto-publish ke GeoServer
    7. Generate SLD style
    ↓
Layer siap digunakan
```

#### **View/Edit Layers**
```
Menu: Layers → List
    ↓
Filter options:
    - By active data year (auto dari session)
    - By kabupaten (session)
    - By category (tanah, komoditas, base_analisis)
    - Search by name
    ↓
Daftar layer ditampilkan:
    - Nama layer
    - Tipe (point/polygon)
    - Jumlah fitur
    - Kategori
    - Status publish
    ↓
Actions:
    - Toggle active/inactive
    - Delete (dengan konfirmasi)
    - View details
    - Download
```

### 2.3 Analisis Kesesuaian Lahan (Step-by-Step)

#### **STEP 1: Pilih Komoditas**
```
Menu: Analysis → Kesesuaian Lahan
    ↓
Form Parameter Analisis
    ↓
Dropdown "Grup Komoditas":
    - Pangan
    - Hortikultura
    - Perkebunan
    - Pakan Ternak
    ↓
Pilih grup → Tampilkan komoditas di grup tersebut
    ↓
Checkbox list komoditas (multi-select):
    ☑ Padi
    ☑ Jagung
    ☐ Kedelai
```

#### **STEP 2: Pilih Layer Spasial**
```
Dropdown "Layer Spasial":
    ↓
List active layers yang tersedia:
    - unit_lahan (1595 fitur)
    - karakteristik_tanah_2024
    - dll
    ↓
Pilih layer yang berisi data tanah
```

#### **STEP 3: Jalankan Analisis**
```
Tombol: "Jalankan Analisis"
    ↓
Frontend kirim request ke API:
    POST /analysis/api/analysis/suitability/batch/
    Body:
    {
        "commodity_ids": [1, 2],
        "layer_id": 15,
        "method": "minimum",
        "include_limiting_factors": true
    }
    ↓
Backend proses (detail di Alur Data)
    ↓
Return hasil agregat
```

#### **STEP 4: View Hasil**
```
Panel Kiri (Commodities):
    - List komoditas yang dianalisis
    - Status badge (Selesai/Pending)
    - Klik untuk menampilkan di peta
    ↓
Panel Kanan (Map):
    - Peta Leaflet dengan poligon berwarna
    - Warna berdasarkan kelas kesesuaian:
        * S1: Hijau tua (Sangat Sesuai)
        * S2: Hijau muda (Cukup Sesuai)
        * S3: Kuning (Sesuai Marginal)
        * N: Merah (Tidak Sesuai)
    - Klik poligon untuk lihat detail
    ↓
Panel Bawah (Results):
    - Statistik ringkas:
        * Total fitur
        * Kelas kesesuaian overall
        * Area total
        * % S1
    - Distribusi kelas (count & percentage)
    - Faktor pembatas
    - Rekomendasi perbaikan
```

#### **STEP 5: Export Hasil**
```
Tombol: "Export Hasil"
    ↓
Pilihan format:
    - PDF Report
    - Excel
    - CSV
    - Image (PNG)
    ↓
Download file
```

### 2.4 Role-Based Access

#### **Regular User**
- ✅ View dan download available layers
- ✅ Perform suitability analysis
- ✅ View analysis history sendiri
- ❌ Upload/manage layers (terbatas)
- ❌ Manage master data

#### **Admin User**
- ✅ Full access semua layers
- ✅ Upload dan manage layers
- ✅ Manage master data (commodities, criteria)
- ✅ View semua analysis history
- ✅ System administration

---

## 3. Alur Data

### 3.1 Upload & Processing Data Spasial

```
Shapefile Upload
    ↓
File Validation (GDAL/OGR)
    ↓
Create MasterLayer Record:
    - name: "unit_lahan"
    - layer_type: "polygon"
    - layer_category: "tanah"
    - table_name: "spatial_featuredata_unit_lahan"
    ↓
Extract Features Loop:
    For each feature in shapefile:
        1. Transform geometri → EPSG:4326
        2. Store geometri di PostGIS (GeometryField)
        3. Store atribut di JSONField
    ↓
FeatureData Records Created:
    feature_id 109:
        geometry: POLYGON(...)
        attributes: {
            "PH_NILAI": 6.0,
            "CORG_NILAI": 1.52,
            "KTK_NILAI": 21.05,
            "TEKSTUR": "sandy loam",
            "DALAM_TNH": "0 - 110",
            "KL": ">45%",
            ...
        }
    ↓
Auto-Publish ke GeoServer:
    1. Create workspace (jika belum ada)
    2. Create PostGIS store
    3. Publish layer
    4. Generate SLD style
    5. Apply style
    ↓
Layer available via WMS
```

### 3.2 Penyimpanan Data Karakteristik Tanah

#### **Raw Format** (dari shapefile/DB)
```json
{
    "KL": ">45%",
    "Suai": "N",
    "UNIT": "APL, Hutan Lahan Kering Sekunder, >45%",
    "K_KRIT": "sedang",
    "N_KRUT": "sedang",
    "P_KRIT": "rendah",
    "BD_KRIT": "rendah",
    "EC_KRIT": "Tidak salin",
    "KS_KRIT": "cepat",
    "K_NILAI": 0.41,
    "N_NILAI": 0.22,
    "PH_KRIT": "Agak Masam Bawah",
    "P_NILAI": 6.26,
    "STASIUN": "Tanete Riaja",
    "TEKSTUR": "sandy loam",
    "BD_NILAI": 0.8,
    "DRAINASE": "sangat cepat",
    "EC_NILAI": 0.16,
    "KS_NILAI": 21.92,
    "KTG_TXTR": "Agak Kasar",
    "KTK_KRIT": "sedang",
    "PH_NILAI": 6.0,
    "VEGETASI": "semak, pohon kayu, mangga",
    "CORG_KRIT": "rendah",
    "DALAM_TNH": "0 - 110",
    "KECAMATAN": "TANETE RIAJA",
    "KTK_NILAI": 21.05,
    "Kdl_tanah": 110,
    "BATUAN_KRI": "Tidak berbatu",
    "BATUAN_NIL": "<3",
    "CH_MAKS_55": 482,
    "CH_MIN_557": 51,
    "CORG_NILAI": 1.52,
    "DALAM_KRIT": "dalam",
    "GUNA_LAHAN": "pertanian lahan kering",
    "TITIK_SAMP": 2
}
```

#### **Normalized Format** (untuk analisis)
```json
{
    "pH Tanah": 6.0,
    "C-Organik": 1.52,
    "KTK": 21.05,
    "Tekstur": "sandy loam",
    "Kedalaman Tanah": 110.0,
    "Kemiringan Lereng": 45.0
}
```

**Mapping Field:**
```
PH_NILAI      → pH Tanah
CORG_NILAI    → C-Organik
KTK_NILAI     → KTK
TEKSTUR       → Tekstur
DALAM_TNH     → Kedalaman Tanah
KL            → Kemiringan Lereng
```

**Proses Normalisasi:**
```python
# Extract number from string formats:
- ">45%" → 45.0
- "0 - 110" → 110.0 (ambil max)
- "6.0" → 6.0 (direct)
```

### 3.3 Analysis Flow: Frontend → API → Backend → Database

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FRONTEND REQUEST                                        │
├─────────────────────────────────────────────────────────────┤
│ User input:                                                 │
│   - Komoditas: [1, 2] (padi, cabai)                       │
│   - Layer: 15 (unit_lahan, 1595 fitur)                     │
│   - Method: minimum                                        │
│                                                              │
│ JavaScript:                                                 │
│   fetch('/analysis/api/analysis/suitability/batch/', {     │
│       method: 'POST',                                      │
│       body: JSON.stringify({                               │
│           commodity_ids: [1, 2],                           │
│           layer_id: 15,                                    │
│           method: 'minimum',                               │
│           include_limiting_factors: true                   │
│       })                                                   │
│   })                                                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. API RECEPTION (analysis/suitability_api.py)            │
├─────────────────────────────────────────────────────────────┤
│ BatchSuitabilityAnalysisAPIView.post():                    │
│   1. Parse JSON request                                     │
│   2. Validate form (BatchSuitabilityAnalysisForm)          │
│   3. Check layer_id or soil_data provided                  │
│   4. Call _process_layer_analysis() or                     │
│      _process_direct_analysis()                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. LAYER-BASED ANALYSIS (_process_layer_analysis)        │
├─────────────────────────────────────────────────────────────┤
│ Input: layer_id = 15, commodity_ids = [1, 2]             │
│                                                              │
│ Step 1: Get Layer                                          │
│   layer = MasterLayer.objects.get(id=15)                   │
│   features = layer.features.all()  # QuerySet             │
│   # Returns 1595 FeatureData records                       │
│                                                              │
│ Step 2: Loop per Commodity                                 │
│   for commodity_id in [1, 2]:                             │
│       feature_results = []                                 │
│                                                              │
│       Step 3: Loop per Feature                             │
│           for feature in features:  # 1595 iterations     │
│               # Extract soil data                          │
│               soil_data = extract_soil_data_from_feature(  │
│                   feature.attributes                        │
│               )                                             │
│               # Returns: {                                 │
│               #   "pH Tanah": 6.0,                         │
│               #   "C-Organik": 1.52,                       │
│               #   "KTK": 21.05,                            │
│               #   ...                                     │
│               # }                                          │
│                                                              │
│               # Run analysis                               │
│               result = analyze_suitability_minimum(         │
│                   commodity_id=commodity_id,                │
│                   soil_data=soil_data,                      │
│                   include_limiting_factors=true             │
│               )                                             │
│               # Returns: {                                 │
│               #   "overall_class": "S2",                   │
│               #   "score": 3.2,                            │
│               #   "characteristics": [...],                 │
│               #   "limiting_factors": [...],                │
│               #   "recommendations": [...]                  │
│               # }                                          │
│                                                              │
│               # Store result                               │
│               feature_results.append({                      │
│                   'feature_id': feature.id,                 │
│                   'geometry': feature.geometry.geojson,     │
│                   'result': result                         │
│               })                                            │
│                                                              │
│       Step 4: Aggregate Results                            │
│           aggregated = aggregate_feature_results(           │
│               feature_results                                │
│           )                                                 │
│           # Returns: {                                     │
│           #   "total_features": 1595,                      │
│           #   "class_counts": {"S1": 400, "S2": 600, ...}, │
│           #   "class_percentages": {"S1": 25.1, ...},      │
│           #   "overall_class": "S2",                       │
│           #   "all_features": feature_results,              │
│           #   "limiting_factors": [...],                   │
│           #   "recommendations": [...]                     │
│           # }                                              │
│                                                              │
│       results[str(commodity_id)] = aggregated              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RESPONSE                                                │
├─────────────────────────────────────────────────────────────┤
│ JsonResponse({                                            │
│     'success': True,                                       │
│     'results': {                                          │
│         '1': {  # Komoditas Padi                          │
│             'commodity_id': 1,                             │
│             'total_features': 1595,                        │
│             'class_counts': {...},                         │
│             'overall_class': 'S2',                         │
│             'all_features': [...]                          │
│         },                                                  │
│         '2': {  # Komoditas Cabai                         │
│             ...                                            │
│         }                                                   │
│     },                                                      │
│     'summary': {                                           │
│         'total_commodities': 2,                            │
│         'successful': 2,                                   │
│         'failed': 0,                                       │
│         'processing_time': '3.45s'                         │
│     }                                                       │
│ })                                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. FRONTEND RENDERING                                      │
├─────────────────────────────────────────────────────────────┤
│ 1. Process response:                                       │
│    - Store results in commodityResults object              │
│    - Update commodities list panel                         │
│                                                              │
│ 2. Display first commodity:                                │
│    - Hide map empty state                                  │
│    - Create GeoJSON from all_features                      │
│    - Add to Leaflet map with color coding                  │
│    - Fit map bounds                                        │
│                                                              │
│ 3. Update results panel:                                   │
│    - Show statistics                                       │
│    - Show class distribution                               │
│    - Show limiting factors                                 │
│    - Show recommendations                                  │
│                                                              │
│ 4. User interaction:                                       │
│    - Click commodity → switch map display                 │
│    - Click polygon → show popup with details               │
│    - Use zoom/pan controls                                 │
└─────────────────────────────────────────────────────────────┘
```

### 3.4 GeoServer Integration

```
Publish Flow:
    ↓
Create Result Layer in PostGIS
    ↓
GeoServer REST API Call:
    POST /geoserver/rest/workspaces/gisportal/datastores
    POST /geoserver/rest/workspaces/gisportal/layers
    ↓
Generate SLD Style:
    - S1 class → #006400 (dark green)
    - S2 class → #32CD32 (light green)
    - S3 class → #FFD700 (gold)
    - N class  → #DC143C (red)
    ↓
Apply Style to Layer
    ↓
Layer Available via WMS:
    GET /geoserver/gisportal/wms?
        SERVICE=WMS&
        VERSION=1.3.0&
        REQUEST=GetMap&
        LAYERS=gisportal:padi_suitability_2024&
        STYLES=suitability&
        BBOX=...
```

---

## 4. Alur Analisis Detail

### 4.1 Ekstraksi Data Tanah

```python
# spatial/utils/suitability_analysis.py

def extract_soil_data_from_feature(attributes: dict) -> dict:
    """
    Extract dan translate soil data dari FeatureData.attributes

    Mapping:
    - PH_NILAI      → pH Tanah
    - CORG_NILAI    → C-Organik
    - KTK_NILAI     → KTK
    - TEKSTUR       → Tekstur
    - DALAM_TNH     → Kedalaman Tanah
    - KL            → Kemiringan Lereng
    """

    mapping = {
        'PH_NILAI': 'pH Tanah',
        'CORG_NILAI': 'C-Organik',
        'KTK_NILAI': 'KTK',
        'TEKSTUR': 'Tekstur',
        'DALAM_TNH': 'Kedalaman Tanah',
        'KL': 'Kemiringan Lereng',
    }

    def _process_value(key: str, value: Any) -> Any:
        # Handle special formats:
        # ">45%" → 45.0
        # "0 - 110" → 110.0
        # "6.0" → 6.0
        ...
```

### 4.2 Penentuan Kelas Kesesuaian

```python
# spatial/utils/limiting_factors.py

def determine_suitability_class(value, characteristic):
    """
    Tentukan kelas kesesuaian (S1/S2/S3/N) berdasarkan nilai

    Priority: S1 → S2 → S3 → N (first match wins)

    Untuk data_type = 'numeric':
    - Parse criteria strings:
        * "6-7" → range 6.0 to 7.0
        * "< 4" → range -inf to 4.0
        * "> 8" → range 8.0 to inf
    - Check if value in range

    Untuk data_type = 'text':
    - Case-insensitive string matching
    - Support comma-separated values
    """
```

### 4.3 Metode Analisis FAO

#### **Minimum Method (Konservatif)**
```
Prinsip: Kelas overall = kelas terburuk dari semua karakteristik

Priority Order: N > S3 > S2 > S1

Contoh:
- pH Tanah → S2
- C-Organik → S1
- KTK → S3
- Tekstur → S1

Overall = S3 (yang terburuk)

Formula: Overall = min(S1, S2, S3, N)
```

#### **Weighted Method (Rata-rata Tertimbang)**
```
Prinsip: Kelas overall berdasarkan skor rata-rata

Scoring:
  S1 = 4 points
  S2 = 3 points
  S3 = 2 points
  N  = 1 point

Formula:
  Weighted Score = Σ(Score_i × Weight_i) / Σ(Weight_i)

Classification:
  - S1: 3.5 - 4.0
  - S2: 2.5 - 3.5
  - S3: 1.5 - 2.5
  - N:  0.0 - 1.5

Default Weights:
  - pH Tanah: 1.0
  - C-Organik: 0.9
  - KTK: 0.8
  - Tekstur: 0.8
  - Kemiringan Lereng: 0.9
  - Kedalaman Tanah: 0.8
```

#### **Parametric Method (Hybrid)**
```
Prinsip: Kombinasi minimum + weighted

Logic:
  IF ada kelas N:
      return N (langsung gagal)
  ELSE:
      gunakan weighted method

Keuntungan:
  - Tetap konservatif untuk N
  - Lebih fleksibel untuk S1-S3
```

### 4.4 Limiting Factors & Rekomendasi

```python
# spatial/models.py - LimitingFactor

class LimitingFactor:
    characteristic = ForeignKey(SuitabilityCharacteristic)
    suitability_class = CharField(choices=['S1', 'S2', 'S3', 'N'])
    solution = TextField()           # Solusi perbaikan
    cost_estimate = DecimalField()    # Estimasi biaya
    time_required = CharField()       # Waktu yang dibutuhkan
    priority = IntegerField()         # Prioritas (1-10)
    severity = CharField()            # Tingkat keparahan
    effectiveness = CharField()       # Efektivitas solusi

# Alur penentuan limiting factor:
1. Cek karakteristik dengan kelas S3 atau N
2. Ambil LimitingFactor untuk characteristic + class tersebut
3. Return list solusi yang tersedia
4. Sort by priority dan severity
```

---

## 5. Model Database

### 5.1 User & Profile (core)

```python
class User(AbstractUser):
    full_name = CharField(max_length=100)

class UserProfile:
    user = OneToOneField(User)
    active_data_year = ForeignKey('master_data.DataYear')
```

### 5.2 Master Data (master_data)

```python
class CommodityGroup:
    name = CharField()  # "Pangan", "Hortikultura", etc.
    is_active = BooleanField(default=True)

class Commodity:
    name = CharField()  # "Padi", "Jagung", etc.
    group = ForeignKey(CommodityGroup)
    characteristics = ManyToMany(SuitabilityCharacteristic)

class SuitabilityCharacteristic:
    commodity = ForeignKey(Commodity)
    name = CharField()  # "pH Tanah", "C-Organik", etc.

    # Kriteria FAO
    s1_value = CharField()  # "6-7"
    s2_value = CharField()  # "5-6"
    s3_value = CharField()  # "4-5"
    n_value = CharField()   # "< 4"

    data_type = CharField(choices=['numeric', 'text'])
    unit = CharField()  # "", "%", "cmol(+)/kg", etc.
```

### 5.3 Spatial Data (spatial)

```python
class MasterLayer:
    name = CharField(max_length=100)
    layer_type = CharField(choices=[
        'point', 'linestring', 'polygon', 'multipolygon'
    ])
    layer_category = CharField(choices=[
        'tanah', 'komoditas', 'base_analisis', 'lainnya'
    ])
    table_name = CharField(unique=True)
    data_year = ForeignKey('master_data.DataYear')
    kabupaten = ForeignKey('Kabupaten')
    attributes = JSONField(default=dict)
    is_active = BooleanField(default=True)

    # GeoServer integration
    style_sld = TextField()
    style_file = FileField(upload_to='layer_styles/')

class FeatureData(GISModel):
    layer = ForeignKey(MasterLayer, related_name='features')
    attributes = JSONField(default=dict)
    geometry = GeometryField(srid=4326)  # PostGIS

    # Soil characteristics di attributes:
    # {
    #     "PH_NILAI": 6.0,
    #     "CORG_NILAI": 1.52,
    #     "KTK_NILAI": 21.05,
    #     ...
    # }

class SuitabilityAnalysisResult:
    commodity = ForeignKey('master_data.Commodity')
    base_layer = ForeignKey(MasterLayer)
    result_layer_name = CharField()
    total_features = IntegerField()
    class_distribution = JSONField()  # {"S1": 100, "S2": 200, ...}
    created_at = DateTimeField(auto_now_add=True)
```

### 5.4 GeoServer Publishing

```python
class GeoServerPublishing:
    layer = OneToOneField(MasterLayer)
    workspace = CharField(default='gisportal')
    store = CharField(default='gisportal_store')
    is_published = BooleanField(default=False)
    published_at = DateTimeField()
```

---

## 6. API Endpoints

### 6.1 Analysis APIs (analysis/suitability_api.py)

```
POST /analysis/api/analysis/suitability/
    Analisis kesesuaian untuk SATU komoditas

    Request:
    {
        "commodity_id": 1,
        "method": "minimum",  # atau "weighted", "parametric"
        "soil_data": {
            "pH Tanah": 6.0,
            "C-Organik": 1.52,
            ...
        },
        "weights": {
            "pH Tanah": 1.0,
            "C-Organik": 0.9,
            ...
        },  # optional, untuk weighted method
        "include_limiting_factors": true
    }

    Response:
    {
        "commodity_id": 1,
        "commodity_name": "Padi",
        "method": "minimum",
        "overall_class": "S2",
        "overall_class_display": "S2 - Cukup Sesuai",
        "overall_score": 3.2,
        "characteristics": [
            {
                "name": "pH Tanah",
                "value": 6.0,
                "class": "S1",
                "score": 4.0
            },
            ...
        ],
        "limiting_factors": [...],
        "recommendations": [...],
        "summary": {...}
    }
```

```
POST /analysis/api/analysis/suitability/batch/
    Analisis kesesuaian untuk BANYAK komoditas dengan LAYER

    Request:
    {
        "commodity_ids": [1, 2, 3],  # padi, jagung, kedelai
        "layer_id": 15,  # unit_lahan
        "method": "minimum",
        "include_limiting_factors": true
    }

    Response:
    {
        "success": true,
        "results": {
            "1": {
                "commodity_id": 1,
                "total_features": 1595,
                "class_counts": {
                    "S1": 400,
                    "S2": 600,
                    "S3": 395,
                    "N": 200
                },
                "class_percentages": {
                    "S1": 25.1,
                    "S2": 37.6,
                    "S3": 24.8,
                    "N": 12.5
                },
                "overall_class": "S2",
                "all_features": [
                    {
                        "feature_id": 109,
                        "geometry": {...},
                        "result": {
                            "overall_class": "S1",
                            "score": 3.8,
                            ...
                        }
                    },
                    ...
                ],
                "limiting_factors": [...],
                "recommendations": [...]
            },
            "2": {...},  # jagung
            "3": {...}   # kedelai
        },
        "summary": {
            "total_commodities": 3,
            "successful": 3,
            "failed": 0,
            "processing_time": "12.34s"
        }
    }
```

```
GET /analysis/api/analysis/methods-info/
    Informasi tentang metode analisis yang tersedia

    Response:
    {
        "methods": [
            {
                "id": "minimum",
                "name": "Minimum Method (FAO Framework)",
                "description": "...",
                "use_cases": [...],
                "advantages": [...],
                "disadvantages": [...],
                "formula": "Overall = min(S1, S2, S3, N)"
            },
            ...
        ],
        "scoring": {
            "S1": {
                "score": 4,
                "name": "Sangat Sesuai",
                "description": "Tidak ada kendala signifikan"
            },
            ...
        },
        "default_weights": {
            "pH Tanah": 1.0,
            "C-Organik": 0.9,
            ...
        }
    }
```

### 6.2 Layer & Map APIs (spatial/views)

```
GET /spatial/api/layers/
    List semua layers dengan filter

    Query params:
    - data_year: 2024
    - kabupaten: Barru
    - category: tanah
    - search: unit_lahan

    Response: [...]
```

```
GET /spatial/api/layers/<id>/geojson/
    Get layer sebagai GeoJSON

    Response:
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {...},
                "properties": {
                    "id": 109,
                    "PH_NILAI": 6.0,
                    ...
                }
            },
            ...
        ]
    }
```

```
POST /spatial/api/feature-at-point/
    Get fitur pada titik yang diklik

    Request:
    {
        "layer_id": 15,
        "x": 119.5432,
        "y": -4.5678,
        "srid": 4326
    }

    Response: Feature details
```

---

## 7. Konfigurasi Warna & Legenda

### Suitability Class Colors
```
S1 (Sangat Sesuai):  #006400 (Dark Green)
S2 (Cukup Sesuai):   #32CD32 (Light Green)
S3 (Sesuai Marginal): #FFD700 (Gold/Yellow)
N  (Tidak Sesuai):   #DC143C (Crimson Red)
```

### Legenda di Peta
```
┌─────────────────────────────┐
│ Legenda Kesesuaian          │
├─────────────────────────────┤
│ ■ S1  Sangat Sesuai        │
│ ■ S2  Cukup Sesuai         │
│ ■ S3  Sesuai Marginal      │
│ ■ N   Tidak Sesuai         │
└─────────────────────────────┘
```

---

## 8. Troubleshooting Common Issues

### Issue: Analisis return "Unknown" class
**Possible causes:**
1. Soil data tidak ada di feature.attributes
2. Field mapping salah (PH_NILAI vs pH_TANAH)
3. Criteria tidak cocok dengan data type

**Solution:**
```python
# Check feature attributes
from spatial.models import FeatureData
f = FeatureData.objects.filter(layer_id=X).first()
print(f.attributes.keys())

# Check mapping
from helpers import SOIL_PARAMETER_TRANSLATION
```

### Issue: Layer tidak muncul di dropdown
**Possible causes:**
1. Layer is_active = False
2. Layer tidak sesuai dengan filter (data_year, kabupaten)
3. Layer tidak memiliki fitur

**Solution:**
```python
# Check layer status
from spatial.models import MasterLayer
layer = MasterLayer.objects.get(id=X)
print(layer.is_active)
print(layer.features.count())
```

### Issue: GeoServer WMS tidak load
**Possible causes:**
1. Layer belum published
2. SLD style error
3. Workspace salah

**Solution:**
```python
# Check publishing status
from spatial.models import GeoServerPublishing
pub = GeoServerPublishing.objects.get(layer_id=X)
print(pub.is_published)

# Republish
from spatial.utils.geoserver import GeoServerClient
client = GeoServerClient()
client.publish_layer(layer)
```

---

## 9. Best Practices

### Untuk Pengembang
1. **Gunakan Django ORM** untuk query, jangan raw SQL
2. **Select related** untuk mengurangi N+1 queries
3. **Cache commodity data** yang sering diakses
4. **Validate input** sebelum proses analisis
5. **Handle edge cases** (missing data, null values, etc.)
6. **Log errors** dengan detail untuk debugging

### Untuk User
1. **Pastikan shapefile valid** sebelum upload
2. **Gunakan field name yang konsisten** di shapefile
3. **Setup criteria dengan benar** sebelum analisis
4. **Test dengan layer kecil** dulu untuk validasi
5. **Backup data** sebelum operasi besar

---

## 10. Glossary

| Term | Penjelasan |
|------|-----------|
| **FAO** | Food and Agriculture Organization (Organisasi Pangan dan Pertanian Dunia) |
| **S1/S2/S3/N** | Kelas kesesuaian lahan menurut FAO |
| **PostGIS** | Ekstensi PostgreSQL untuk data spasial |
| **GeoServer** | Server untuk publish data spasial sebagai WMS |
| **WMS** | Web Map Service - standar untuk serving map images |
| **GeoJSON** | Format JSON untuk data geospasial |
| **SLD** | Styled Layer Descriptor - XML untuk styling GeoServer |
| **Shapefile** | Format file geospasial (.shp, .shx, .dbf) |
| **HTMX** | Library untuk dynamic HTML tanpa banyak JavaScript |
| **Leaflet** | JavaScript library untuk interactive maps |

---

*Dokumentasi ini dibuat untuk memahami alur sistem Analisis Kesesuaian Lahan secara komprehensif.*

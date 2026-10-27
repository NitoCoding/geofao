# BAB I

## PENDAHULUAN

### 1.1 Latar Belakang

Sektor pertanian memegang peranan strategis dalam perekonomian nasional dan ketahanan pangan Indonesia. Sebagai negara agraris, produktivitas pertanian menjadi salah satu penentu kesejahteraan masyarakat dan stabilitas negara. Salah satu faktor kunci yang menentukan keberhasilan dan keberlanjutan usaha tani adalah kesesuaian antara jenis tanaman yang dibudidayakan dengan karakteristik lahan yang digunakan. Penanaman pada lahan yang tidak sesuai dapat mengakibatkan rendahnya hasil panen, penggunaan input (pupuk, pestisida) yang tidak efisien, dan bahkan kerusakan ekosistem lahan itu sendiri.

Proses penilaian kesesuaian lahan secara tradisional sering kali mengandalkan survei lapangan dan analisis manual yang bersifat kompleks dan memakan waktu lama, terutama untuk area yang cukup luas. Metode ini juga menghadapi tantangan dalam mengintegrasikan berbagai parameter lahan—seperti karakteristik tanah (tekstur, pH, kesuburan), iklim (curah hujan, suhu), dan topografi (kemiringan)—secara simultan dan komprehensif. Akibatnya, informasi mengenai potensi lahan sering kali tidak tersedia secara tepat waktu, sulit diakses oleh berbagai kalangan, dan kurang mendukung pengambilan keputusan yang cepat dan akurat.

Perkembangan teknologi informasi, khus usnya Sistem Informasi Geografis (SIG), mem bawa solusi dalam mengatasi tantangan ters ebut. SIG memung kinkan analisis data spasial menjadi lebih efisien dan terintegrasi. Dengan menghadirkan SIG dalam platform web, aksesibilitas informasi geospasial dapat diperluas kepada berbagai pemangku kepentingan, mulai dari petani, penyuluh pertanian, hingga perencana kebijakan, tanpa memerlukan perangkat lunak yang mahal dan keahlian teknis yang mendalam.

Melihat potensi ini, penel itian ini ber tujuan untuk mengembangkan sebuah Sistem Informasi Kesesuaian Lahan Pertanian berbasis WebGIS untuk Kabupaten Barru, Provinsi Sulawesi Selatan. Sistem ini dibangun menggunakan kerangka kerja *Design Science Research Methodology* (DSRM) dari Peffers et al. (2007) sebagai paradigma penel itian dan *Rapid Application Development* (R AD) dari Kendall & Kendall (2020) sebagai metode pengembangan perangkat lunak. Sistem diimplementasikan dengan *stack* teknologi Django, PostgreSQL + PostGIS untuk peny impanan data geospasial, Celery + Redis untuk pemrosesan analisis secara *asynchronous*, serta Leaflet.js untuk visual isasi peta interaktif.

Sistem tidak hanya melakukan klasifikasi kesesuaian lahan ke dalam empat kelas FAO (S1, S2, S3, N) meng gunakan *FAO Minimum Method*, tetapi juga menye diakan fitur *Expert Review* yang memung kinkan tenaga ahli pertanian mem berikan catatan lapangan (*ground truth*) pada setiap poligon hasil analisis. Sistem juga dilengkapi modul *Identity and Access Management* (IAM) dengan tiga tingkat akses pengguna — admin, tenaga ahli, dan guest — untuk menjamin keamanan data dan pembagian wewenang yang jelas. Dengan demikian, diharapkan sistem ini dapat menjadi alat bantu pengambilan keputusan yang cerdas, aksesibel, dan tervalidasi secara ilmiah untuk mendukung peningkatan produktivitas pertanian di Kabupaten Barru.

### 1.2 Rumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, maka rumusan masalah dalam penelitian ini adalah sebagai berikut:

1. Bagaimana mengembangkan sistem WebGIS yang mampu mengintegrasikan data spasial (shapefile/GeoJSON) dengan parameter karakteristik lahan untuk melakukan analisis kesesuaian lahan pertanian secara terkomputasi di Kabupat en Barru?
2. Bagaimana mengimplementasikan *FAO Minimum Method* dalam sistem berbasis web sehingga mampu mengklasifikasikan kesesuaian lahan ke dalam kelas S1, S2, S3, dan N secara akurat dan konsisten dengan perhitungan manual?
3. Bagaimana menye diakan mekanisme validasi hasil analisis oleh tenaga ahli pertanian melalui fitur *Expert Review* yang terintegrasi dalam sistem, sehingga hasil klasifikasi sistem dapat diband ingkan dengan kondisi lapangan?
4. Bagaimana mengelola hak akses pengguna melalui modul IAM (*Identity and Access Management*) untuk menjamin keamanan data dan pembagian wewenang yang sesuai dengan peran masing-masing pengguna (admin, tenaga ahli, guest)?

### 1.3 Batasan Masalah

Agar penel itian ini tetap fokus dan terarah, perlu ditetapkan batasan-batasan sebagai berikut:

1. **Batasan Wilayah:** Sistem dikembangkan dan diuji meng gunakan data spasial Kabupat en Barru, Provinsi Sulawesi Selatan, dengan luas wilayah 1.174 km² yang mencakup 7 kecamatan. Namun, sistem dirancang agar dapat dikembangkan untuk wilayah lain dengan mengganti data spasial yang digunakan.
2. **Batasan Parameter:** Analisis kesesuaian lahan meng gunakan parameter utama yang tersedia dalam data, meliputi: pH tanah, C-Organik, Kapasitas Tukar Kation (KTK), tekstur tanah, kemiringan lereng, kedalaman tanah efektif, drainase, dan curah hujan.
3. **Batasan Algoritma:** Penel itian ini mengimplementasikan *FAO Minimum Method* sebagai metode analisis kesesuaian lahan, di mana kelas kesesuaian akhir ditentukan oleh parameter dengan nilai terburuk sesuai prinsip *Law of the Minimum*.
4. **Batasan Fungsionalitas:** Sistem berfungsi sebagai alat bantu pengambilan keputusan (*decision support system*), bukan sebagai satu-satunya penentu keputusan. Hasil analisis dari sistem tetap memerlukan pertimbangan dan validasi dari ahli pertanian melalui fitur *Expert Review* yang disediakan.
5. **Batasan Teknologi:** Data spasial disajikan langsung melalui GeoJSON API dari Django ke Leaflet.js tanpa ketergantungan pada *map server* eksternal. Data spasial yang digunakan bersumber dari data sekunder yang disediakan oleh LMPP UNHAS, bukan dari proses penginderaan jauh dari awal.
6. **Batasan Akses:** Sistem menye diakan tiga tingkat akses pengguna (admin, tenaga ahli, guest) melalui modul IAM.

### 1.4 Tujuan Penelitian

Penel itian ini ber tujuan untuk mengembangkan Sistem Informasi Kesesuaian Lahan Pertanian berbasis WebGIS yang mengimplementasikan *FAO Minimum Method* dengan kerangka kerja DSRM dan pendekatan pengembangan RAD. Secara spesifik, tujuan penel itian dirumuskan sebagai berikut:

1. Mengembangkan sistem WebGIS meng gunakan framework Django, PostgreSQL + PostGIS, Celery + Redis, dan Leaflet.js yang dapat mengintegrasikan data spasial (shapefile/GeoJSON) dengan parameter karakteristik lahan untuk wilayah Kabupat en Barru.
2. Mengimplementasikan algoritma *FAO Minimum Method* untuk mengklasifikasikan kesesuaian lahan ke dalam kelas S1, S2, S3, dan N secara terkomputasi, dengan pemrosesan *asynchronous* melalui Celery untuk menangani dataset besar (1.595 unit lahan).
3. Mengembangkan fitur *Expert Review* yang memung kinkan tenaga ahli pertanian mem berikan catatan lapangan pada setiap poligon hasil analisis sebagai validasi terhadap hasil kalkulasi sistem.
4. Mengimplementasikan modul IAM (*Identity and Access Management*) dengan tiga tingkat akses pengguna (admin, tenaga ahli, guest) untuk menjamin keamanan data dan pembagian wewenang yang sesuai.
5. Menguji performa dan fungsionalitas sistem melalui *black box testing* (47 test case pada 7 modul), uji performa (waktu respons analisis), dan evaluasi kebutuhan non-fungsional.

### 1.5 Tinjauan Pustaka

#### 1.5.1 Sistem Informasi

Sistem informasi dapat didefinisikan sebagai sekumpulan komponen yang saling terkait yang berfungsi untuk mengumpulkan, memroses, menyimpan, dan mendistribusikan informasi guna mendukung pengambilan keputusan, koordinasi, dan pengendalian dalam suatu organisasi (Laudon et al., 2020). O'B rien dan Marakas (2017) mendefinisikan sistem informasi sebagai kombinasi terorganisasi dari manusia, perangkat keras, perangkat lunak, jaring an komunikasi, sumber daya data, serta kebijakan dan prosedur yang menyimpan, mengambil, mentransformasikan, dan mendiseminasikan informasi dalam suatu organisasi.

Dalam perspektif manajemen, sistem informasi tidak semata-mata merupakan persoalan teknologi, melainkan mencakup dimensi organisasi dan manusia yang saling berinteraksi. Stair dan Reynolds (2018) menekankan bahwa nilai suatu sistem informasi ditentukan oleh seja uh mana sistem tersebut mampu mendukung pencapaian tujuan organisasi, meningkatkan produktivitas, dan memfasilitasi proses bisnis yang lebih efektif. Dalam konteks penel itian ini, sistem informasi yang dibangun ber tujuan untuk mendukung proses evaluasi kesesuaian lahan pertanian di Kabupat en Barru dengan menye diakan platform terpusat yang mengintegrasikan fungsi peny impanan data spasial, analisis kesesuaian lahan berbasis FAO, validasi tenaga ahli, dan visual isasi hasil ber upa peta interaktif.

#### 1.5.2 Sistem Informasi Geografis

**Konsep SIG**

Sistem Informasi Geografis (SIG) atau *Geographic Information System* (GIS) adalah sistem komputer yang dirancang untuk mengumpulkan, menyimpan, menganalisis, dan menampilkan data yang memiliki referensi geografis atau spasial (Aronoff, 1989). Kemampuan utama SIG yang membedakan dari sistem informasi konvensional adalah kapasitasnya menghubungkan data atribut dengan lokasi di permukaan bumi (koordinat X dan Y). Integrasi antara data spasial dan non-spasial ini memung kinkan analisis yang mempertimbangkan dimensi keruangan, seperti *overlay*, *buffer*, dan analisis jaring an.

**Data Spasial dan Atribut**

Data dalam SIG terdiri dari dua komponen utama. Pertama, **data spasial** yang merepresentasikan lokasi dan bentuk objek geografis dalam dua model: model vektor (titik, garis, poligon) dan model raster (grid/piksel). Kedua, **data atribut** yang berisi informasi deskriptif yang melekat pada objek spasial, seperti nama, nilai pH, atau jenis tanah. Dalam penel itian ini, data spasial yang digunakan ber upa poligon unit lahan dalam format vektor dengan atribut karakteristik tanah yang disimpan dalam *field* atribut setiap fitur.

**Komponen SIG**

SIG terdiri dari lima komponen utama yang saling terkait: (1) **perangkat keras** (*hardware*) ber upa komputer dan perangkat pendukung; (2) **perangkat lunak** (*software*) untuk pemrosesan dan analisis data; (3) **data** spasial dan atribut sebagai bahan baku; (4) **manusia** (*people*) sebagai pengguna dan pengelola sistem; serta (5) **metode** atau prosedur analisis yang terstandarisasi. Keberhasilan implementasi SIG bergantung pada keseimbangan dan integrasi seluruh komponen tersebut (Heywood et al., 2011).

**WebGIS**

WebGIS merupakan evolusi dari SIG desktop tradisional ke platform berbasis web, memung kinkan fungsi-fungsi SIG diakses melalui peramban web tanpa memerlukan instalasi perangkat lunak khus us (Peng & Tsou, 2003). Keungulan utama WebGIS meliputi: aksesibilitas tinggi dari berbagai perangkat, distribusi informasi yang cepat dan serentak, kemandirian platform (*cross-platform*), serta pembaruan data yang terpusat di server. Arsitektur WebGIS modern mengadopsi model *client-server* di mana *frontend* (Leaflet, OpenLayers) menangani visual isasi dan interaksi, *backend* (Django, FastAPI) memroses logika bisnis, dan database spasial (PostGIS) menyimpan serta meng-*query* data geografis.

#### 1.5.3 Evaluasi Kesesuaian Lahan

**Konsep Evaluasi Lahan**

Evaluasi lahan (*land evaluation*) adalah proses penilaian potensi penggunaan lahan untuk tujuan tertentu, seperti pertanian, kehutanan, atau penggunaan lainnya (FAO, 1976). Proses ini mencakup interpretasi dan analisis data mengenai karakteristik lahan—termasuk tanah, iklim, dan topografi—untuk menentukan tingkat kesesuaian terhadap jenis penggunaan lahan yang direncanakan. Evaluasi lahan menjadi langkah fundamental dalam perencanaan penggunaan lahan yang rasional karena memberikan informasi tentang potensi dan keterbatasan setiap unit lahan.

**Pendekatan FAO**

*Food and Agriculture Organization* (FAO) melalui publikasi *A Framework for Land Evaluation* (1976) menetapkan standar internasional untuk evaluasi kesesuaian lahan. Kerangka kerja ini memperkenalkan konsep *matching*—yakni proses pencocokan antara persyaratan tumbuh tanaman (*crop requirements*) dengan karakteristik dan kualitas lahan aktual (*land characteristics and qualities*). Pendekatan FAO bersifat multi-kriteria dan mempertimbangkan aspek fisik, kimia, dan biologis lahan secara simultan. Keunggulan pendekatan ini terletak pada sifatnya yang sistematis, dapat direplikasi, dan memungkinkan perbandingan antar wilayah.

**Kelas Kesesuaian Lahan**

Dalam kerangka FAO, hasil evaluasi lahan diklasifikasikan ke dalam empat kelas utama berdasarkan tingkat faktor pembatas yang ditemukan:

| Kelas  | Nama                                    | Deskripsi                                                                                                                    |
| ------ | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **S1** | Sangat Sesuai (*Highly Suitable*)       | Lahan tidak memiliki faktor pembatas signifikan; produktivitas optimal dapat dicapai dengan input standar.                   |
| **S2** | Cukup Sesuai (*Moderately Suitable*)    | Lahan memiliki faktor pembatas ringan yang sedikit mengurangi produktivitas; memerlukan input tambahan yang masih ekonomis.  |
| **S3** | Sesuai Marginal (*Marginally Suitable*) | Lahan memiliki faktor pembatas berat yang secara signifikan menurunkan produktivitas; memerlukan input dan manajemen tinggi. |
| **N**  | Tidak Sesuai (*Not Suitable*)           | Lahan memiliki faktor pembatas sangat berat yang tidak memung kinkan penggunaan berkelanjutan dengan teknologi yang tersedia. |

**Faktor Pembatas (Limiting Factor)**

Faktor pembatas adalah karakteristik lahan yang nilainya berada di bawah ambang batas optimal sehingga menghambat pertumbuhan dan produktivitas tanaman (S ys et al., 1991). Dalam evaluasi kesesuaian lahan, faktor pembatas dapat ber upa: pH tanah yang terlalu rendah atau tinggi, kandungan bahan organik yang kurang, kemiringan lereng yang terjal, drainase yang buruk, atau kedalaman tanah yang dangkal. Setiap faktor pembatas memiliki solusi perbaikan spesifik—misalnya pengapuran untuk pH rendah, penambahan pupuk organik untuk C-Organik rendah, atau pembuatan terasering untuk kemiringan curam—yang memerlukan analisis biaya-manfaat sebelum diterapkan.

**Metode Matching**

Prosedur pencocokan (*matching*) dilakukan dengan membandingkan setiap parameter lahan aktual terhadap kriteria persyaratan tumbuh tanaman yang telah ditetapkan. Metode yang paling umum digunakan adalah *FAO Minimum Method*, di mana kelas kesesuaian keseluruhan ditentukan oleh parameter dengan nilai terburuk. Prinsip ini konsisten dengan hukum minimum Liebig: pertumbuhan tanaman dibatasi oleh faktor yang paling langka, bukan oleh jumlah total sumber daya yang tersedia. Secara matematis, metode ini dapat dinyatakan sebagai:

$$
C\_{akhir} = \min(C\_1, C\_2, ..., C\_n)
$$

di mana $C\_{akhir}$ adalah kelas kesesuaian akhir dan $C\_i$ adalah nilai skor dari masing-masing parameter lahan (FAO, 1976; Djaenudin et al., 2011).

#### 1.5.4 Evaluasi Kesesuaian Lahan FAO

**Konsep Evaluasi Lahan**

Evaluasi lahan adalah proses penilaian potensi penggunaan lahan untuk tujuan tertentu, seperti pertanian, kehutanan, atau penggunaan lainnya (FAO, 1976). *Food and Agriculture Organization* (FAO) melalui publikasi *A Framework for Land Evaluation* (1976) menetapkan kerangka kerja standar internasional untuk mengevaluasi kesesuaian lahan berdasarkan karakteristik fisik, kimia, dan lingkungan. Kerangka kerja ini telah diadopsi secara luas dalam penel itian pertanian dan perencanaan tata guna lahan di berbagai negara, termasuk Indonesia.

**Klasifikasi Kesesuaian Lahan**

Sistem klasifikasi FAO membagi kesesuaian lahan ke dalam empat kelas utama (Djaenudin et al., 2011):

- **S1 (Sangat Sesuai):** Lahan tidak memiliki pembatas yang berarti untuk penggunaan tertentu secara berkelanjutan, atau hanya memiliki pembatas minor yang tidak berpengaruh signifikan terhadap produktivitas.
- **S2 (Cukup Sesuai):** Lahan memiliki pembatas agak berat yang memerlukan input tambahan untuk mempertahankan tingkat produktivitas. Input yang diperlukan umumnya lebih tinggi dari S1 namun masih dalam batas ekonomis.
- **S3 (Sesuai Marginal):** Lahan memiliki pembatas yang berat dan memerlukan input yang tinggi. Keuntungan yang diperoleh umumnya hanya sedikit di atas biaya produksi.
- **N (Tidak Sesuai):** Lahan memiliki pembatas permanen yang sangat berat sehingga tidak memung kinkan untuk penggunaan tertentu secara berkelanjutan.

**FAO Minimum Method**

*FAO Minimum Method* adalah pendekatan klasifikasi yang mengadopsi prinsip *Law of the Minimum* dari Liebig: pertumbuhan tanaman dibatasi oleh faktor yang paling langka atau paling terbatas. Dalam konteks evaluasi lahan, kelas kesesuaian akhir suatu unit lahan ditentukan oleh parameter dengan nilai terburuk di antara seluruh parameter yang dievaluasi. Secara matematis, metode ini dirumuskan sebagai:

$$C_{akhir} = \min(C_1, C_2, C_3, ..., C_n)$$

di mana $C_i$ adalah kelas kesesuaian untuk parameter ke-$i$. Sebagai contoh, jika suatu unit lahan memiliki pH tanah pada kelas S1, tekstur pada kelas S2, tetapi kemiringan lereng pada kelas N, maka kelas kesesuaian akhir unit lahan tersebut adalah N. Pendekatan ini bersifat deterministik dan transparan — setiap hasil klasifikasi dapat ditelusuri kembali ke parameter yang menjadi pembatas, sehingga pengguna dapat mengetahui secara tepat karakteristik lahan mana yang perlu mendapat perhatian.

#### 1.5.5 Arsitektur dan Teknologi WebGIS

**Django Framework**

Django adalah *web framework* Python tingkat tinggi yang mendorong pengembangan aplikasi secara cepat dengan desain yang bersih dan pragmatis (Django Software Foundation, 2024). Dajngo mengimplementasikan pola arsitektur MVT (*Model-View-Template*) dengan komponen bawaan yang komprehensif: ORM (*Object-Relational Mapping*) untuk abstraksi database, sistem autentikasi dan otorisasi, *admin interface* yang *auto-generated*, *URL routing* yang fleksibel, *template engine* untuk rendering HTML, serta proteksi keamanan bawaan terhadap serangan umum (CSRF, XSS, SQL Injection). Dajngo dipilih sebagai *backend framework* utama karena skalabilitasnya yang teruji dan ekosistem pustaka pendukung yang luas.

**GeoDjango**

GeoDjango adalah ekstensi spasial dari Django yang mengintegrasikan fungsionalitas GIS ke dalam *framework* (Django Contributors, 2024). Fitur utama GeoDjango meliputi: *field* geometri (`PointField`, `PolygonField`, `GeometryField`) yang memung kinkan peny impanan data spasial langsung dalam model Django; *spatial queries* dan *lookups* (misalnya `distance__lt`, `bbcontains`, `intersects`); integrasi dengan pustaka GDAL/OGR untuk membaca, menulis, dan mentransformasi berbagai format data vektor; dukungan *Spatial Reference Systems* (SRS) untuk konversi antar sistem koordinat; serta kompatibilitas penuh dengan database spasial PostGIS. GeoDjango memung kinkan pengembang bekerja dengan data geografis meng gunakan sintaks Dajngo ORM yang familier, tanpa harus menulis SQL spasial secara manual.

**PostgreSQL dan PostGIS**

PostgreSQL adalah sistem manajemen basis data relasional *open-source* yang dikenal akan keandalan, kepatuhan terhadap standar SQL, dan ekstensibilitasnya (PostgreSQL Global Development Group, 2024). PostGIS adalah ekstensi spasial untuk PostgreSQL yang menambahkan dukungan untuk objek geografis, memung kinkan *query* lokasi dijalankan langsung dalam SQL. PostGIS menye diakan: tipe data geometri dan geografi; fungsi-fungsi spasial (`ST_Area`, `ST_Buffer`, `ST_Intersects`, `ST_Union`); indeks spasial berbasis GiST (*Generalized Search Tree*) untuk mempercepat *query* spasial pada dataset besar; dukungan standar OGC (*Open Geospatial Consortium*) termasuk WKT, WKB, dan GeoJSON; serta kemampuan transformasi koordinat antar SRID. Dalam sistem yang dikembangkan, PostGIS berperan sebagai peny impanan utama untuk geometri unit lahan dan menjalankan operasi spasial secara efisien langsung di sisi *database*.

**Celery dan Redis**

Celery adalah *distributed task queue* untuk Python yang memung kinkan eksekusi tugas secara *asynchronous* di luar *request-response cycle* HTTP (Celery Contributors, 2024). Ceelry meng gunakan *message broker* — dalam hal ini Redis — untuk menerima dan mendistribusikan *task* ke *worker*. Dalam sistem ini, Celery digunakan untuk menjalankan analisis kesesuaian lahan secara *background*, sehingga pengguna tidak perlu menunggu proses selesai dan antarmuka tetap responsif. Redis juga berfungsi sebagai *cache backend* melalui `django-redis` untuk menyimpan data yang sering diakses (kriteria kesesuaian, daftar layer) dengan TTL tertentu, mengurangi *query* berulang ke database.

**Identity and Access Management (IAM)**

*Identity and Access Management* (IAM) adalah kerangka kerja untuk mengelola identitas digital pengguna dan mengontrol akses mereka terhadap sumber daya sistem (Osmanoglu, 2014). Dalam sistem ini, IAM diimplementasikan melalui model `UserRole` yang menghubungkan pengguna Django dengan *role* tertentu. Sistem menye diakan tiga tingkat akses: **admin** (pengelolaan data, analisis, dan manajemen pengguna), **tenaga ahli** (input catatan lapangan melalui *Expert Review*), dan **guest** (melihat data tanpa kemampuan mengubah). Pembatasan akses diterapkan pada level *view* Django maupun tampilan antarmuka, di mana menu navigasi dan tombol aksi disesuaikan secara dinamis berdasarkan *role* pengguna yang sedang login.

#### 1.5.6 Teknologi Visualisasi dan Antarmuka

**Leaflet**

Leaflet adalah pustaka JavaScript *open-source* untuk peta interaktif yang ringan (sekitar 42 KB), dirancang dengan fokus pada kesederhanaan, performa, dan kegunaan (Agafonkin, 2024). Leaflet menye diakan fitur-fitur esensial untuk visual isasi peta web: dukungan *tile layers* (OpenStreetMap, WMS), *vector layers* (poligon, garis, titk, GeoJSON), interaksi pengguna (klik, hover, zoom, pan), kontrol peta (*zoom*, *layer switcher*, *scale*), serta *popup* dan *tooltip* untuk menampilkan informasi atribut. Dalam sistem ini, Leaflet digunakan untuk menampilkan poligon hasil analisis dengan kode warna sesuai kelas kesesuaian (hijau tua untuk S1, hijau muda untuk S2, kuning untuk S3, merah untuk N) dan menampilkan detail faktor pembatas ketika pengguna mengklik suatu poligon.

**HTMX**

HTMX adalah *library* JavaScript yang memung kinkan elemen HTML berinteraksi dengan server melalui atribut deklaratif (`hx-get`, `hx-post`, `hx-trigger`, dll.) tanpa menulis JavaScript kustom (Gross, 2024). HTMX memperluas HTML standar dengan memberikan akses ke *AJAX*, *CSS Transitions*, *WebSockets*, dan *Server Sent Events* langsung dari *markup*. Dalam sistem ini, HTMX digunakan untuk menangani interaksi dinamis seperti: mengirim form analisis tanpa *page reload*, melakukan *polling* status *task* Celery secara periodik, dan memperbarui bagian halaman (*partial update*) berdasarkan respons server. Pendekatan ini menjaga kode *frontend* tetap minimal dan terintegrasi erat dengan *template* Django.

**Tailwind CSS**

Tailwind CSS adalah kerangka kerja CSS *utility-first* yang menyediakan kelas-kelas siap pakai untuk membangun antarmuka pengguna secara cepat dan konsisten (Tailwind Labs, 2024). Tidak seperti framework seperti Bootstrap yang menyediakan komponen *pre-styled*, Tailwind memberikan *low-level utility classes* (`flex`, `pt-4`, `text-center`, `bg-green-500`) yang dikomposisikan langsung di HTML untuk membangun desain kustom tanpa meninggalkan *markup*. Dalam sistem ini, Tailwind CSS digunakan untuk menata seluruh antarmuka: *dashboard* admin, form analisis, panel peta, tabel data, serta indikator faktor pembatas—dengan hasil yang responsif di berbagai ukuran layar (desktop, tablet, ponsel).

#### 1.5.7 Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) adalah model kontrol akses yang mengatur hak akses pengguna berdasarkan peran (*role*) yang dimiliki dalam suatu organisasi, bukan berdasarkan identitas individu (Sandhu et al., 1996; Ferraiolo et al., 2001). Dalam model RBAC, *permissions* (izin) dilekatkan ke *role*, bukan langsung ke pengguna. Pengguna kemudian dilekatkan ke satu atau beberapa *role* yang sesuai dengan tanggung jawab dan wewenang mereka. Pendekatan ini menyederhanakan manajemen akses, ter utama pada sistem dengan banyak pengguna, karena administrator hanya perlu mengelola izin pada tingkat *role*, bukan per individu.

Komponen utama RBAC meliputi: (1) **User** — individu yang mengakses sistem; (2) **Role** — peran atau jabatan dalam organisasi yang menentukan tingkat akses; (3) **Permission** — izin untuk melakukan operasi tertentu (membaca, menulis, menghapus); dan (4) **Session** — pemetaan dinamis antara pengguna dan *role* yang akt if pada suatu waktu tertentu. RBAC juga mendukung konsep *role hierarchy*, di mana *role* yang lebih tinggi mewarisi izin dari *role* di bawahnya, serta *separation of duty* (SoD) untuk mencegah konflik kepentingan.

Dalam sistem yang dibangun, konsep RBAC diimplementasikan melalui modul IAM (*Identity and Access Management*) yang menye diakan tiga tingkat akses: **Admin** (akses penuh ke seluruh fungsionalitas), **Tenaga Ahli** (akses terbatas: kelola data master, analisis, dan *Expert Review*), serta **Guest** (hanya melihat peta interaktif). Setiap *role* memiliki himpunan *menu* dan *action* yang berbeda, yang diatur melalui model `UserRole` dan `MenuRole` pada *database*. Pembatasan akses diterapkan baik pada tingkat *view* (melalui *decorator* `@role_required`) maupun tampilan antarmuka, di mana menu navigasi dan tombol aksi disesuaikan secara dinamis berdasarkan *role* pengguna.

#### 1.5.8 Unified Modeling Language (UML)

Unified Modeling Language (UML) merupakan bahasa pemodelan standar yang digunakan untuk memvisualisasikan, merancang, dan mendokumentasikan arsitektur sistem perangkat lunak (Rumbaugh et al., 1999). UML menye diakan sekumpulan notasi grafis yang memung kinkan pengembang untuk mengkomunikasikan rancangan sistem secara jelas dan terstruktur kepada berbagai pemangku kepentingan.

Dalam penel itian ini, beber apa diagram UML digunakan untuk memodelkan sistem yang dibangun, antara lain:

1. **Use Case Diagram** menggambarkan interaksi antara aktor (pengguna) dengan sistem. Aktor dalam sistem ini meliputi Admin, Tenaga Ahli, dan Guest, masing-masing dengan hak akses dan fungsionalitas yang ber beda sesuai perannya.
2. **Activity Diagram** menggambarkan alur kerja proses bisnis utama dalam sistem, khus usnya alur analisis kesesuaian lahan yang melibatkan tahapan pemilihan komoditas, pemilihan layer spasial, eksekusi analisis *FAO Minimum Method* secara *asynchronous* melalui Celery, hingga visual isasi hasil pada peta interaktif.
3. **Class Diagram** menggambarkan struktur statis sistem, termasuk entitas data dan hubungan antar entitas yang tercermin dalam rancangan basis data.

#### 1.5.9 Use Case Diagram

Use Case Diagram adalah salah satu diagram UML yang menggambarkan interaksi antara aktor eksternal (pengguna atau sistem lain) dengan sistem yang sedang dikembangkan (Booch et al., 2005). Diagram ini berfokus pada *apa* yang dilakukan sistem dari perspektif pengguna, bukan *bagaimana* sistem melakukannya. Komponen utama Use Case Diagram meliputi: **aktor** yang merepresentasikan peran pengguna atau sistem eksternal, **use case** yang merepresentasikan fungsionalitas sistem, serta **relasi** (*association*, *include*, *extend*, *generalization*) yang menghubungkan aktor dengan use case.

Dalam sistem yang dibangun, terdapat tiga aktor utama yang berinteraksi dengan sistem. **Admin** memiliki akses penuh terhadap seluruh fungsionalitas: manajemen pengguna dan role (IAM), pengelolaan data master (komoditas, grup, kriteria), manajemen data spasial (unggah, edit, hapus layer), menjalankan analisis kesesuaian lahan, serta mengakses dashboard dan control center. **Tenaga Ahli** memiliki akses terbatas pada pengelolaan data master, menjalankan analisis, memberikan catatan lapangan melalui fitur *Expert Review*, dan melihat dashboard. **Guest** hanya dapat melihat peta interaktif tanpa kemampuan mengubah data atau menjalankan analisis. Pembagian peran ini memastikan keamanan data dan pembagian tanggung jawab yang jelas.

#### 1.5.10 Activity Diagram

Activity Diagram adalah diagram UML yang menggambarkan alur aktivitas atau aliran kerja (*workflow*) dalam suatu proses bisnis atau operasional sistem (Booch et al., 2005). Diagram ini mirip dengan *flowchart* namun memiliki notasi yang lebih kaya, termasuk *swimlane* untuk memisahkan tanggung jawab antar aktor, *fork/join* untuk aliran paralel, dan *decision node* untuk percabangan. Activity Diagram sangat berguna untuk memodelkan logika bisnis yang kompleks dan mengidentifikasi potensi *bottleneck* dalam proses.

Dalam penelitian ini, Activity Diagram digunakan untuk memodelkan alur analisis kesesuaian lahan, yang mencakup beberapa tahapan utama: (1) pengguna memilih satu atau beberapa komoditas dari daftar yang tersedia; (2) pengguna memilih layer spasial target; (3) sistem memvalidasi kelengkapan data dan kriteria kesesuaian; (4) analisis *FAO Minimum Method* dijalankan secara *asynchronous* melalui Celery; (5) pengguna memantau progres melalui Control Center; dan (6) hasil analisis ditampilkan pada peta interaktif dengan kode warna S1–N. Alur ini memungkinkan pengguna untuk memahami setiap langkah yang terjadi dalam sistem, mulai dari *input* hingga *output*.

#### 1.5.11 Class Diagram

Class Diagram adalah diagram UML yang menggambarkan struktur statis sistem dengan menunjukkan kelas-kelas yang membangun sistem, atribut yang dimiliki setiap kelas, metode (operasi), serta hubungan antar kelas seperti *association*, *aggregation*, *composition*, dan *inheritance* (Booch et al., 2005). Class Diagram menjadi landasan utama dalam perancangan basis data berorientasi objek dan sering kali direalisasikan menjadi Entity Relationship Diagram (ERD) untuk sistem berbasis RDBMS.

Dalam sistem yang dibangun, Class Diagram mencerminkan sembilan entitas utama yang dikelompokkan ke dalam tiga modul: (1) modul Master Data — `CommodityGroup`, `Commodity`, `SuitabilityCharacteristic`, dan `DataYear`; (2) modul Spasial — `MasterLayer`, `FeatureData`, dan `ExpertReview`; serta (3) modul Analisis — `SuitabilityAnalysisResult` dan `SuitabilityAnalysisResultPerFeature`. Setiap entitas memiliki hubungan *one-to-many* atau *many-to-one* yang dijaga melalui *foreign key constraint* pada PostgreSQL, dengan *primary key* `id` bertipe `BigAutoField`. Hubungan utama meliputi: satu grup komoditas menaungi banyak komoditas, satu komoditas memiliki banyak kriteria kesesuaian, satu layer spasial berisi banyak fitur geografis, dan satu hasil analisis mencakup banyak poligon.

#### 1.5.12 Black Box Testing

Black Box Testing adalah metode pengujian perangkat lunak yang berfokus pada fungsionalitas eksternal sistem tanpa memperhatikan struktur internal atau kode sumber (Pressman, 2010). Pendekatan ini memperlakukan sistem sebagai "kotak hitam" di mana penguji hanya mengetahui *input* dan *output* yang diharapkan, tanpa mengetahui bagaimana sistem memproses *input* tersebut. Tujuan utama Black Box Testing adalah memastikan bahwa setiap fungsi sistem berjalan sesuai dengan spesifikasi kebutuhan yang telah ditetapkan.

Teknik-teknik yang digunakan dalam Black Box Testing meliputi: (1) **E quivalence Partition ing** — membagi data *input* menjadi kelompok-kelompok yang diharapkan memiliki peril aku serupa; (2) **B oundary Value Analy sis** — menguji nilai-nilai batas (*boundary*) dari setiap kelompok *input*; (3) **De cision Table Tes ting** — menguji kombinasi kond isi dan aksi; serta (4) **St ate Tran sition Tes ting** — menguji per ubahan *state* sistem berdasarkan *event* tertentu. Dalam pene litian ini, Black Box Testing digunakan untuk menguji fungsional itas utama sistem seperti: (a) proses autent ikasi dan manajemen pengguna; (b) oper asi CRUD data master (komod itas, grup, krit eria); (c) unggah dan kelola layer spasial; (d) eksekusi analisis kesesuaian lahan melalui Celery; (e) penambahan dan pengeditan catatan *Expert Review*; serta (f) tampilan dashboard dan peta interakt if. Hasil pengujian divalidasi dengan membandingkan *output* aktual sistem terhadap *output* yang diharapkan berdasarkan sken ario uji.

Beberapa penelitian sebelumnya telah mengkaji integrasi SIG dan analisis kesesuaian lahan dalam berbagai konteks:

Djaenudin et al. (2011) menyusun kriteria kesesuaian lahan untuk berbagai komoditas pertanian di Indonesia. Dokumen ini menjadi acuan utama dalam penentuan parameter dan *threshold* kelas S1–N pada sistem yang dikembangkan. Data dari publikasi ini digunakan sebagai dasar penyusunan tabel kriteria kesesuaian dalam modul *master data* sistem.

Penelitian oleh Wahyudi et al. (2021) melakukan analisis kesesuaian lahan padi meng gunakan metode FAO dan perangkat lunak ArcGIS. Penelitian tersebut berhasil memetakan kelas kesesuaian berdasarkan *overlay* parameter tanah, iklim, dan topografi, namun masih mengandalkan analisis desktop yang tidak dapat diakses secara daring dan memerlukan pengoperasian perangkat lunak SIG secara manual pada setiap tahapan analisis.

Nurhadi et al. (2023) membandingkan teknik klasifikasi tutupan lahan dan dampaknya terhadap evaluasi kesesuaian lahan. Mereka menyoroti pentingnya memasukkan data tutupan lahan *existing* untuk menghindari konflik penggunaan lahan, serta menekankan perlunya validasi hasil analisis dengan kondisi lapangan.

Perbedaan dan kontribusi penelitian ini dibandingkan dengan penelitian terdahulu adalah:

1. **Integrasi DSRM dan RAD:** Penelitian ini meng gunakan *Design Science Research Methodology* (DSRM) sebagai paradigma penel itian dan *Rapid Application Development* (R AD) sebagai metode pengembangan, menghasilkan artefak yang tidak hanya fungsional tetapi juga tervalidasi secara akademik melalui enam tahapan DSRM yang terstruktur.
2. **Fitur Expert Review:** Sistem menye diakan mekanisme validasi hasil analisis oleh tenaga ahli pertanian melalui fitur *Expert Review* yang terintegrasi dalam peta interaktif. Tenaga ahli dapat memberikan catatan lapangan pada setiap poligon hasil analisis, sehingga hasil klasifikasi sistem dapat dibandingkan dengan kondisi aktual di lapangan — fitur yang belum tersedia pada penelitian sebelumnya.
3. **Manajemen Akses Berbasis Role (IAM):** Sistem mengimplementasikan modul IAM dengan tiga tingkat akses pengguna (admin, tenaga ahli, guest) yang membatasi wewenang setiap pengguna sesuai perannya. Menu navigasi dan tombol aksi disesuaikan secara dinamis berdasarkan *role*, menjamin keamanan data dan pembagian tanggung jawab yang jelas.
4. **Arsitektur** ***Asynchronous*** **dan GeoJSON API:** Penggunaan Celery dan Redis untuk pemrosesan analisis secara *background* memungkinkan sistem menangani dataset besar (1.595 unit lahan) tanpa mengorbankan responsivitas antarmuka. Data spasial disajikan langsung melalui GeoJSON API dari Django ke Leaflet.js, menyederhanakan arsitektur dan menghilangkan ketergantungan pada *map server* eksternal.
5. **Implementasi Teknologi Modern:** Sistem dibangun dengan *stack* Django + PostGIS + Celery + Redis + Leaflet + HTMX + Tailwind CSS yang ringan, responsif, dan mudah dikembangkan, berbeda dengan pendekatan berbasis platform desktop atau *framework* berat pada penelitian sebelumnya.

Dengan demikian, penelitian ini melanjutkan kontribusi akademik sebelumnya dengan menghadirkan platform evaluasi kesesuaian lahan yang lebih interaktif, terkomputasi, tervalidasi oleh tenaga ahli, dan dilengkapi manajemen akses yang aman — dari manajemen data hingga visualisasi hasil analisis.
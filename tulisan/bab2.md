Bab 2 
Tinjauan Pustaka
•	2.1 Kesesuaian Lahan Pertanian 
•	2.1.1 Konsep Kesesuaian Lahan 
•	Kesesuaian lahan (land suitability) adalah sebuah konsep fundamental dalam perencanaan dan manajemen sumberdaya lahan. Secara umum, kesesuaian lahan didefinisikan sebagai tingkat kecocokan sebuah unit lahan untuk penggunaan tertentu, dalam hal ini untuk budidaya tanaman pertanian, tanpa menyebabkan kerusakan yang permanen pada lahan tersebut (FAO, 1976). Konsep ini bertujuan untuk mencocokkan (matching) karakteristik dan kualitas lahan dengan persyaratan yang dibutuhkan oleh sebuah jenis tanaman agar dapat tumbuh dan berproduksi secara optimal. 
•	Analisis kesesuaian lahan tidak hanya mengevaluasi apakah suatu tanaman dapat hidup di suatu lokasi, tetapi juga seberapa baik tanaman tersebut akan berperforma. Hasil dari evaluasi ini biasanya diklasifikasikan ke dalam beberapa kelas, seperti Sangat Sesuai (S1), Cukup Sesuai (S2), Sesuai Marjinal (S3), dan Tidak Sesuai (N). Klasifikasi ini menjadi dasar untuk pengambilan keputusan dalam menentukan komoditas pertanian yang paling menguntungkan dan berkelanjutan untuk suatu wilayah. 
•	2.1.2 Kriteria dan Parameter Penilaian 
•	Penilaian kesesuaian lahan dalam penelitian ini melibatkan analisis multi-parameter yang sistematis, mencakup tiga kriteria utama: karakteristik tanah, iklim, dan topografi, serta ditambah dengan kriteria tutupan lahan existing. Setiap kriteria ini diwakili oleh indikator atau parameter spesifik yang nilainya akan dievaluasi untuk menentukan kelas kesesuaian. Berdasarkan data yang tersedia, parameter-parameter yang digunakan adalah sebagai berikut: 
•	1. Parameter Tanah 
•	Merupakan faktor fisik dan kimia yang secara langsung mempengaruhi pertumbuhan akar dan ketersediaan nutrisi bagi tanaman. Dalam sistem ini, parameter tanah menjadi kriteria penilaian utama dan meliputi: 
•	Tekstur Tanah: Komposisi partikel pasir, debu, dan liat yang mempengaruhi kemampuan tanah menahan air (kapasitas retensi air) dan aerasi. Dalam data, ini direpresentasikan oleh atribut TEKSTUR (misalnya: sandy loam) dan KTG_TXTR (misalnya: Agak Kasar).
•	pH Tanah: Tingkat keasaman atau kebasaan tanah yang sangat menentukan ketersediaan nutrisi bagi tanaman. Nilai pH (PH_NILAI) dan kelas kritikalnya (PH_KRIT, misalnya: Agak Masam Bawah) menjadi input penting dalam evaluasi.
•	Kesuburan Tanah: Merupakan indikator ketersediaan hara esensial. Parameter ini mencakup:
•	Unsur Hara Makro: Nilai dari Nitrogen (N_NILAI), Fosfor (P_NILAI), dan Kalium (K_NILAI).
•	Karbon Organik (C-Organik): (CORG_NILAI) sebagai indikator kandungan bahan organik tanah yang vital untuk kesuburan dan struktur tanah.
•	Kemampuan Tukar Kation (KTK): (KTK_NILAI) yang menunjukkan kemampuan tanah dalam menahan dan melepas nutrisi bagi tanaman.
•	Drainase: Kemampuan tanah untuk mengalirkan kelebihan air, yang terkait dengan tekstur dan struktur tanah. Parameter ini direpresentasikan oleh atribut DRAINASE (misalnya: sedang).
•	Kedalaman Tanah Efektif: (Kdl_tanah atau DALAM_TNH) adalah ketebalan lapisan tanah yang dapat ditembus oleh akar tanaman, yang sangat mempengaruhi pertumbuhan vegetatif.
•	Kerikilan/Batuan: Persentase atau kelas kerikilan dan batuan di dalam profil tanah (BATUAN_NIL dan BATUAN_KRI) yang dapat menghambat perkembangan akar dan pengolahan lahan.
•	Berat Volume Tanah (Bulk Density): (BD_NILAI) adalah ukuran kepadatan massa tanah yang mempengaruhi pertumbuhan akar dan infiltrasi air.
•	2. Parameter Iklim 
•	Merupakan faktor lingkungan yang tidak dapat dikendalikan dan memiliki pengaruh global terhadap pertumbuhan tanaman. Data iklim untuk sistem ini diperoleh dari stasiun pengamatan iklim terdekat, yang dalam contoh data ini adalah STASIUN "Tanete Riaja". Parameter iklim utama yang digunakan meliputi: 
•	Curah Hujan: Jumlah dan distribusi hujan sepanjang tahun yang menentukan ketersediaan air untuk tanaman. Data ini biasanya berupa nilai rata-rata tahunan.
•	Suhu Udara: Suhu rata-rata harian atau bulanan yang mempengaruhi laju metabolisme dan fase pertumbuhan tanaman.
•	3. Parameter Topografi 
•	Merupakan karakteristik permukaan bumi yang mempengaruhi kondisi mikro iklim dan manajemen lahan. Parameter topografi yang digunakan dalam penelitian ini adalah: 
•	Kemiringan Lereng: Persentase kemiringan lahan yang direpresentasikan oleh atribut KL (misalnya: 25-45%). Parameter ini sangat mempengaruhi potensi erosi, drainase permukaan, dan kemudahan penggunaan alat pertanian.
•	4. Parameter Tutupan dan Penggunaan Lahan 
•	Meskipun bukan karakteristik fisik lahan, informasi mengenai penggunaan lahan saat ini memberikan konteks yang penting untuk evaluasi. 
•	Penggunaan Lahan: Jenis tutupan atau penggunaan lahan yang ada, seperti yang tercantum dalam atribut GUNA_LAHAN (misalnya: hutan lahan kering). Informasi ini penting untuk menilai tingkat konversi yang diperlukan dan potensi dampak lingkungan.
•	Vegetasi: Jenis vegetasi yang dominan tumbuh di lokasi, seperti yang dicatat dalam VEGETASI (misalnya: kemiri, areng), dapat menjadi indikator karakteristik ekologis lahan.
•	2.1.3 Metode Analisis Kesesuaian Lahan 
•	Metode yang paling diakui secara internasional untuk analisis kesesuaian lahan adalah kerangka kerja yang dikembangkan oleh Food and Agriculture Organization (FAO). Metode ini bersifat sistematis dan komprehensif, melibatkan dua tahapan utama: (1) identifikasi persyaratan tumbuh tanaman (crop requirements) dan (2) evaluasi karakteristik lahan (land characteristics). Kesesuaian lahan ditentukan dengan membandingkan kedua hal tersebut. 
•	Prosesnya dimulai dengan menentukan kriteria ideal untuk setiap jenis tanaman. Selanjutnya, data lahan aktual (tanah, iklim, topografi) dikumpulkan dan dievaluasi terhadap kriteria ideal tersebut. Setiap parameter diberi bobot dan tingkat kesesuaiannya. Hasil akhirnya adalah peta kesesuaian lahan yang menggambarkan kelas kesesuaian untuk setiap unit lahan. Metode ini menjadi landasan logis bagi pengembangan algoritma dalam sistem yang akan dibangun, di mana komputer akan melakukan proses pencocokan data secara otomatis. 
•	2.1.4 Pentingnya Kesesuaian Lahan 
•	Melaksanakan analisis kesesuaian lahan sebelum melakukan budidaya memiliki manfaat strategis, antara lain: 
•	Meningkatkan Produktivitas: Menanam jenis tanaman yang paling sesuai akan memaksimalkan hasil panen.
•	Efisiensi Ekonomi: Mengurangi risiko kegagalan panen dan penggunaan input pertanian (pupuk, pestisida) yang tidak perlu.
•	Keberlanjutan Lingkungan: Mencegah degradasi lahan seperti erosi dan penurunan kesuburan yang disebabkan oleh penggunaan lahan yang tidak tepat.
•	Dasar Perencanaan: Menjadi acuan bagi pemerintah dalam menyusun program pertanian regional dan kebijakan ketahanan pangan.
•	2.2 Sistem Informasi Geografis (SIG) 
•	2.2.1 Konsep Dasar SIG 
•	Sistem Informasi Geografis (Geographic Information System - GIS) adalah sebuah sistem komputer yang dirancang untuk mengumpulkan, menyimpan, menganalisis, dan menampilkan data yang memiliki referensi geografis atau spasial. Berbeda dengan sistem informasi biasa yang hanya menangani data atribut (misalnya nama dan alamat), SIG mampu menghubungkan data atribut tersebut dengan lokasi di permukaan bumi (koordinat x, y, atau bahkan z). Kemampuan inilah yang membuat SIG menjadi alat yang sangat kuat untuk analisis spasial. 
•	Komponen utama SIG terdiri dari perangkat keras (hardware), perangkat lunak (software), data, manusia (pengguna), dan metode. Dalam konteks penelitian ini, perangkat lunak berupa aplikasi web yang akan dikembangkan, data berupa peta dan parameter lahan, dan manusia adalah para pengguna seperti petani dan penyuluh. 
•	2.2.2 SIG Berbasis Web (WebGIS) 
•	Perkembangan teknologi internet melahirkan konsep SIG Berbasis Web (WebGIS). WebGIS adalah evolusi dari SIG desktop tradisional yang memungkinkan fungsi-fungsi SIG diakses dan digunakan melalui peramban web (web browser). Implementasi WebGIS mengubah cara informasi geospasial didistribusikan dan diakses, dari model yang terpusat dan memerlukan perangkat lunak mahal menjadi model yang terbuka, mudah diakses, dan kolaboratif. 
•	Keunggulan utama WebGIS yang menjadi dasar pengembangan sistem ini adalah: 
•	Aksesibilitas Tinggi: Pengguna tidak perlu menginstal perangkat lunak SIG khusus; mereka hanya memerlukan peramban web dan koneksi internet. Ini menjawab tantangan aksesibilitas data spasial bagi berbagai kalangan.
•	Distribusi Informasi Cepat: Hasil analisis dan peta dapat dengan mudah dibagikan kepada banyak pemangku kepentingan secara simultan melalui sebuah URL.
•	Platform Independen: Sistem dapat diakses dari berbagai perangkat (desktop, tablet, ponsel) dan sistem operasi.
•	Pembaruan Data Terpusat: Data dan analisis dikelola di satu server, memastikan semua pengguna mendapatkan informasi yang paling mutakhir.
•	2.2.3 Arsitektur dan Teknologi WebGIS 
•	Sistem WebGIS umumnya mengadopsi arsitektur client-server. Dalam arsitektur ini, terdapat beberapa komponen teknologi yang bekerja sama: 
•	Client Side (Frontend): Merupakan antarmuka yang berinteraksi langsung dengan pengguna. Komponen ini bertugas untuk menampilkan peta, menerima input dari pengguna (seperti memilih lokasi atau parameter), dan mengirimkan permintaan ke server. Untuk keperluan ini, pustaka JavaScript seperti Leaflet sangat populer digunakan karena kemudahannya dalam menampilkan peta interaktif di halaman web. Antarmuka pengguna (UI) itu sendiri dapat dibangun dengan kerangka kerja CSS seperti Tailwind CSS dan diperkaya dengan interaksi dinamis menggunakan HTMX.
•	Server Side (Backend): Merupakan otak dari aplikasi yang berjalan di server. Backend memproses permintaan dari client, menjalankan logika bisnis (seperti algoritma kesesuaian lahan), mengakses database, dan mengembalikan data yang diperlukan. Django dengan Django REST Framework adalah pilihan yang ideal untuk membangun backend yang kuat, aman, dan menyediakan API (Application Programming Interface) yang efisien untuk komunikasi dengan frontend.
•	Database Spasial: Untuk menyimpan data geografis (peta) dan data atribut secara terintegrasi, diperlukan database yang mendukung tipe data spasial. PostgreSQL dengan ekstensi PostGIS adalah standar industri untuk keperluan ini. PostGIS menyediakan fungsi-fungsi canggih untuk query dan analisis data spasial secara langsung dari database, yang sangat efisien untuk aplikasi seperti ini.
•	Server Peta (Map Server): Untuk aplikasi dengan data spasial yang kompleks dan luas, sering kali digunakan server peta khusus seperti GeoServer atau QGIS Server. Server ini bertugas melayani data peta dalam format standar web seperti WMS (Web Map Service) untuk gambar peta dan WFS (Web Feature Service) untuk data vektor mentah. Penggunaan server peta memisahkan beban rendering peta dari server aplikasi utama, sehingga meningkatkan performa dan skalabilitas secara keseluruhan.


### 2.3 Sistem Rekomendasi

Sistem rekomendasi adalah perangkat lunak yang bertujuan menampilkan saran atau rekomendasi kepada pengguna berdasarkan analisis data dan preferensi tertentu. Secara umum ada tiga pendekatan besar:

1. **Content-based filtering**: sistem menilai kesamaan antara item (misalnya, jenis tanaman) berdasarkan atributnya, lalu merekomendasikan item serupa kepada pengguna.
2. **Collaborative filtering**: rekomendasi didasarkan pada pola perilaku atau penilaian pengguna lain yang serupa (menggunakan teknik seperti user-user atau item-item similarity).
3. **Knowledge-based (rule-based)**: sistem menggunakan aturan eksplisit atau pengetahuan domain untuk menghasilkan rekomendasi. Aturan ini biasanya dikodekan oleh ahli domain dan tidak bergantung pada data historis pengguna.

Untuk analisis kesesuaian lahan, pendekatan knowledge-based lebih sesuai karena kebutuhan rekomendasi didasarkan pada kombinasi kriteria fisik, iklim, dan topografi yang sudah ditetapkan oleh ahli agronomi. Data spasial dan parametrik yang dimiliki memungkinkan penyusunan aturan ('if-then') yang memetakan kelas kesesuaian lahan ke jenis-jenis tanaman tertentu. Dengan begitu, sistem dapat memberikan rekomendasi komoditas pertanian yang paling potensial untuk setiap unit lahan menurut klasifikasi S1–N.

Sebagai contoh, aturan sederhana dapat berbunyi:

> Jika kelas kesesuaian lahan untuk padi adalah S1 dan penggunaan lahan saat ini bukan kawasan konservasi, maka rekomendasikan padi.

Aturan yang lebih kompleks menggabungkan beberapa parameter sekaligus, seperti pH, ketersediaan air, dan kemiringan lereng. Rekomendasi tidak hanya bersifat teknis, tetapi juga dapat mencakup aspek ekonomis atau lingkungan dengan menambahkan bobot/batasan tambahan ke dalam aturan.

Penggunaan sistem rekomendasi dalam konteks pertanian telah terbukti membantu petani memilih tanaman, teknologi budidaya, dan sumber daya lain secara lebih sistematis. Dalam sistem yang dikembangkan untuk penelitian ini, WebGIS menjadi antarmuka bagi pengguna untuk memperoleh rekomendasi berbasis lokasi serta melihat peta kesesuaian secara visual.

### 2.4 Framework Django dan Pustaka Pendukung

Pemilihan kerangka kerja dan pustaka teknis pada sistem ini didasarkan pada kebutuhan akan platform yang stabil, mudah dikembangkan, dan mendukung operasi spasial.

- **Django**: Sebagai web framework Python yang sudah matang, Django menyediakan struktur MVC (Model-View-Controller) yang kuat, ORM untuk interaksi basis data, serta sistem autentikasi dan administrasi bawaan. Keunggulannya termasuk dokumentasi lengkap, komunitas besar, dan dukungan terhadap aplikasi berskala menengah hingga besar.

- **GeoDjango**: Ekstensi Django untuk pengembangan aplikasi GIS. GeoDjango mempermudah definisi model spasial, query spasial, dan integrasi dengan database PostGIS. Fitur-fitur seperti field `PointField`, `PolygonField`, serta fungsi-fungsi geometris (jarak, tumpang tindih) sangat membantu dalam menangani data peta dan analisis kesesuaian.

- **Django REST Framework (DRF)**: Menyediakan alat untuk membangun API RESTful. Sistem menggunakan API agar frontend (JavaScript/HTMX) dapat berkomunikasi secara asinkron dengan backend. DRF membuat serialisasi data, autentikasi token, dan dokumentasi API menjadi mudah.

- **Leaflet**: Pustaka JavaScript ringan untuk menampilkan peta interaktif. Leaflet mendukung berbagai penyedia tile, vektor, serta event interaksi seperti klik dan zoom. Dalam sistem, peta Leaflet menampilkan layer kesesuaian lahan, batas administratif, dan hasil rekomendasi.

- **HTMX**: Library yang memungkinkan elemen HTML berinteraksi dengan server menggunakan atribut sederhana (`hx-get`, `hx-post`, dll.). HTMX mempercepat pembangunan antarmuka dinamis tanpa memerlukan kerangka kerja JavaScript yang besar, sehingga menjaga kesederhanaan dan performa.

- **Tailwind CSS**: Kerangka kerja CSS utility-first yang memudahkan penataan tampilan responsif dengan kelas-kelas siap pakai. Tailwind memungkinkan pembuatan antarmuka yang konsisten tanpa menulis banyak CSS kustom.

- **PostgreSQL + PostGIS**: Database relasional dengan ekstensi spasial. PostGIS menyimpan data geometri dan menyediakan operasi spasial langsung dalam query SQL, seperti `ST_Intersects`, `ST_Buffer`, dan `ST_Area`. Hal ini mempercepat pengolahan data peta dan perhitungan kesesuaian.

Secara keseluruhan, kombinasi teknologi ini menghasilkan arsitektur client-server yang modular: frontend ringan berbasis HTML/HTMX/Tailwind/Leaflet, backend Python/Django/DRF/GeoDjango, dan penyimpanan data pada PostgreSQL/PostGIS. Desain ini mendukung pemeliharaan yang mudah, skalabilitas, serta interoperabilitas data spasial.

### 2.5 Penelitian Terdahulu

Kajian literatur menunjukkan beberapa penelitian dan aplikasi serupa yang mengintegrasikan SIG dan analisis kesesuaian lahan, baik untuk tujuan pertanian, kehutanan, maupun penggunaan lahan lainnya. Di antaranya:

- Studi oleh Wahyudi et al. (2021) yang melakukan analisis kesesuaian lahan padi di Kabupaten X menggunakan metode FAO dan software ArcGIS. Mereka memetakan kelas kesesuaian dan memberikan rekomendasi berbasis overlay parameter-parameter tanah, iklim, dan topografi.
- Tugas akhir oleh Sari (2022) mengembangkan sistem WebGIS sederhana untuk kesesuaian lahan jagung, memanfaatkan GeoServer sebagai server peta dan OpenLayers sebagai frontend. Rekomendasi disajikan dalam bentuk peta interaktif, tetapi logika rekomendasi belum diotomasi dan masih memerlukan analisis manual.
- Penelitian oleh Nurhadi et al. (2023) yang membandingkan beberapa teknik klasifikasi untuk peta tutupan lahan dan dampaknya terhadap kesesuaian lahan. Mereka juga menyoroti pentingnya memasukkan data tutupan lahan existing untuk menghindari konflik penggunaan lahan.

Beberapa perbedaan dan keunggulan sistem pada penelitian ini dibandingkan karya terdahulu adalah:

- Otomatisasi logika rekomendasi menggunakan kerangka rule-based yang diintegrasikan ke dalam backend, sehingga pengguna dapat memperoleh saran secara instan tanpa analisis manual.
- Penggunaan teknologi WebGIS modern (Leaflet, HTMX, Tailwind) untuk antarmuka yang lebih ringan dan responsif dibandingkan dengan sistem yang bergantung pada plugin berat.
- Pemanfaatan database spasial PostGIS secara penuh untuk perhitungan kesesuaian, sehingga analisis dapat dilakukan langsung di sisi server dengan query yang efisien.
- Struktur kode berbasis Django yang memudahkan pengembangan lanjut dan integrasi dengan modul lain seperti manajemen master data dan tugas analisis yang berjalan terjadwal.

Dengan demikian, penelitian ini melanjutkan warisan akademik sebelumnya dan menambahkan kontribusi berupa platform rekomendasi lahan yang lebih interaktif, otomatis, dan berbasis web.


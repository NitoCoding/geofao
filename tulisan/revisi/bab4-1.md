## BAB V
## KESIMPULAN DAN SARAN

### 5.1 Kesimpulan

Berdasarkan hasil penelitian dan pengembangan yang telah dilakukan menggunakan kerangka kerja *Design Science Research Methodology* (DSRM) dengan pendekatan *Rapid Application Development* (RAD), dapat ditarik kesimpulan sebagai berikut:

1. Penelitian ini berhasil mengidentifikasi permasalahan utama dalam evaluasi kesesuaian lahan pertanian di Kabupaten Barru, yaitu belum tersedianya sistem terintegrasi yang mampu mengklasifikasikan kesesuaian lahan secara otomatis berdasarkan parameter tanah dan kriteria FAO. Melalui tahap *Problem Identification & Motivation* dan *Define Objectives of a Solution* pada DSRM, dirumuskan kebutuhan fungsional dan non-fungsional sistem yang menjadi acuan pengembangan.

2. Sistem Informasi Kesesuaian Lahan Pertanian berbasis WebGIS berhasil dikembangkan melalui enam sprint RAD yang mencakup: (1) setup environment dan modul IAM, (2) manajemen data master, (3) manajemen data spasial, (4) modul analisis kesesuaian lahan, (5) peta interaktif dan expert review, serta (6) dashboard, finalisasi, dan pengujian. Sistem dibangun dengan arsitektur Django, PostgreSQL + PostGIS untuk penyimpanan data geospasial, Celery + Redis untuk pemrosesan asynchronous, dan Leaflet.js untuk visualisasi peta interaktif.

3. Algoritma *FAO Minimum Method* berhasil diimplementasikan untuk menentukan kelas kesesuaian lahan (S1, S2, S3, N) secara otomatis berdasarkan prinsip *Law of the Minimum*, di mana kelas kesesuaian akhir ditentukan oleh parameter dengan nilai terburuk. Validasi melalui test case menunjukkan bahwa hasil klasifikasi sistem konsisten dengan perhitungan manual menggunakan tabel kriteria FAO, tanpa ditemukan selisih dalam penentuan kelas.

4. Sistem menyediakan tiga tingkat akses pengguna melalui modul IAM: admin untuk pengelolaan data dan analisis, tenaga ahli untuk validasi lapangan melalui fitur *Expert Review*, dan guest untuk melihat data. Fitur *Expert Review* memungkinkan tenaga ahli pertanian memberikan catatan lapangan pada setiap poligon hasil analisis sebagai pembanding hasil kalkulasi sistem, dengan unique constraint yang memastikan satu ahli hanya memberikan satu catatan per poligon.

5. Hasil pengujian *black box* terhadap 47 test case pada tujuh modul (autentikasi, manajemen pengguna, data master, layer spasial, analisis kesesuaian lahan, peta interaktif, dan expert review) menunjukkan tingkat keberhasilan 100%. Pengujian performa menunjukkan waktu respons 0,12 detik untuk query fitur tunggal dan 5,28 detik untuk analisis 1.595 fitur secara asynchronous, dengan penggunaan CPU maksimal 55% dan memori 680 MB dari 12 GB yang tersedia. Seluruh kebutuhan non-fungsional — performa, keamanan, kompatibilitas multi-platform, dan maintainability — telah terpenuhi sesuai target yang ditetapkan.

### 5.2 Saran

Berdasarkan hasil penelitian dan keterbatasan yang teridentifikasi selama pengembangan, beberapa saran untuk pengembangan selanjutnya adalah sebagai berikut:

1. **Integrasi Data Iklim Dinamis** — Data curah hujan dan parameter iklim lainnya saat ini diinput secara manual. Pengembangan selanjutnya dapat mengintegrasikan API cuaca atau data satelit (misalnya BMKG, CHIRPS) untuk memperbarui parameter iklim secara berkala dan meningkatkan akurasi analisis.

2. **Peningkatan Skalabilitas** — Performa sistem menurun secara linear untuk dataset di atas 5.000 fitur. Disarankan penerapan *chunking* dan *parallel processing* pada Celery worker, serta migrasi ke infrastruktur cloud untuk menangani volume data yang lebih besar.

3. **Validasi Geometri Otomatis** — Shapefile dengan geometri invalid (misalnya *self-intersecting polygon*) dapat menyebabkan error saat pemrosesan. Perlu ditambahkan pre-processing otomatis menggunakan `ST_MakeValid` atau `ogr2ogr` sebelum data disimpan ke PostGIS.

4. **Pengembangan Mobile** — Mengingat kebutuhan akses di lapangan, disarankan pengembangan aplikasi mobile atau Progressive Web App (PWA) dengan kemampuan offline syncing agar tenaga ahli dapat memberikan catatan lapangan langsung dari lokasi tanpa ketergantungan pada koneksi internet.

5. **Eksplorasi Metode Hybrid** — Penelitian lanjutan dapat mengeksplorasi kombinasi *FAO Minimum Method* dengan pendekatan *machine learning* (misalnya memanfaatkan data historis hasil panen) untuk memperkaya rekomendasi kesesuaian lahan.

6. **Studi Lapangan Jangka Panjang** — Disarankan evaluasi dampak penggunaan sistem terhadap produktivitas dan keberlanjutan lahan pertanian di Kabupaten Barru dalam studi lapangan jangka panjang, serta perbandingan efektivitas dengan pendekatan evaluasi lahan konvensional.

### Daftar Pustaka

- Djaenudin, D., Marwan, H., Subagjo, H., & Hidayat, A. (2011). *Petunjuk Teknis Evaluasi Lahan untuk Komoditas Pertanian*. Balai Besar Penelitian dan Pengembangan Sumberdaya Lahan Pertanian, Bogor.
- Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design Science in Information Systems Research. *MIS Quarterly*, 28(1), 75–105.
- Kendall, K. E., & Kendall, J. E. (2020). *Systems Analysis and Design* (10th ed.). Pearson.
- Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A Design Science Research Methodology for Information Systems Research. *Journal of Management Information Systems*, 24(3), 45–77.
- FAO. (1976). *A Framework for Land Evaluation*. FAO Soils Bulletin No. 32. Rome: Food and Agriculture Organization of the United Nations.
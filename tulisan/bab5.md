Bab 5  
Kesimpulan dan Saran

### 5.1 Kesimpulan
Berdasarkan analisis dan pengembangan yang dilakukan, dapat ditarik beberapa kesimpulan utama:

1. Sistem WebGIS yang dikembangkan berhasil menerapkan konsep kesesuaian lahan FAO dan menyediakan antarmuka interaktif bagi pengguna untuk memasukkan data spasial dan parameter lahan.
2. Algoritma rule‑based mampu menentukan kelas kesesuaian (S1–N) secara otomatis dan menghasilkan rekomendasi tanaman yang konsisten dengan kriteria agronomi; ini menjawab rumusan masalah terkait otomatisasi rekomendasi.
3. Implementasi teknologi Django, GeoDjango, Leaflet, HTMX, dan PostGIS terbukti memenuhi kebutuhan fungsional dan non‑fungsional, termasuk performa (<2 detik respon) serta aksesibilitas via browser.
4. Pengujian black box dan umpan balik pengguna menunjukkan bahwa sistem mudah digunakan oleh petani/penyuluh dan memberikan informasi yang berguna untuk pengambilan keputusan budidaya.

### 5.2 Saran
Beberapa rekomendasi untuk pengembangan selanjutnya dan penelitian lanjut:

- **Integrasi Data Dinamis**: tambahkan modul pengambilan data iklim real‑time dari API cuaca untuk meningkatkan akurasi analisis.
- **Skalabilitas dan Cloud**: migrasi ke infrastruktur cloud (mis. AWS/GCP) serta penggunaan load‑balancer untuk menangani volume data yang lebih besar.
- **Fitur Mobile Offline**: kembangkan aplikasi mobile dengan kemampuan offline syncing agar petani di daerah tanpa koneksi dapat tetap menggunakan sistem.
- **Kombinasi Metode Rekomendasi**: eksplorasi hybrid antara rule‑based dan machine learning (misalnya memanfaatkan data historis hasil panen) untuk memperkaya rekomendasi.
- **Penelitian Lanjutan**: evaluasi dampak penggunaan sistem terhadap produktivitas dan keberlanjutan lahan dalam studi lapangan jangka panjang, serta bandingkan dengan pendekatan manual.

Dengan pengembangan ini, sistem diharapkan dapat menjadi alat yang lebih canggih dan bermanfaat bagi manajemen lahan pertanian berkelanjutan.

### Daftar Pustaka

- Djaenudin, A., et al. (2011). *Analisis Kesesuaian Lahan*. SlideShare. Data dari halaman 47–48. https://www.slideshare.net/slideshow/djaenudin-et-al-2011/80437932#48
- “Kesesuaian Lahan untuk Pertanaman” (pdf). Neliti. https://media.neliti.com/media/publications/101338-none-e82914ba.pdf
- “Evaluasi Kesesuaian Lahan Pertanaman Padi” (pdf). Neliti. https://media.neliti.com/media/publications/233040-evaluasi-kesesuaian-lahan-pertanaman-pad-925b2d2a.pdf
- Abdul Rahman, J. (tahun?). *Jordy LP* [file lokal]. file:///C:/Users/LENOVO/Downloads/jordy_lp,+publish_Abdul+Rahman_119-126.pdf

(Referensi di atas digunakan sebagai sumber teori dan kajian penelitian terdahulu dalam Bab 2 dan Bab 4.)

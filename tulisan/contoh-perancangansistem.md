2.8 Perancangan Sistem
Perancangan sistem merupakan aktivitas teknis yang bertujuan mentransformasikan spesifikasi kebutuhan yang telah dideklarasikan ke dalam bentuk model visual terstruktur yang siap diimplementasikan ke dalam baris kode pemrograman komputer. Pemodelan sistem dalam penelitian rancang bangun ini memanfaatkan standar notasi Unified Modeling Language (UML) dan Entity Relationship Diagram (ERD).
2.8.1 Use Case Diagram

Gambar 3. Use case diagram SIPLK
      Use Case Diagram merupakan diagram perilaku dalam notasi Unified Modeling Language (UML) yang berfungsi untuk memodelkan interaksi antara aktor eksternal dengan fungsionalitas sistem dari perspektif pengguna. Sebagaimana didefinisikan oleh Pressman dan Maxim (2020), setiap use case merepresentasikan satu unit fungsionalitas yang bernilai bagi aktor dan dapat diamati sebagai perilaku yang koheren dari sistem. Dalam konteks perancangan sistem SIPLK, use case diagram digunakan untuk mendefinisikan, memvalidasi, dan mengomunikasikan kebutuhan fungsional kepada seluruh pemangku kepentingan, baik teknis maupun non-teknis (Sommerville, 2016). Sistem SIPLK melibatkan lima aktor dengan hierarki peran yang mencerminkan struktur organisasi PT. Trakindo Utama. Relasi generalisasi (generalization) antar aktor menggambarkan bahwa aktor dengan peran lebih tinggi mewarisi kapabilitas aktor dengan peran lebih rendah. Relasi <<include>> digunakan untuk use case yang wajib dieksekusi sebagai prasyarat, sedangkan relasi <<extend>> digunakan untuk use case yang bersifat opsional berdasarkan kondisi tertentu. Prinsip least privilege diterapkan secara konsisten, di mana peran Viewer hanya memiliki akses baca-saja sesuai kebutuhan keamanan dan pengendalian informasi kontrak perusahaan.
      Dalam sistem SIPLK yang dikembangkan, terdapat lima aktor utama yang berinteraksi dengan sistem:
1.	Admin (Administrator) — Pengelola utama sistem dengan kontrol penuh terhadap seluruh fungsionalitas dan akses ke seluruh folder area.
2.	Manager — Pengambil keputusan tingkat menengah/atas yang bertanggung jawab atas persetujuan tingkat lanjut dan penghentian kontrak aktif.
3.	Supervisor — Penanggung jawab operasional yang melakukan peninjauan awal terhadap kontrak yang diajukan.
4.	Staff — Pelaksana operasional yang membuat dan mengelola draf kontrak serta menyusun dokumen.
5.	Viewer — Pengguna dengan akses baca-saja (read-only) yang dapat memantau status kontrak dan dasbor analitik.

Use Case utama yang terdapat dalam sistem meliputi:
a. Use Case Manajemen Pengguna
	Menambah pengguna baru (Admin).
	Menghapus pengguna (Admin).
	Mengatur hak akses folder pengguna (Admin).
b. Use Case Manajemen Kontrak
	Membuat kontrak baru dengan mengunggah PDF (Admin, Staff).
	Mengedit metadata kontrak berstatus Draft (Admin, Staff pemilik).
	Mengajukan kontrak untuk ditinjau (Admin, Staff).
	Menyetujui atau menolak kontrak (Admin, Manager, Supervisor).
	Menghentikan kontrak aktif (Admin, Manager).
	Melihat detail dan riwayat kontrak (Semua peran).
	Mengunduh dokumen kontrak bertanda air (Admin, Manager, Supervisor).
c. Use Case Penulisan Dokumen
	Membuat dokumen baru dari templat atau dokumen kosong (Admin, Staff).
	Menyunting dokumen dengan penyunting teks kaya (Admin, Staff).
	Menyimpan dan memulihkan versi dokumen (Admin, Staff).
	Memfinalisasi dokumen menjadi kontrak (Admin, Staff).
d. Use Case Manajemen Templat dan Pustaka Pasal
	Membuat, mengedit, dan menghapus templat (Admin).
	Membuat, mengedit, dan menghapus pasal pustaka (Admin).
e. Use Case Pemantauan dan Analitik
	Memantau kewajiban kontraktual (Admin, Manager, Supervisor, Staff).
	Menandai kewajiban sebagai selesai (Admin, Manager, Supervisor, Staff).
	Mengakses dasbor analitik (Semua peran).
	Mengimpor data analitik (Admin, Manager).
f. Use Case Keamanan dan Audit
	Melihat log audit aktivitas (Admin, Manager, Supervisor).
	Autentikasi pengguna (Semua peran).
	Keluar dari sistem (Semua peran).

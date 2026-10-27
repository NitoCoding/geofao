3.7	Evaluasi
Tahap kelima DSR adalah evaluasi untuk mengukur seberapa baik artefak mendukung solusi terhadap masalah. Evaluasi dilakukan menggunakan metode Black-box Testing untuk memverifikasi fungsionalitas sistem.
3.7.1	Pengujian Halaman Login
Tabel 37. Hasil Pengujian Halaman Login
Skenario	Test Case	Hasil Diharapkan	Hasil	Kesimpulan
Mengosongkan username dan password	Username: (kosong), Password: (kosong)	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
Mengisi username yang salah	Username: wronguser, Password: admin123	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
Mengisi password yang salah	Username: admin, Password: wrongpass	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
Mengisi data dengan benar	Username: admin, Password: admin123	Sistem menerima dan mengarahkan ke dashboard	Sesuai Harapan	Valid
3.7.2	Pengujian Manajemen Pengguna (Koordinator)
Tabel 38. Hasil Pengujian Manajemen Pengguna
No	Skenario	Test Case	Hasil Diharapkan	Hasil	Kesimpulan
1	Menambah pengguna baru	Mengisi semua field dengan data valid	Data pengguna tersimpan dan muncul di daftar	Sesuai Harapan	Valid
2	Menambah pengguna duplikat	Username: admin (sudah ada)	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
3	Mengedit data pengguna	Mengubah nama lengkap pengguna	Data pengguna berhasil diperbarui	Sesuai Harapan	Valid
4	Menghapus pengguna	Klik hapus dan konfirmasi	Data pengguna berhasil dihapus	Sesuai Harapan	Valid
3.7.3	Pengujian Input Nilai (Asisten)
Tabel 39. Hasil Pengujian Input Nilai
Skenario	Test Case	Hasil Diharapkan	Hasil	Kesimpulan
Menginput nilai valid	Nilai: 85	Nilai berhasil disimpan	Sesuai Harapan	Valid
Menginput nilai > 100	Nilai: 150	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
Menginput format salah	Nilai: abc	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
Mengubah nilai	Mengubah dari 85 menjadi 90	Nilai berhasil diperbarui	Sesuai Harapan	Valid
3.7.4	Pengujian Melihat Nilai (Mahasiswa)
Tabel 40. Hasil Pengujian Melihat Nilai
Skenario Pengujian	Test Case	Hasil yang Diharapkan	Hasil Pengujian	Kesimpulan
Melihat daftar nilai praktikum	Klik menu nilai	Sistem menampilkan daftar nilai praktikum	Sesuai Harapan	Valid
Filter nilai berdasarkan mata kuliah	Pilih mata kuliah tertentu	Sistem menampilkan nilai sesuai filter	Sesuai Harapan	Valid
Melihat detail nilai	Klik detail pada salah satu nilai	Sistem menampilkan rincian komponen nilai	Sesuai Harapan	Valid
3.7.5	Pengujian Kehadiran
Tabel 41. Hasil Pengujian Kehadiran
Skenario Pengujian	Test Case	Hasil yang Diharapkan	Hasil Pengujian	Kesimpulan
Mencatat kehadiran mahasiswa	Status: Hadir	Data kehadiran tersimpan	Sesuai Harapan	Valid
Mengubah status kehadiran	Hadir → Tidak Hadir	Status berhasil diperbarui	Sesuai Harapan	Valid
Melihat rekap kehadiran	Pilih sesi	Sistem menampilkan rekap kehadiran	Sesuai Harapan	Valid
3.7.6	Pengujian Manajemen Materi
Tabel 42. Hasil Pengujian Manajemen Materi
Skenario Pengujian	Test Case	Hasil yang Diharapkan	Hasil Pengujian	Kesimpulan
Mengunggah materi baru	File PDF valid	Materi berhasil diunggah	Sesuai Harapan	Valid
Mengunggah file dengan format tidak valid	File .exe	Sistem menolak dan menampilkan pesan error	Sesuai Harapan	Valid
Mengunduh materi	Klik unduh	File berhasil diunduh	Sesuai Harapan	Valid
3.7.7	Ringkasan Hasil Pengujian
Tabel 43. Ringkasan Hasil Pengujian
No	Modul	Jumlah Test	Valid	Persentase
1	Login	4	4	100%
2	Manajemen Pengguna	4	4	100%
3	Input Nilai	4	4	100%
4	Lihat Nilai	3	3	100%
5	Kehadiran	3	3	100%
6	Manajemen Materi	3	3	100%
	Total	21	21	100%
Hasil pengujian menunjukkan bahwa seluruh fungsionalitas sistem berjalan sesuai dengan kebutuhan yang telah ditentukan. Seluruh test case menghasilkan output yang sesuai dengan harapan, sehingga sistem SILAB dapat dikatakan telah memenuhi spesifikasi dan siap untuk diimplementasikan.

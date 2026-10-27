3.3.2 Activity Diagram
Activity Diagram merupakan representasi grafis dari alur kerja prosedural (control flow) yang berjalan secara dinamis di dalam sistem SIPLK. Dalam perancangan ini, Activity Diagram berfungsi untuk menggambarkan logika bisnis, memetakan urutan aktivitas kerja dari satu tahapan ke tahapan berikutnya, serta memvisualisasikan bagaimana lima aktor berinteraksi dengan sistem untuk mencapai tujuan bisnis tertentu. Penggunaan Activity Diagram sangat krusial untuk memastikan tidak terjadi kebocoran otorisasi, mengendalikan validasi berkas unggah secara linier, serta memastikan algoritma pengkondisian transisi status berjalan dengan ketat di level peladen (server-side logic validation). Berikut adalah rincian fungsionalitas Activity Diagram yang dikelompokkan berdasarkan modul peran pengguna untuk memberikan gambaran menyeluruh mengenai mekanisme operasional sistem SIPLK:

Activity Diagram Umum (Proses Autentikasi dan Manajemen Sesi Keamanan). Proses ini merupakan pintu gerbang utama keamanan sistem yang berlaku wajib bagi seluruh entitas pengguna yang ingin berinteraksi dengan SIPLK, baik untuk peran Admin, Manager, Supervisor, Staff, maupun Viewer. Alur kerja dimulai ketika pengguna mengakses halaman utama peladen web internal dan memasukkan data kredensial berupa nama pengguna (username) dan kata sandi (password).
       Sistem secara terotomasi akan menangkap masukan tersebut, mengaktifkan fungsi pencegahan serangan siber brute-force di level server, lalu melakukan pencocokan data masukan dengan record data terenkripsi pada tabel basis data users. Verifikasi kata sandi dijalankan di sisi peladen menggunakan fungsi bawaan PHP password_verify() untuk memvalidasi keabsahan struktur hash bcrypt. Jika data masukan terbukti tidak cocok atau status akun dinyatakan tidak aktif, sistem akan langsung memutus alur kerja, merekam kegagalan log pada file log, dan melempar pesan kesalahan (error message) kembali ke antarmuka pengguna.
       Sebaliknya, jika proses pencocokan berhasil dan sah, sistem akan menginisiasi pembuatan sesi global (session initialization), menerbitkan ID sesi yang terenkripsi unik, menetapkan penanda waktu aktivitas (timestamp), serta mengaktifkan modul penghitung waktu mundur (countdown active session) dengan batasan waktu maksimal 30 menit. Setelah sesi global aktif, sistem membaca nilai atribut peran (role value) pengguna untuk merender struktur menu dashboard secara dinamis, mengunci proteksi menu terlarang, dan memberikan hak akses navigasi menu utama sesuai porsi otoritas kerja masing-masing aktor.

      Sistem Keamanan & Autentikasi. Kategori ini merupakan pilar utama perlindungan sistem yang bertanggung jawab atas proses identifikasi, verifikasi, dan kontrol gerbang masuk pengguna ke dalam lingkungan aplikasi. 

1.	Activity Diagram Login
Fitur ini digunakan untuk memverifikasi identitas pengguna sebelum memberikan akses ke area sistem yang sensitif. Pengguna memasukkan username dan password, lalu sistem memeriksa status pemblokiran akun dan memvalidasi kredensial dengan basis data. Jika data valid, sistem akan mengarahkan pengguna ke dasbor utama. 

     Dasbor Utama. Kategori ini berfungsi sebagai pusat penyajian ringkasan data operasional terpusat yang dirancang untuk memberikan informasi kinerja sistem secara cepat (high-level summary) kepada pengguna sesaat setelah masuk ke dalam aplikasi. Dengan mengintegrasikan penyaringan berbasis izin hak akses folder kerja (folder assignment), kategori ini memastikan bahwa visualisasi statistik, jumlah berkas terdaftar, kontrak aktif, dan kewajiban tertunda (pending obligations) yang disajikan pada halaman utama telah disesuaikan secara real-time dengan batas wewenang masing-masing pengguna.

1.	Activity Diagram Main Dashboard
Halaman utama yang otomatis muncul setelah login. Halaman ini menampilkan ringkasan visual (seperti jumlah file dan status kontrak) yang datanya disesuaikan dengan hak akses masing-masing pengguna. 

 Manajemen Pengguna. Kategori ini memfasilitasi kebutuhan administrasi akun pengguna (user administration) yang membolehkan administrator sistem mengontrol siklus hidup akun personel di dalam aplikasi. Modul ini menyediakan fungsi untuk mendaftarkan akun baru, mengenkripsi kredensial kata sandi dengan standar industri BCRYPT berkekuatan tinggi, memperbarui izin folder operasional secara dinamis, serta melakukan penghapusan akun beserta dependensi datanya secara aman dan selaras menggunakan relasi basis data cascading.

1.	Activity Diagram View Users List
Halaman khusus Admin untuk melihat daftar seluruh akun yang terdaftar di sistem, lengkap dengan informasi jabatan (role) dan batas akses folder mereka.

2.	Activity Diagram Create New User
Fitur bagi Admin untuk mendaftarkan karyawan baru ke dalam sistem, mengatur password yang aman, serta menentukan batas hak akses folder kerja mereka.

3.	Activity Diagram Edit User Permissions
Fitur bagi Admin untuk mengubah atau memperbarui hak akses folder kerja pengguna secara fleksibel sesuai dengan perubahan tugas mereka.

4.	Activity Diagram Delete User
 Fitur bagi Admin untuk menghapus akun pengguna dari sistem secara permanen (Admin tidak bisa menghapus akunnya sendiri yang sedang digunakan).

  Files Repository. Kategori ini bertindak sebagai kubah penyimpanan digital (secure file vault) yang menangani seluruh siklus penyimpanan, pembacaan, dan penghapusan berkas fisik PDF kontrak secara aman. Modul ini menerapkan skema keamanan tingkat tinggi melalui enkripsi berkas berbasis algoritma AES-256-GCM sebelum disimpan ke dalam penyimpanan server utama maupun folder cadangan internal, serta mengontrol aktivitas pembacaan pratinjau (inline stream preview) dan pengunduhan berkas terdekripsi melalui mekanisme otorisasi berbasis token sementara (temporary token).

1.	Activity Diagram Upload Encrypted PDF Files
Fitur bagi Admin untuk mengunggah file PDF kontrak ke dalam sistem. Sistem akan mengecek keamanan file, mengacak namanya, dan mengunci file tersebut dengan enkripsi kuat agar aman dari pencurian data.

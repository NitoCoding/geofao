# Alur Prosedural — Prompt untuk Generate Diagram

Gunakan setiap bagian di bawah ini sebagai prompt untuk AI model lain (Claude, ChatGPT, dll.) guna menghasilkan diagram UML (Activity Diagram, Flowchart, Sequence Diagram).

---

## 1. Alur Autentikasi & RBAC (Login + Otorisasi per Role)

**Jenis Diagram:** Activity Diagram dengan Swimlane

**Aktor/Swimlane:** User, Sistem

**Alur:**

```
                            ┌─── LOGIN ───┐
                            │              │
                            ▼              │
                      [User] Akses halaman │
                      (/accounts/login/)   │
                            │              │
                            ▼              │
                      [User] Input         │
                      username & password  │
                            │              │
                            ▼              │
                      [Sistem] Validasi    │
                      input terisi?        │
                            │              │
              ┌─────────────┴──────┐       │
              │ TIDAK              │ YA    │
              ▼                    ▼       │
        [Sistem] Tampilkan   [Sistem] Cek  │
        "Username & password username di   │
        wajib diisi"         database      │
              │                    │       │
              └────────────────────┼───────┘
                                   ▼
                             User ditemukan?
                                   │
                    ┌──────────────┴──────────────┐
                    │ TIDAK                       │ YA
                    ▼                             ▼
              [Sistem] Tampilkan            [Sistem] Verifikasi
              "Invalid credentials"        password (PBKDF2)
                    │                             │
                    │                  ┌──────────┴──────────┐
                    │                  │ SALAH                │ BENAR
                    │                  ▼                      ▼
                    │            [Sistem] Tampilkan     [Sistem] Buat
                    │            "Invalid credentials"  session & cookie
                    │                  │                      │
                    └──────────────────┼──────────────────────┘
                                       │
                                       ▼
                                 Kembali ke form login
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │   LOGIN BERHASIL     │
                            │                      │
                            │ [Sistem] Ambil role  │
                            │ user dari database   │
                            │        │             │
                            │        ▼             │
                            │ [Sistem] Redirect ke │
                            │ dashboard sesuai     │
                            │ role                 │
                            └──────────┬───────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
         ▼                             ▼                             ▼
   ┌──────────┐                 ┌────────────┐                ┌──────────┐
   │  ADMIN   │                 │TENAGA AHLI │                │  GUEST   │
   │Dashboard │                 │ Dashboard  │                │  Peta    │
   │(semua    │                 │ (terbatas) │                │Interaktif│
   │ menu)    │                 │            │                │  (saja)  │
   └────┬─────┘                 └──────┬─────┘                └────┬─────┘
        │                              │                           │
        └──────────────────────────────┼───────────────────────────┘
                                       │
                                       ▼
                            ┌─── RBAC: SETIAP REQUEST HALAMAN ───┐
                            │                                    │
                            │ [User] Request URL                 │
                            │ (contoh: /master-data/commodities/)│
                            │        │                           │
                            │        ▼                           │
                            │ [Sistem] Cek session:              │
                            │ user sudah login?                  │
                            │        │                           │
                            │  ┌─────┴─────┐                     │
                            │  │ TIDAK     │ YA                  │
                            │  ▼           ▼                     │
                            │ Redirect  [Sistem] Ambil role      │
                            │ ke login  user dari session        │
                            │              │                     │
                            │              ▼                     │
                            │         Role diizinkan             │
                            │         akses halaman ini?         │
                            │              │                     │
                            │    ┌─────────┴─────────┐           │
                            │    │ TIDAK             │ YA        │
                            │    ▼                   ▼           │
                            │  403 Forbidden   [Sistem] Proses   │
                            │  atau redirect   request & ambil   │
                            │  ke halaman      data              │
                            │  default role         │            │
                            │                       ▼            │
                            │                  [Sistem] Render    │
                            │                  halaman sesuai     │
                            │                  role:              │
                            │                       │            │
                            │    ┌──────────────────┼──────┐     │
                            │    │                  │      │     │
                            │    ▼                  ▼      ▼     │
                            │  Admin:         Tenaga Ahli: Guest:│
                            │  SEMUA menu     Data Master,  Peta │
                            │  + tombol aksi  Analisis,    saja  │
                            │                 Expert Review,     │
                            │                 Dashboard          │
                            │                       │            │
                            │                       ▼            │
                            │                  [User] Melihat     │
                            │                  halaman sesuai     │
                            │                  role               │
                            └────────────────────────────────────┘
                                       │
                                       ▼
                                 ┌───────────┐
                                 │  LOGOUT   │
                                 │           │
                                 │ [User]    │
                                 │ Klik      │
                                 │ Logout    │
                                 │     │     │
                                 │     ▼     │
                                 │ [Sistem]  │
                                 │ Hapus     │
                                 │ session & │
                                 │ cookie    │
                                 │     │     │
                                 │     ▼     │
                                 │ Redirect  │
                                 │ ke login  │
                                 └───────────┘
                                       │
                                       ▼
                                      END
```

---

## 2. Alur Upload & Ekstraksi Data Spasial

**Jenis Diagram:** Activity Diagram dengan Swimlane

**Aktor/Swimlane:** User, Sistem

**Alur:**

```
START
  │
  ▼
[User] Akses halaman upload layer (/spatial/layers/upload/)
  │
  ▼
[User] Pilih file ZIP (berisi .shp, .dbf, .shx, .prj)
  │
  ▼
[User] Isi metadata: nama layer, kategori, tahun data
  │
  ▼
[User] Klik "Upload"
  │
  ▼
[Sistem] Validasi file:
  │
  ├── Bukan file ZIP? ──► [Sistem] Tampilkan error "Format file tidak valid" ──► END
  │
  ├── ZIP tidak mengandung .shp? ──► [Sistem] Tampilkan error "File .shp tidak ditemukan" ──► END
  │
  └── Valid ──► Lanjutkan
                 │
                 ▼
            [Sistem] Cek ukuran file:
                 │
                 ├── > 5 MB ──► [Sistem] Kirim task async ke background worker
                 │                 │
                 │                 ▼
                 │            [Sistem] Baca shapefile dari ZIP
                 │                 │
                 │                 ▼
                 │            [Sistem] Ekstrak geometri (Polygon/MultiPolygon)
                 │                 │
                 │                 ▼
                 │            [Sistem] Ekstrak atribut (field names + values)
                 │                 │
                 │                 ▼
                 │            [Sistem] Deteksi SRID dari .prj
                 │                 │
                 │                 ▼
                 │            [Sistem] Simpan geometri ke database
                 │                 │
                 │                 ▼
                 │            [Sistem] Simpan atribut ke database
                 │                 │
                 │                 ▼
                 │            [Sistem] Update status task: "completed"
                 │                 │
                 │                 ▼
                 │            [Sistem] Kirim notifikasi ke user
                 │                 │
                 │                 ▼
                 │               END
                 │
                 └── ≤ 5 MB ──► [Sistem] Proses langsung (sinkron)
                                   │
                                   ▼
                              [Sistem] Baca shapefile dari ZIP
                                   │
                                   ▼
                              [Sistem] Ekstrak geometri (Polygon/MultiPolygon)
                                   │
                                   ▼
                              [Sistem] Ekstrak atribut (field names + values)
                                   │
                                   ▼
                              [Sistem] Deteksi SRID dari .prj
                                   │
                                   ▼
                              [Sistem] Simpan geometri ke database
                                   │
                                   ▼
                              [Sistem] Simpan atribut ke database
                                   │
                                   ▼
                              [Sistem] Return response sukses + redirect
                                   │
                                   ▼
                                 END
```

---

## 3. Alur Analisis Kesesuaian Lahan — FAO Minimum Method

**Jenis Diagram:** Activity Diagram dengan Swimlane

**Aktor/Swimlane:** User, Sistem

**Alur:**

```
START
  │
  ▼
[User] Akses halaman analisis (/analysis/run/)
  │
  ▼
[User] Pilih komoditas (multi-select: Padi, Jagung, Kedelai, dll.)
  │
  ▼
[User] Pilih layer spasial target (dropdown dari MasterLayer)
  │
  ▼
[User] Klik "Mulai Analisis"
  │
  ▼
[Sistem] Validasi input:
  │
  ├── Komoditas kosong? ──► [Sistem] Tampilkan "Pilih minimal 1 komoditas" ──► END
  │
  ├── Layer kosong? ──► [Sistem] Tampilkan "Pilih layer spasial" ──► END
  │
  └── Valid ──► Lanjutkan
                 │
                 ▼
            [Sistem] Buat record analisis (status: "pending")
                 │
                 ▼
            [Sistem] Kirim task ke background worker
                 │
                 ▼
            [Sistem] Redirect user ke Control Center
                 │
                 ▼
╔══════════════════════════════════════════════════════════╗
║              SISTEM — Background Processing              ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  [Sistem] Ambil task dari queue                          ║
║       │                                                   ║
║       ▼                                                   ║
║  [Sistem] Update status: "processing"                     ║
║       │                                                   ║
║       ▼                                                   ║
║  [Sistem] Ambil kriteria kesesuaian komoditas             ║
║  (pH, C-Organik, KTK, tekstur, lereng,                   ║
║   kedalaman, drainase, curah hujan)                      ║
║       │                                                   ║
║       ▼                                                   ║
║  [Sistem] Query semua fitur dari layer target             ║
║       │                                                   ║
║       ▼                                                   ║
║  LOOP untuk setiap fitur (1..N):                          ║
║       │                                                   ║
║       ▼                                                   ║
║  ┌─────────────────────────────────────────┐              ║
║  │ FAO MINIMUM METHOD per fitur:            │              ║
║  │                                           │              ║
║  │ 1. Ambil nilai atribut fitur             │              ║
║  │                                           │              ║
║  │ 2. LOOP untuk setiap parameter (1..8):    │              ║
║  │    a. Ambil nilai aktual fitur            │              ║
║  │       (contoh: pH = 5.8)                  │              ║
║  │    b. Bandingkan dengan kriteria S1–N     │              ║
║  │       IF pH 6.0–7.0 → S1                  │              ║
║  │       IF pH 5.5–6.0 → S2                  │              ║
║  │       IF pH 5.0–5.5 → S3                  │              ║
║  │       IF pH < 5.0  → N                    │              ║
║  │    c. Simpan kelas per parameter          │              ║
║  │                                           │              ║
║  │ 3. Tentukan kelas akhir:                  │              ║
║  │    C_akhir = min(C_pH, C_Corganik,        │              ║
║  │              C_KTK, C_tekstur,            │              ║
║  │              C_lereng, C_kedalaman,       │              ║
║  │              C_drainase, C_ch)            │              ║
║  │                                           │              ║
║  │ 4. Identifikasi faktor pembatas:          │              ║
║  │    parameter dengan kelas = C_akhir       │              ║
║  │                                           │              ║
║  │ 5. Simpan hasil per fitur ke database     │              ║
║  └─────────────────────────────────────────┘              ║
║       │                                                   ║
║       ▼                                                   ║
║  [Sistem] Update progress: (i / N * 100)%                 ║
║       │                                                   ║
║       ▼                                                   ║
║  END LOOP                                                 ║
║       │                                                   ║
║       ▼                                                   ║
║  [Sistem] Update status: "completed"                      ║
║       │                                                   ║
║       ▼                                                   ║
║  [Sistem] Simpan ringkasan: jumlah S1, S2, S3, N          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
                 │
                 ▼
[User di Control Center] Polling status setiap 2 detik
                 │
                 ▼
            [Sistem] Status "completed"?
                 │
                 ├── BELUM ──► [Sistem] Tampilkan progress bar + "processing"
                 │                 │
                 │                 └──► User polling lagi
                 │
                 └── YA ──► [Sistem] Tampilkan ringkasan hasil:
                               - Total fitur: 1.595
                               - S1: 234 (14.7%)
                               - S2: 567 (35.5%)
                               - S3: 612 (38.4%)
                               - N:  182 (11.4%)
                               │
                               ▼
                          [User] Klik toggle "Aktifkan di Peta"
                               │
                               ▼
                          [Sistem] Render GeoJSON dengan kode warna:
                               - S1 → #1B5E20 (hijau tua)
                               - S2 → #4CAF50 (hijau muda)
                               - S3 → #FF9800 (jingga)
                               - N  → #F44336 (merah)
                               │
                               ▼
                             END
```

---

## 4. Alur Expert Review — Validasi Tenaga Ahli

**Jenis Diagram:** Activity Diagram dengan Swimlane

**Aktor/Swimlane:** User, Sistem

**Alur:**

```
START
  │
  ▼
[User] Buka peta interaktif (/spatial/map/)
  │
  ▼
[User] Klik salah satu poligon hasil analisis
  │
  ▼
[Sistem] Deteksi fitur berdasarkan koordinat klik (lat, lng)
  │
  ▼
[Sistem] Ambil data dari 3 sumber:
  │
  ├── Data poligon asli (pH, tekstur, C-Organik, dll.)
  ├── Hasil klasifikasi sistem (per parameter + kelas akhir)
  └── Catatan tenaga ahli sebelumnya (jika ada)
  │
  ▼
[Sistem] Tampilkan drawer panel dengan 4 bagian:
  │
  ├── Bagian 1: Data Poligon Asli (tabel atribut)
  ├── Bagian 2: Hasil Analisis Sistem (tabel dengan kode warna S1–N)
  ├── Bagian 3: Form Catatan Lapangan (textarea)
  └── Bagian 4: Daftar Review Sebelumnya
  │
  ▼
[User] Mengisi catatan lapangan di textarea
  │
  ▼
[User] Klik "Simpan"
  │
  ▼
[Sistem] Cek: apakah user sudah punya catatan untuk poligon ini?
  │
  ├── SUDAH ADA ──► [Sistem] UPDATE catatan yang sudah ada
  │
  └── BELUM ADA ──► [Sistem] INSERT catatan baru
  │
  ▼
[Sistem] Perbarui drawer panel
  │
  ▼
[User] Melihat catatan tersimpan di daftar review
  │
  ▼
END

HAPUS CATATAN (khusus Admin):
  [User] Klik "Hapus" pada catatan di drawer panel
    │
    ▼
  [Sistem] Tampilkan konfirmasi: "Yakin hapus catatan ini?"
    │
    ├── BATAL ──► Tidak terjadi apa-apa
    │
    └── YA ──► [Sistem] Hapus catatan dari database
                 │
                 ▼
              [Sistem] Perbarui drawer panel
                 │
                 ▼
               END
```

---

## 5. Alur Dashboard — Agregasi Data

**Jenis Diagram:** Flowchart / Activity Diagram

**Aktor/Swimlane:** User, Sistem

**Alur:**

```
START
  │
  ▼
[User] Akses /dashboard/
  │
  ▼
[Sistem] Cek role user (Admin/Tenaga Ahli)
  │
  ▼
[Sistem] Jalankan 4 query agregasi:
  │
  ├── Total layer aktif
  ├── Total komoditas
  ├── Total analisis
  └── Total review ahli
  │
  ▼
[Sistem] Render dashboard dengan:
  │
  ├── Card 1: Total Layer Aktif
  ├── Card 2: Total Komoditas
  ├── Card 3: Total Analisis
  ├── Card 4: Total Review Ahli
  │
  ├── Navigasi Cepat:
  │   ├── Link ke Control Center
  │   ├── Link ke Peta Interaktif
  │   ├── Link ke Layer Management
  │   └── Link ke Data Komoditas
  │
  └── (Opsional) Grafik ringkasan per kelas S1–N
  │
  ▼
[User] Melihat dashboard dengan data real-time
  │
  ▼
END
```

---

## 6. Alur End-to-End: Pipeline Analisis Kesesuaian Lahan

**Jenis Diagram:** Sequence Diagram

**Partisipan:** User, Sistem

**Alur:**

```
User                          Sistem
 │                               │
 │  Pilih komoditas + layer      │
 │  Klik "Mulai Analisis"        │
 │──────────────────────────────►│
 │                               │  Validasi input
 │                               │  Buat record analisis
 │                               │  Kirim task ke background worker
 │                               │
 │  Redirect ke Control Center   │
 │◄──────────────────────────────│
 │                               │
 │                               │  ┌── Background Processing ──┐
 │                               │  │ Ambil kriteria komoditas  │
 │                               │  │ Query semua fitur layer   │
 │                               │  │                           │
 │                               │  │ LOOP setiap fitur:        │
 │                               │  │   FAO Minimum Method      │
 │                               │  │   Simpan hasil per fitur  │
 │                               │  │   Update progress         │
 │                               │  │                           │
 │                               │  │ Simpan ringkasan S1–N     │
 │                               │  │ Update status: completed  │
 │                               │  └───────────────────────────┘
 │                               │
 │  Polling status (setiap 2s)   │
 │──────────────────────────────►│
 │  Progress: 45%                │
 │◄──────────────────────────────│
 │                               │
 │  Polling status               │
 │──────────────────────────────►│
 │  Progress: 100% — completed   │
 │  Ringkasan S1:234 S2:567      │
 │  S3:612 N:182                 │
 │◄──────────────────────────────│
 │                               │
 │  Toggle "Aktifkan di Peta"    │
 │──────────────────────────────►│
 │                               │  Query hasil analisis
 │  GeoJSON (poligon + warna)    │
 │◄──────────────────────────────│
 │                               │
 │  Lihat peta interaktif        │
 │  (S1=hijau tua, S2=hijau      │
 │   muda, S3=jingga, N=merah)   │
```

---

## Catatan Penggunaan

1. Copy salah satu bagian di atas sebagai prompt
2. Tambahkan instruksi: "Generate an Activity Diagram / Flowchart / Sequence Diagram in Mermaid.js syntax based on the following procedural flow"
3. Untuk Mermaid.js, hasilnya bisa langsung dirender di GitHub, Notion, atau tools seperti mermaid.live
4. Untuk PlantUML, ganti instruksi menjadi "Generate a PlantUML diagram"
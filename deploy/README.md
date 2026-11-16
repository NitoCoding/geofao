# deploy/

Unit systemd untuk proyek ini. Ketiga file `skripsi*.service` adalah salinan
**verbatim** dari unit yang benar-benar berjalan di server, jadi tinggal `cp`.

| File | Untuk apa |
|---|---|
| `skripsi.service` | gunicorn (web) — `127.0.0.1:8094` |
| `skripsi-celery.service` | worker Celery — menjalankan task di `apps/analysis/tasks.py` |
| `skripsi-celerybeat.service` | penjadwal Celery — `cleanup_old_temp_files` tiap 00:00 |
| `gunicorn.service` | **template generik** dari awal (masih ada placeholder `/path/proyek`, `User=www-data`). Bukan yang dipakai server. Biarkan sebagai contoh kalau proyek ini dipindah ke server lain. |

## Cara pakai (tinggal cp)

Unit-unit ini adalah **systemd --user** dan pemiliknya user `hermes`, jadi
perintahnya harus dijalankan **sebagai hermes** dan tujuan `cp`-nya absolut
(bukan `~`, karena `~` akan menunjuk home user yang menjalankannya):

```bash
cp /srv/projects/skripsi/deploy/skripsi.service \
   /srv/projects/skripsi/deploy/skripsi-celery.service \
   /srv/projects/skripsi/deploy/skripsi-celerybeat.service \
   /home/hermes/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now skripsi.service skripsi-celery.service skripsi-celerybeat.service
```

Cek hasilnya:

```bash
systemctl --user status skripsi.service
systemctl --user status skripsi-celery.service
systemctl --user status skripsi-celerybeat.service
```

## Catatan penting

1. **Jalankan sebagai `hermes`.** `systemctl --user` selalu bicara ke user manager
   milik yang menjalankan perintah (`/run/user/<uid>/`, mode 700). Dari akun
   `ilham`, unit ini tidak akan ditemukan. Untuk perintah Django
   (`make superuser`, `make migrate`, `make shell`) tidak ada batasan ini —
   semuanya bisa dijalankan user mana pun via `./.venv/bin/python`.

2. **`XDG_RUNTIME_DIR`** — kalau `systemctl --user` mengeluh
   *"Failed to connect to user scope bus via local transport"*, set dulu:
   ```bash
   export XDG_RUNTIME_DIR=/run/user/$(id -u)
   ```
   Target `make restart`/`make status` sudah menanganinya sendiri.

3. **Path di dalam unit bersifat absolut** (`/srv/projects/skripsi`,
   `/srv/projects/.uv-python`). Kalau proyek dipindah, `WorkingDirectory`,
   `ExecStart`, dan `DJANGO_ENV_FILE` harus ikut diubah.

4. **Beat hanya boleh satu instance.** Jangan duplikasi `skripsi-celerybeat.service`.

5. **Kenapa `DJANGO_ENV_FILE` dan bukan `EnvironmentFile`?** Aplikasi membaca
   sendiri `/srv/projects/skripsi/.env.prod` (mode 600, milik hermes) lewat
   variabel itu, sehingga rahasia tidak masuk ke environment proses dan tidak
   bisa bocor lewat `systemctl show`.

6. **`make install`** hanya mengurus unit web (`skripsi.service`). Untuk
   `skripsi-celery` dan `skripsi-celerybeat`, pakai perintah `cp` + `enable` di atas.

## Kalau nanti mau unit system-level (butuh sudo)

Unit di folder ini adalah **user unit**. Alternatifnya unit system-level
(`/etc/systemd/system/`, `User=hermes`, `WantedBy=multi-user.target`) — bisa
dikelola user mana pun yang punya sudo, tapi perlu sudo untuk memasangnya dan
log-nya pindah ke `journalctl -u <unit>` (tanpa `--user`). Belum dibuat.

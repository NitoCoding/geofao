# ============================================================================
# Makefile - proyek skripsi (Django + GeoDjango) di /srv/projects/skripsi
#
# Dua konteks pemakaian:
#   * Target environment (python, setup, lock)      -> BUTUH `uv`
#   * Semua target lain                             -> TIDAK butuh uv.
#     Memakai interpreter venv langsung, jadi bisa dijalankan user mana pun
#     yang punya akses ke folder proyek ini (ilham maupun hermes).
#
# Prasyarat agar target runtime jalan untuk SEMUA user:
#   Python di dalam .venv harus berada di /srv/projects/.uv-python, BUKAN di
#   dalam /home/hermes (home hermes mode 750, tidak bisa ditembus user lain).
#   Karena itu semua perintah uv dipaksa memakai UV_PY_DIR.
#
# Jalankan `make help` untuk daftar perintah.
# `make doctor` = pemeriksaan baca-saja sebelum/sesudah deploy.
# ============================================================================

# ---------- Path & nama unit ----------
PROJECT_DIR    = /srv/projects/app
PY             = $(PROJECT_DIR)/.venv/bin/python
MANAGE         = $(PY) $(PROJECT_DIR)/manage.py
ENV_PROD       = $(PROJECT_DIR)/.env.prod
ENV_DEV        = $(PROJECT_DIR)/.env
SCRIPTS        = $(PROJECT_DIR)/scripts
BACKUP_DIR     = $(PROJECT_DIR)/backups

SERVICE        = gunicorn.service
SERVICE_WORKER = celery.service
SERVICE_BEAT   = celerybeat.service
ALL_SERVICES   = $(SERVICE) $(SERVICE_WORKER) $(SERVICE_BEAT)

# Kontainer PostGIS yang menampung database proyek ini.
# pg_dump/psql dijalankan DI DALAM kontainer karena host tidak punya
# psql/pg_dump, dan versi client harus cocok dengan server (PostgreSQL 18).
PG_CONTAINER   = databases-postgis-1

# ---------- Port & bind ----------
PORT      = 8094
# Server pengembangan sengaja di port lain supaya tidak bentrok dengan produksi.
PORT_DEV  = 8095
# Default 127.0.0.1 = hanya dari dalam server. Untuk dibuka dari laptop
# lewat Tailscale: make run-ts
HOST     ?= 127.0.0.1
TS_IP     = 100.76.107.101

CERT_FILE = $(PROJECT_DIR)/cert.crt
KEY_FILE  = $(PROJECT_DIR)/cert.pem

# ---------- Toolchain Python bersama (lihat catatan di header) ----------
UV_PY_DIR = /srv/projects/.uv-python

# ---------- systemctl --user butuh XDG_RUNTIME_DIR ----------
# Di shell non-login (SSH, su, tmux, sudo -u) variabel ini sering kosong dan
# gejalanya: "Failed to connect to user scope bus via local transport".
# Baris di bawah menurunkan nilainya kalau shell belum menyetelnya
# (?= tidak menimpa nilai yang sudah ada dari environment).
XDG_RUNTIME_DIR ?= /run/user/$(shell id -u)
export XDG_RUNTIME_DIR

.PHONY: help \
        python setup lock \
        check check-prod migrate makemigrations showmigrations migrate-status \
        collectstatic superuser passwd shell test clearsessions urls \
        run run-ts run-secure \
        install restart restart-celery restart-beat restart-all start stop \
        status logs logs-celery logs-beat logs-all uninstall \
        doctor env-info \
        backup-db backup-media restore-db restore-media \
        db-shell clean-pyc \
        crontab-backup crontab-backup-remove crontab-list

# ============================================================================
# help
# ============================================================================
help:
	@echo "Perintah yang tersedia:"
	@echo ""
	@echo "  DATABASE & MODEL"
	@echo "    make showmigrations  daftar migrasi dan statusnya"
	@echo "    make makemigrations  buat migrasi dari perubahan model"
	@echo "    make migrate         terapkan migrasi ke database"
	@echo "    make db-shell        psql interaktif di dalam kontainer"
	@echo ""
	@echo "  BACKUP & RESTORE (django-dbbackup)"
	@echo "    make backup-db       backup database (terkompresi, bersihkan yg lama)"
	@echo "    make backup-media    backup file media (terkompresi)"
	@echo "    make restore-db      restore database dari backup terakhir"
	@echo "    make restore-media   restore file media dari backup terakhir"
	@echo ""
	@echo "  CEK & VALIDASI"
	@echo "    make doctor          periksa semua (baca-saja, tanpa mengubah apa pun)"
	@echo "    make env-info        tampilkan konfigurasi efektif (rahasia disamarkan)"
	@echo "    make check           validasi konfigurasi Django"
	@echo "    make check-prod      validasi Django dengan setelan produksi (check --deploy)"
	@echo ""
	@echo "  AKUN & SHELL"
	@echo "    make superuser       buat akun admin Django (interaktif)"
	@echo "    make passwd DJUSER=nama   ganti password user Django"
	@echo "    make shell           Django shell"
	@echo "    make test            jalankan test"
	@echo "    make clearsessions   hapus sesi kedaluwarsa"
	@echo "    make urls            daftar semua URL"
	@echo ""
	@echo "  SERVER PENGEMBANGAN"
	@echo "    make run             dev server di $(HOST):$(PORT_DEV) (hanya dari dalam server)"
	@echo "    make run-ts          dev server di $(TS_IP):$(PORT_DEV) (buka dari laptop via Tailscale)"
	@echo "    make run-secure      dev server + HTTPS self-signed"
	@echo ""
	@echo "  SERVICE (systemd --user milik hermes - harus dijalankan sebagai hermes)"
	@echo "    make install         collectstatic + daftarkan & nyalakan ketiga unit"
	@echo "    make restart         restart web ($(SERVICE))"
	@echo "    make restart-celery  restart worker Celery"
	@echo "    make restart-beat    restart penjadwal Celery"
	@echo "    make restart-all     restart ketiganya"
	@echo "    make start / stop    nyalakan / hentikan ketiganya"
	@echo "    make status          status ketiga unit"
	@echo "    make logs            ikuti log web"
	@echo "    make logs-celery     ikuti log worker Celery"
	@echo "    make logs-beat       ikuti log penjadwal Celery"
	@echo "    make logs-all        ikuti ketiga log sekaligus"
	@echo "    make uninstall       hentikan & hapus dari daftar enable"
	@echo ""
	@echo "  ENVIRONMENT (butuh uv)"
	@echo "    make python          pasang Python 3.10 ke $(UV_PY_DIR)"
	@echo "    make setup           sinkronkan environment dari uv.lock"
	@echo "    make lock            perbarui uv.lock"
	@echo ""
	@echo "  PEMELIHARAAN"
	@echo "    make collectstatic   kumpulkan file statis"
	@echo "    make clean-pyc       hapus __pycache__ (tidak menyentuh .venv)"
	@echo ""
	@echo "  CRONTAB BACKUP (penjadwalan sistem)"
	@echo "    make crontab-backup         daftarkan backup-db (6:00, 18:00) & backup-media (6:00)"
	@echo "    make crontab-backup-remove   hapus jadwal backup dari crontab"
	@echo "    make crontab-list            lihat isi crontab saat ini"

# ============================================================================
# Environment (butuh uv)
# ============================================================================
python:
	UV_PYTHON_INSTALL_DIR=$(UV_PY_DIR) uv python install 3.10

setup:
	UV_PYTHON_INSTALL_DIR=$(UV_PY_DIR) uv sync

lock:
	UV_PYTHON_INSTALL_DIR=$(UV_PY_DIR) uv lock

# ============================================================================
# Cek & validasi
# ============================================================================
doctor:
	@bash $(SCRIPTS)/preflight.sh

env-info:
	@bash $(SCRIPTS)/preflight.sh --env-info

check:
	$(MANAGE) check

# Memeriksa dengan setelan PRODUKSI (.env.prod), bukan .env dev.
check-prod:
	DJANGO_ENV_FILE=$(ENV_PROD) $(MANAGE) check --deploy

# ============================================================================
# Database & model
# ============================================================================
showmigrations:
	$(MANAGE) showmigrations

makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

# Tidak dipakai langsung, hanya alias agar `make migrate-status` tidak salah ketik.
migrate-status: showmigrations

# Backup & restore via django-dbbackup.
# Backup disimpan di direktori yang ditetapkan STORAGES["dbbackup"] di settings.py
# (saat ini /backup/).
backup-db:
	$(MANAGE) dbbackup --clean --compress
	@echo "backup database selesai (lihat /backup/ di server)"

backup-media:
	$(MANAGE) mediabackup --clean --compress
	@echo "backup media selesai (lihat /backup/ di server)"

restore-db:
	$(MANAGE) dbrestore --clean
	@echo "restore database selesai"

restore-media:
	$(MANAGE) mediarestore --clean
	@echo "restore media selesai"

db-shell:
	@db=$$(grep -m1 '^DB_NAME=' $(ENV_PROD) 2>/dev/null | cut -d= -f2- | tr -d '"'); db=$${db:-gisdb3}; \
	 user=$$(grep -m1 '^DB_USER=' $(ENV_PROD) 2>/dev/null | cut -d= -f2- | tr -d '"'); user=$${user:-gisuser}; \
	 echo "psql di kontainer $(PG_CONTAINER) sebagai '$$user' pada database '$$db' (ketik \\q untuk keluar)"; \
	 t=$$([ -t 0 ] && echo '-it' || echo '-i'); \
	 sg docker -c "docker exec $$t $(PG_CONTAINER) psql -U $$user -d $$db"

# ============================================================================
# Akun, shell, test
# ============================================================================
superuser:
	$(MANAGE) createsuperuser

# Sengaja TIDAK memakai nama variabel USER: itu variabel environment (nama login
# shell) yang otomatis diimpor make, jadi bisa tertukar tanpa disadari.
passwd:
	@test -n "$(DJUSER)" || { echo "Pakai: make passwd DJUSER=<username>"; exit 1; }
	$(MANAGE) changepassword $(DJUSER)

shell:
	$(MANAGE) shell

test:
	$(MANAGE) test

clearsessions:
	$(MANAGE) clearsessions

urls:
	$(MANAGE) show_urls

# ============================================================================
# Server pengembangan
# ============================================================================
run:
	$(MANAGE) runserver_plus $(HOST):$(PORT_DEV)

# Bind ke IP Tailscale supaya bisa dibuka dari laptop (jaringan privat).
# DEBUG=True, jadi JANGAN pakai 0.0.0.0 di jaringan yang tidak dipercaya.
run-ts:
	$(MANAGE) runserver_plus $(TS_IP):$(PORT_DEV)

run-secure:
	$(MANAGE) runserver_plus $(HOST):$(PORT_DEV) --cert-file $(CERT_FILE) --key-file $(KEY_FILE)

# ============================================================================
# Service (systemd --user milik hermes)
# Unit-nya di /home/hermes/.config/systemd/user/, dan systemctl --user selalu
# bicara ke user manager MILIK YANG MENJALANKAN perintah (/run/user/<uid>/,
# mode 700). Jadi target di bawah ini hanya bisa dijalankan sebagai hermes.
# Target Django di atas tidak terikat batasan ini.
# ============================================================================
install: collectstatic
	systemctl --user daemon-reload
	systemctl --user enable --now $(SERVICE) $(SERVICE_WORKER) $(SERVICE_BEAT)

restart:
	systemctl --user restart $(SERVICE)

restart-celery:
	systemctl --user restart $(SERVICE_WORKER)

restart-beat:
	systemctl --user restart $(SERVICE_BEAT)

restart-all:
	systemctl --user restart $(SERVICE) $(SERVICE_WORKER) $(SERVICE_BEAT)

start:
	systemctl --user start $(SERVICE) $(SERVICE_WORKER) $(SERVICE_BEAT)

stop:
	systemctl --user stop $(SERVICE) $(SERVICE_WORKER) $(SERVICE_BEAT)

status:
	@for s in $(ALL_SERVICES); do printf '%-28s %s\n' "$$s" "$$(systemctl --user is-active $$s)"; done
	@echo "(detail: systemctl --user status $(SERVICE) --no-pager)"

logs:
	journalctl --user -u $(SERVICE) -f

logs-celery:
	journalctl --user -u $(SERVICE_WORKER) -f

logs-beat:
	journalctl --user -u $(SERVICE_BEAT) -f

logs-all:
	journalctl --user -u $(SERVICE) -u $(SERVICE_WORKER) -u $(SERVICE_BEAT) -f

uninstall:
	systemctl --user disable --now $(SERVICE) $(SERVICE_WORKER) $(SERVICE_BEAT)

# ============================================================================
# Pemeliharaan
# ============================================================================
collectstatic:
	$(MANAGE) collectstatic --noinput

# Sengaja dibatasi ke folder kode saja; .venv tidak disentuh.
clean-pyc:
	@for d in apps config core scripts; do \
		[ -d $(PROJECT_DIR)/$$d ] && find $(PROJECT_DIR)/$$d -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null; \
	done; true
	@echo "cache Python dibersihkan (apps, config, core, scripts)"

# ============================================================================
# Crontab backup
# Memakai marker comment agar bisa dihapus bersih tanpa menyentuh entri lain.
# ============================================================================
CRONTAB_MARKER_START = # --- skripsi-backup ---
CRONTAB_MARKER_END   = # --- end skripsi-backup ---

# Backup database jam 6:00 dan 18:00 setiap hari.
# Backup media jam 6:00 setiap hari (setelah backup-db).
CRONTAB_BACKUP_ENTRIES = \
	'$(CRONTAB_MARKER_START)' \
	'0 6 * * * cd $(PROJECT_DIR) && $(MAKE) backup-db >/dev/null 2>&1' \
	'0 18 * * * cd $(PROJECT_DIR) && $(MAKE) backup-db >/dev/null 2>&1' \
	'0 7 * * * cd $(PROJECT_DIR) && $(MAKE) backup-media >/dev/null 2>&1' \
	'$(CRONTAB_MARKER_END)'

crontab-backup:
	@if crontab -l 2>/dev/null | grep -qF '$(CRONTAB_MARKER_START)'; then \
		echo "Jadwal backup sudah ada di crontab. Tidak ada perubahan."; \
	else \
		(crontab -l 2>/dev/null; echo "$$(printf '%s\n' $(CRONTAB_BACKUP_ENTRIES))") | crontab -; \
		echo "Jadwal backup ditambahkan ke crontab:"; \
		echo "  06:00 - backup database"; \
		echo "  07:00 - backup media"; \
		echo "  18:00 - backup database"; \
	fi

crontab-backup-remove:
	@if crontab -l 2>/dev/null | grep -qF '$(CRONTAB_MARKER_START)'; then \
		crontab -l 2>/dev/null | sed '/$(CRONTAB_MARKER_START)/,/$(CRONTAB_MARKER_END)/d' | crontab -; \
		echo "Jadwal backup dihapus dari crontab."; \
	else \
		echo "Tidak ada jadwal backup di crontab."; \
	fi

crontab-list:
	@crontab -l 2>/dev/null || echo "(crontab kosong)"

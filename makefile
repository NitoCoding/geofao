SERVICE     = myapp.service
UNIT_DIR    = /etc/systemd/system
CERT_FILE   = cert.crt
KEY_FILE    = cert.pem

.PHONY: setup run run-secure migrate collectstatic test install restart status logs uninstall

# --- Dev (laptop atau server) ---
setup:
	uv sync

run:
	uv run python manage.py runserver_plus

run-secure:
	uv run python manage.py runserver_plus --cert-file $(CERT_FILE) --key-file $(KEY_FILE)

migrate:
	uv run python manage.py migrate

collectstatic:
	uv run python manage.py collectstatic --noinput

test:
	uv run python manage.py test

# --- Deploy (Ubuntu server) ---
install:
	uv run python manage.py collectstatic --noinput
	sudo cp $(SERVICE) $(UNIT_DIR)/$(SERVICE)
	sudo systemctl daemon-reload
	sudo systemctl enable --now $(SERVICE)

restart:
	sudo systemctl restart $(SERVICE)

status:
	systemctl status $(SERVICE)

logs:
	journalctl -u $(SERVICE) -f

uninstall:
	sudo systemctl disable --now $(SERVICE)
	sudo rm -f $(UNIT_DIR)/$(SERVICE)
	sudo systemctl daemon-reload
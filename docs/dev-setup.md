# Development Setup: Frappe on Windows (WSL2 / Devcontainer)

Frappe/ERPNext do not run natively on Windows. There are two supported ways
to develop **Distributor ERP Lite** on a Windows machine:

1. **WSL2 + bench** (recommended for day-to-day work)
2. **VS Code Dev Container** (reproducible, zero host pollution)

---

## Option 1 — WSL2 + bench

### 1. Install WSL2 with Ubuntu

```powershell
wsl --install -d Ubuntu-22.04
```

Reboot when prompted, then open the Ubuntu shell and update:

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install system dependencies

```bash
sudo apt install -y git python3.11 python3.11-dev python3.11-venv python3-pip \
    mariadb-server mariadb-client redis-server xvfb libfontconfig1 \
    libmysqlclient-dev libncurses5-dev libcairo2-dev libpango1.0-dev \
    wkhtmltopdf pkg-config curl nodejs npm
```

Install Node 18+ via nvm (Ubuntu's apt node is often too old for Frappe's
build tooling):

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
```

### 3. Configure MariaDB for Frappe

```bash
sudo systemctl enable --now mariadb
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'admin123'; FLUSH PRIVILEGES;"
```

Add the Frappe-required settings to `/etc/mysql/mariadb.conf.d/50-server.cnf`
under `[mysqld]`:

```ini
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

```bash
sudo systemctl restart mariadb
```

### 4. Install bench and the framework

```bash
pip3 install --user frappe-bench
# ensure ~/.local/bin is on PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc && source ~/.bashrc

bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
```

### 5. Get ERPNext and this repository

```bash
bench get-app erpnext --branch version-15 https://github.com/frappe/erpnext
bench get-app distributor_erp_lite https://github.com/danangswn/ERP --branch main
```

### 6. Create a site and install the apps

```bash
bench new-site dev.local \
    --db-root-password admin123 \
    --admin-password admin \
    --install-app erpnext

bench --site dev.local install-app distributor_core
bench --site dev.local install-app id_compliance
bench --site dev.local install-app marketplace_sync

bench --site dev.local set-maintenance-mode off
bench start   # http://dev.local:8000  (admin / admin)
```

Add `127.0.0.1 dev.local` to `/etc/hosts` if needed.

### 7. Running tests

```bash
bench --site dev.local run-tests --app distributor_core
bench --site dev.local run-tests --app id_compliance
bench --site dev.local run-tests --app marketplace_sync
```

---

## Option 2 — VS Code Dev Container

This repository is designed to be opened in a dev container that mounts the
apps into a bench directory. Create `.devcontainer/devcontainer.json` (not
committed — tailor paths to your machine):

```json
{
  "name": "distributor-erp-lite",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    "ghcr.io/itsmechlark/features/redis-server:1": {},
    "ghcr.io/itsmechlark/features/mariadb:1": { "version": "10.6" }
  },
  "postCreateCommand": "bash .devcontainer/setup-bench.sh",
  "forwardPorts": [8000, 9000, 3306],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "samuelcolvin.jinjahtml"
      ]
    }
  }
}
```

And `.devcontainer/setup-bench.sh`:

```bash
#!/usr/bin/env bash
set -e
pip install frappe-bench
bench init --frappe-branch version-15 ~/frappe-bench
cd ~/frappe-bench
# symlink this checkout's apps into the bench
for app in distributor_core id_compliance marketplace_sync; do
    ln -s "$PWD/../..//apps/$app" "apps/$app" 2>/dev/null || true
done
```

Then: **F1 → "Dev Containers: Reopen in Container"**.

> The container approach requires MariaDB inside the container; the
> `itsmechlark/features/mariadb` feature handles install but you still need
> the `50-server.cnf` utf8mb4 settings from Option 1, step 3.

---

## Windows-side quick checks (no bench required)

Some validation does not need a running site and can be run from PowerShell:

```powershell
# Python syntax check of all three apps (requires Python on PATH)
python -m compileall -q distributor_core id_compliance marketplace_sync

# JSON syntax check of every doctype/report/print-format JSON
node -e "const fs=require('fs');['distributor_core','id_compliance','marketplace_sync'].forEach(app=>{const walk=d=>fs.readdirSync(d,{withFileTypes:true}).forEach(f=>{const p=d+'/'+f.name;if(f.isDirectory())walk(p);else if(f.name.endsWith('.json'))JSON.parse(fs.readFileSync(p,'utf8'))});walk(app);console.log(app,'JSON OK')})"
```

---

## Editor settings

- Format Python with **Black** (88 cols) and sort imports with **isort**.
- Jinja templates: use the `jinjahtml` VS Code extension.
- Doctype JSONs are hand-maintained; Frappe regenerates them on migration,
  so avoid reformatting them mechanically.

## Useful bench commands

| Command | Purpose |
| --- | --- |
| `bench start` | Run web/worker/scheduler locally |
| `bench --site dev.local migrate` | Apply schema/migrations after doctype changes |
| `bench --site dev.local clear-cache` | Clear cache after hooks changes |
| `bench --site dev.local reinstall` | Destructive reset of the site |
| `bench build --app distributor_core` | Bundle JS/CSS assets |

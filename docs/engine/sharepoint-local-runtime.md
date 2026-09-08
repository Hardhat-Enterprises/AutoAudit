# SharePoint Online local scan runtime

Run all commands from the AutoAudit project root (`.../AutoAudit/`), not `.../AutoAudit/engine/`, unless a step says otherwise.

Keep certificate and password files **outside the repo**. Never commit them, and never commit `docker-compose.sharepoint.override.yml`.

## 1. Pull latest `main`

```bash
git switch main
git pull
```

## 2. Save the provided files

Contact the Team Lead for `t8sjf.pfx` and `t8sjf.password`. Do not generate your own certificate for this shared test runtime.

Place those files in `~/autoaudit-sharepoint-cert/`:

```bash
mkdir -p ~/autoaudit-sharepoint-cert
```

The folder must look like this:

```
~/autoaudit-sharepoint-cert/
├── t8sjf.pfx
└── t8sjf.password
```

Confirm they are **files** (not directories) before starting Docker. If the paths are missing, Docker may create directories with those names and SharePoint collection will fail:

```bash
test -f ~/autoaudit-sharepoint-cert/t8sjf.pfx && echo "PFX OK"
test -f ~/autoaudit-sharepoint-cert/t8sjf.password && echo "Password OK"
```

Both commands should print `OK` before you run Docker Compose.

## 3. Copy the override

```bash
cp docker-compose.sharepoint.override.yml.example docker-compose.sharepoint.override.yml
```

Edit only the two host paths. Docker needs **absolute** host paths (not `~`). Those files are mounted **read-only** into the PowerShell container:

```yaml
- /home/<USER>/autoaudit-sharepoint-cert/t8sjf.pfx:/certs/aliases/t8sjf.pfx:ro
- /home/<USER>/autoaudit-sharepoint-cert/t8sjf.password:/certs/aliases/t8sjf.password:ro
```

## 4. Start worker and PowerShell

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.sharepoint.override.yml \
  --profile worker --profile powershell \
  up -d --build worker powershell-service
```

## 5. Confirm they are running

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.sharepoint.override.yml \
  --profile worker --profile powershell \
  ps
```

`worker` and `powershell-service` should be up.

## 6. Run the scan

You do not need to run `Connect-PnPOnline` yourself. AutoAudit connects to SharePoint PnP during the scan.

In the app, use the M365 connection for the **t8sjf** tenant/application that matches the provided certificate. If you pick a different tenant, Graph and Exchange can scan that tenant while SharePoint PnP still uses t8sjf.

Open http://localhost:3000 and start a scan.

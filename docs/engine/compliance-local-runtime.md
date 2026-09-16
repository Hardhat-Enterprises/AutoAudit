# Security & Compliance local scan runtime

Run all commands from the AutoAudit project root (`.../AutoAudit/`), not `.../AutoAudit/engine/`, unless a step says otherwise.

Security & Compliance local runtime mirrors the SharePoint local runtime [SharePoint local runtime](./sharepoint-local-runtime.md) and reuses the
same certificate and app registration. Only the differences are described here.

Keep certificate and password files **outside the repo**. Never commit them, and never commit `docker-compose.compliance.override.yml`.

## 1. Tenant prerequisites

The certificate alone is not enough. Two things must also be true in Entra:

- `Exchange.ManageAsApp` on **Microsoft Exchange Online Protection**. If not, connection will be refused with an `AADSTS` error. Note that a permission with the same name `Exchange.ManageAsApp` also exists on *Office 365 Exchange Online*, which is what the Exchange collectors use. S&C is a different API with different permissions. `Exchange.ManageAsApp` for *Exchange Online Protection* is specifically required.
- A directory role valid for Security & Compliance. **Global Reader** is recommended, tested and verified working. If this is not done, the connection will be established, but the cmdlet requested will throw an error as 'not recognised'.

Also note that the Exchange Administrator role is not valid for Security & Compliance, despite being valid for Exchange Online PowerShell. An app holding only the Exchange Administrator role will connect but will find none of the required cmdlets.

Allow some time for permissions and role assignment to propagate, up to approximately one hour.

## 2. Use the SharePoint certificate

No new certificate is needed. AutoAudit passes the same `client_id` to `Connect-PnPOnline` and `Connect-IPPSSession`, so the certificate already uploaded to the app registration works for both.

Use the files from step 2 of the SharePoint runtime. Filenames vary (`.p12` and `.pfx` are the same format); match whatever you have available into the override below.

## 3. Copy the override

```bash
cp docker-compose.compliance.override.yml.example docker-compose.compliance.override.yml
```

Edit the two host paths, and `COMPLIANCE_ORGANIZATION`. Docker needs **absolute** host paths (not `~`). The files are mounted **read-only**.

`COMPLIANCE_ORGANIZATION` must be the tenant's primary `.onmicrosoft.com` domain. A tenant GUID is rejected.

## 4. Start worker and PowerShell

```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.sharepoint.override.yml \
  -f docker-compose.compliance.override.yml \
  --profile worker --profile powershell \
  up -d --build worker powershell-service
```


## 5. Verify the connection

Compliance collectors are not registered yet, so call the service directly:

```bash
curl -s -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"module":"Compliance","cmdlet":"Get-DlpCompliancePolicy","params":{},
       "tenant_id":"<tenant>.onmicrosoft.com","client_id":"<client-id>",
       "certificate_alias":"<your alias>","organization":"<tenant>.onmicrosoft.com"}'
```

Expect `"success": true` in 10–15 seconds. A `null` result means the connection worked and the tenant has no DLP policies — that is not compliance, and the policies fail closed on missing evidence.

If it fails, read the error before touching the certificate:

- **`... is not recognized as a name of a cmdlet`** — authentication succeeded and the session has no Purview cmdlets. Assign the directory role from step 1.
- **`AADSTS...`** — authentication failed. `AADSTS700016` means the `client_id` is wrong; other codes usually mean the Exchange Online Protection permission is missing or unconsented.
- **`The certificate data cannot be read with the provided password`** — the password file and certificate disagree, usually a trailing newline baked in when the file was created on Windows. Check with `openssl pkcs12 -in <file> -nokeys -noout -passin ...`.

## Rules

- Compliance requires the PowerShell HTTP service. Without `POWERSHELL_SERVICE_URL` the worker raises a clear error rather than falling back to Docker.
- Do not commit certificates, passwords, or `docker-compose.compliance.override.yml`.
- Do not create another Security & Compliance authentication flow.
- `COMPLIANCE_CERT_ALIASES` is a separate map from `SHAREPOINT_CERT_ALIASES` on purpose. Pointing both at one certificate is a convenience for the shared dev tenant; swapping in a dedicated certificate later is config only, no code changes.
- The shared certificate now covers SharePoint **and** Compliance, so its expiry breaks more than it used to.

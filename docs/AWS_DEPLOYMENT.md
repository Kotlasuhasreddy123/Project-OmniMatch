# OmniMatch AWS deployment guide

This guide deploys the synthetic-data application on one Linux EC2 machine. No AWS resources were provisioned by this change. Costs depend on region, instance, disk, traffic and runtime; configure a billing budget first. Start with an x86 Ubuntu 24.04 instance with 8 GB RAM for CPU model inference, then measure actual memory and latency. A small free-tier machine may run out of memory during model loading.

## 1. Prepare AWS

Create an EC2 instance using an encrypted EBS root volume (at least 40 GB recommended for images and models). Use an IAM role and Systems Manager for access where available. Otherwise allow SSH port 22 only from your current IP. Keep ports 3000, 8000, 6333 and 6334 closed to the internet. For a public demo, allow HTTPS 443 and HTTP 80 for certificate issuance, with a domain pointed to the instance. Use synthetic details only.

Official references: [EC2 security groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html), [data protection and encrypted EBS](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/data-protection.html), [Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

## 2. Install and copy the application

Install Docker Engine and the Compose plugin following the official Ubuntu guide above. Verify:

```bash
docker version
docker compose version
git clone https://github.com/Kotlasuhasreddy123/Project-OmniMatch.git
cd Project-OmniMatch
cp backend/.env.example backend/.env
openssl rand -hex 32
openssl rand -hex 32
```

Edit backend/.env. Set APP_SECRET_KEY and JWT_SECRET_KEY to the two separate generated secrets. Keep DEMO_MODE=true. Do not commit this file. A fresh clone of the GitHub repository contains backend, frontend and docker-compose.yml at its root. Run the commands from that root. If you also have an older local project copy, use the reviewed Git checkout rather than mixing its files with the older copy.

## 3. Private deployment for rehearsal

Keep APP_ALLOWED_ORIGINS=http://localhost:3000. On EC2:

```bash
docker compose --env-file backend/.env up -d --build
docker compose ps
docker compose logs --tail=100 backend
curl --fail http://localhost:8000/api/v1/health
```

The initial build/model download can take several minutes. On your laptop, use a terminal and your EC2 DNS/key:

```powershell
ssh -i "C:\path\key.pem" -L 3000:127.0.0.1:3000 -L 8000:127.0.0.1:8000 ubuntu@YOUR_EC2_PUBLIC_DNS
```

Leave the tunnel open and visit http://localhost:3000. Microphone permission works on localhost. Existing localhost API settings work through this tunnel. This is the easiest presentation deployment without exposing the API publicly.

## 4. Public HTTPS deployment

The repository includes a Caddy/Compose overlay to configure the two HTTPS domains without editing the base Compose file. From the repository root on EC2:

```bash
cp deploy/aws.env.example deploy/aws.env
# Edit deploy/aws.env with your app and API domains.
# Verify encrypted EBS and backups, then set ENCRYPTED_STORAGE_CONFIRMED=true.
docker compose --env-file backend/.env --env-file deploy/aws.env -f docker-compose.yml -f deploy/compose.aws.yml config --quiet
docker compose --env-file backend/.env --env-file deploy/aws.env -f docker-compose.yml -f deploy/compose.aws.yml up -d --build
docker compose --env-file backend/.env --env-file deploy/aws.env -f docker-compose.yml -f deploy/compose.aws.yml ps
```

Both environment files are required: backend/.env supplies the public WorkOS IDs to the frontend build, and deploy/aws.env supplies the domains and storage confirmation. Set WORKOS_CLIENT_ID and WORKOS_ORGANIZATION_ID in backend/.env before building.

Create DNS A records for both domains pointing to your EC2 public IPv4 address. Allow TCP 80 and 443 in the EC2 security group; keep application/database ports private. Keep backend/.env configured with strong distinct secrets. The overlay sets browser API URL at build time, CORS origin, synthetic-data mode, and TLS 1.3. Caddy stores certificate state in named volumes. Verify certificate issuance and all browser calls before sharing the URL. This configuration requires testing on your AWS account; no account resources or certificates have been provisioned here.

Use a reverse proxy such as Caddy or an Application Load Balancer with an ACM certificate. Serve the frontend at https://app.YOUR_DOMAIN and backend at https://api.YOUR_DOMAIN. Change the frontend build argument NEXT_PUBLIC_API_URL in docker-compose.yml to https://api.YOUR_DOMAIN and rebuild the frontend; changing only the runtime variable will not update a Next.js browser bundle. Set backend APP_ALLOWED_ORIGINS=https://app.YOUR_DOMAIN. Keep application ports bound to loopback when the proxy runs on the host. A container proxy must join the Compose network and address backend:8000 and frontend:3000 instead.

For a host-installed Caddy proxy, the Caddyfile is:

```caddyfile
app.YOUR_DOMAIN {
    tls {
        protocols tls1.3
    }
    reverse_proxy 127.0.0.1:3000
}
api.YOUR_DOMAIN {
    tls {
        protocols tls1.3
    }
    reverse_proxy 127.0.0.1:8000
}
```

Replace both domain placeholders and verify DNS before enabling the proxy. Configure [passwordless organization roles and owner approval](PASSWORDLESS_ACCESS.md). Review backend configuration before allowing external users. HTTPS is necessary for browser microphone access on a public domain.

Production startup also requires configured WorkOS client/organization IDs, explicit HTTPS origins and two different random secrets. See [security guardrails](SECURITY_GUARDRAILS.md). Startup refuses missing prerequisites; the storage confirmation flag does not perform encryption.

## 5. Acceptance checks

Confirm health and all three containers. In the browser, create a synthetic patient label, grant consent, record or enter a fictional note, correct the transcript, approve terms and submit. Confirm the inbox receives results, charts reflect filtered visits, and timeline shows repeat visits for the same patient label. Verify the app rejects recording without consent and rejects unauthenticated inbox API calls. Verify archive/restore and refresh persistence. Test HTTPS microphone access from the actual presentation laptop.

## 6. Operations, backup and rollback

Persist both Compose named volumes. Record image tags and the deployed commit. Before an update, stop writes and take encrypted EBS snapshots including all application storage, then test restoration on a separate instance. SQLite and Qdrant need a consistent backup; copying live database files is not a reliable backup strategy. Rebuild using the previous reviewed Git revision to roll back application code, while retaining volumes. Schema changes may require restoring the matching database snapshot. Never use docker compose down -v unless deliberately deleting all stored demo data.

Check logs and disk space regularly. Monitor CPU, memory, latency and failed requests. Configure CloudWatch and budget alerts as needed. Stop EC2 when unused, remembering that EBS and some networking resources can continue billing. Production scaling needs a persistent job queue, shared database, user administration and independent security/clinical evaluation; multiple web replicas alone do not provide those capabilities.

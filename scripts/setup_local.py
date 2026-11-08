"""Configure a synthetic-data local Docker installation without overwriting existing settings."""
from __future__ import annotations
import argparse
import json
import secrets
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", action="store_true", help="Build and start the local Docker services")
    parser.add_argument("--verify", action="store_true", help="Check the already-running frontend and backend")
    parser.add_argument("--advanced", action="store_true", help="Enable and download optional pinned local transformers")
    parser.add_argument("--project-name", help="Existing Compose project name when upgrading, to preserve its volumes")
    args = parser.parse_args()
    if args.verify:
        try:
            with urllib.request.urlopen("http://localhost:8000/api/v1/health", timeout=15) as response:
                health = json.load(response)
            with urllib.request.urlopen("http://localhost:3000/preview", timeout=15) as response:
                frontend_ok = response.status == 200
            with urllib.request.urlopen("http://localhost:8000/api/v1/auth/config", timeout=15) as response:
                auth = json.load(response)
            report = {"backend": health, "frontend_available": frontend_ok,
                      "passwordless_configured": auth.get("configured", False),
                      "live_email_sign_in_verified": False, "medical_accuracy_98_validated": False}
            print(json.dumps(report, indent=2))
            if not auth.get("configured"):
                print("Services can run, but sign-in needs your WorkOS client and organization IDs. See docs/PASSWORDLESS_ACCESS.md.")
            return int(not (frontend_ok and health.get("qdrant_connected") and health.get("whisper_loaded") and auth.get("configured")))
        except Exception as exc:
            print(f"Verification could not complete: {exc}. Check docker compose ps and docker compose logs --tail=100 backend.")
            return 1
    if not shutil.which("docker"):
        print("Install Docker Desktop (Windows/macOS) or Docker Engine with Compose (Linux), then run this command again.")
        return 1
    if subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        print("Docker is not ready. Start Docker Desktop/Engine, wait until ready, then rerun.")
        return 1
    if subprocess.run(["docker", "compose", "version"], capture_output=True).returncode:
        print("Docker Compose v2 is required.")
        return 1
    target = ROOT / "backend/.env"
    if not target.exists():
        content = (ROOT / "backend/.env.example").read_text(encoding="utf-8")
        content = content.replace("change-me-to-a-random-256-bit-secret", secrets.token_hex(32))
        content = content.replace("change-me-to-another-random-256-bit-secret", secrets.token_hex(32))
        # Exclusive creation protects a concurrently created configuration.
        with target.open("x", encoding="utf-8") as handle:
            handle.write(content)
        print("Created backend/.env with two independent random secrets.")
    else:
        print("Using existing backend/.env.")
    if "change-me-to-" in target.read_text(encoding="utf-8"):
        print("The existing backend/.env still contains placeholder secrets. Set APP_SECRET_KEY and JWT_SECRET_KEY to separate random values before starting.")
        return 1
    if args.advanced:
        content = target.read_text(encoding="utf-8")
        content = re.sub(r"(?m)^ADVANCED_NLP_ENABLED=.*$", "ADVANCED_NLP_ENABLED=true", content) if re.search(r"(?m)^ADVANCED_NLP_ENABLED=", content) else content.rstrip()+"\nADVANCED_NLP_ENABLED=true\n"
        target.write_text(content, encoding="utf-8")
    # One configuration source supplies BOTH backend settings and frontend build args.
    compose = ["docker", "compose", "--env-file", str(target)]
    if args.project_name:
        compose += ["-p", args.project_name]
    result = subprocess.run(compose+["config", "--quiet"], cwd=ROOT)
    if result.returncode:
        return result.returncode
    if args.start:
        result = subprocess.run(compose+["build"], cwd=ROOT)
        if result.returncode:
            return result.returncode
        if args.advanced:
            result = subprocess.run(compose+["run", "--rm", "--no-deps", "backend", "python", "prepare_advanced_models.py"], cwd=ROOT)
            if result.returncode:
                return result.returncode
        result = subprocess.run(compose+["up", "-d"], cwd=ROOT)
        if result.returncode:
            return result.returncode
        print("Open http://localhost:3000. Allow time for first model downloads, then run this script with --verify.")
    else:
        print("Configuration checked. Run with --start to build and launch the app.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

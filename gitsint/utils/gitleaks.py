import json
import os
import platform
import subprocess
import tarfile
import zipfile
from io import BytesIO

import requests

GITLEAKS_VERSION = "8.25.1"
GITLEAKS_DIR = os.path.join(os.path.dirname(__file__), "../tools/gitleaks")
GITLEAKS_BIN = os.path.join(GITLEAKS_DIR, "gitleaks")


def setup_gitleaks():
    if os.path.exists(GITLEAKS_BIN):
        return GITLEAKS_BIN

    print("[*] Gitleaks not found. Downloading...")

    system = platform.system().lower()
    machine = platform.machine().lower()
    ext = "zip" if system == "windows" else "tar.gz"

    if "x86_64" in machine or "amd64" in machine:
        arch = "x64"
    elif "arm64" in machine or "aarch64" in machine:
        arch = "arm64"
    elif "armv7" in machine:
        arch = "armv7"
    elif "armv6" in machine:
        arch = "armv6"
    else:
        raise Exception(f"Unsupported architecture: {machine}")

    filename = f"gitleaks_{GITLEAKS_VERSION}_{system}_{arch}.{ext}"
    url = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}/{filename}"

    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Failed to download Gitleaks: {url}")

    os.makedirs(GITLEAKS_DIR, exist_ok=True)

    if ext == "zip":
        with zipfile.ZipFile(BytesIO(resp.content)) as zip_ref:
            zip_ref.extractall(GITLEAKS_DIR)
    else:
        with tarfile.open(fileobj=BytesIO(resp.content), mode="r:gz") as tar_ref:
            tar_ref.extractall(GITLEAKS_DIR)

    if system != "windows":
        os.chmod(GITLEAKS_BIN, 0o755)

    print(f"[+] Gitleaks installed at {GITLEAKS_BIN}")
    return GITLEAKS_BIN


def run_gitleaks_scan(repo_path):
    bin_path = setup_gitleaks()
    try:
        result = subprocess.run(
            [
                bin_path,
                "detect",
                "--source",
                repo_path,
                "--no-banner",
                "--report-format",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        # Handle cases where gitleaks failed completely
        if result.returncode not in (0, 1):
            print(f"❌ Gitleaks error on {repo_path}:\n{result.stderr.strip()}")
            return []

        # Handle empty or invalid JSON output
        if not result.stdout.strip():
            print(f"❌ Gitleaks returned empty output for {repo_path}")
            return []

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            print(
                f"❌ Gitleaks returned invalid JSON for {repo_path}:\n{result.stdout}"
            )
            return []

    except Exception as e:
        print(f"❌ Exception while running Gitleaks on {repo_path}: {e}")
        return []

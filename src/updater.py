import time
import json
import shutil
import tempfile
import urllib.request
import urllib.error
import zipfile
from pathlib import Path

REPO = "MariosMoraitis/SQL-Alter-Tool"
CURRENT_VERSION_FILE = Path(__file__).parent.parent / "VERSION"

# Files/folders never to touch, even if they exist in the zip
PRESERVE = {"VERSION", ".venv", "venv", "__pycache__", ".git"}

CACHE_FILE = Path(__file__).parent.parent / ".update_check_cache"
CHECK_INTERVAL = 60 * 60 * 6    # 6 hours

def should_check() -> bool:

    if not CACHE_FILE.exists():
        return True

    las_check = float(CACHE_FILE.read_text().strip() or 0)
    return (time.time() - las_check) > CHECK_INTERVAL

def mark_checked():
    CACHE_FILE.write_text(str(time.time()))

def get_current_version() -> str:

    if CURRENT_VERSION_FILE.exists():
        return CURRENT_VERSION_FILE.read_text().strip()

    return "0.0.0"

def get_latest_release() -> dict:

    try:
        url = f"https://api.github.com/repos/{REPO}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "sql-alter-tool-updater"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.load(resp)

    except urllib.error.HTTPError as e:
        print("Status:", e.code)    
        print("Remaining:", e.headers.get("X-RateLimit-Remaining"))
        print("Reset at (unix):", e.headers.get("X-RateLimit-Reset"))
        print("Body:", e.read().decode())
        raise

def download_n_extract(zip_url: str, dest_dir: Path):

    try:
        req = urllib.request.Request(
            zip_url,
            headers={"User-Agent": "sql-alter-tool-updater"}
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

    except urllib.error.HTTPError as e:
            print("Status:", e.code)    
            print("Remaining:", e.headers.get("X-RateLimit-Remaining"))
            print("Reset at (unix):", e.headers.get("X-RateLimit-Reset"))
            print("Body:", e.read().decode())
            raise

    zip_path = dest_dir / "update.zip"
    zip_path.write_bytes(data)

    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest_dir)

    zip_path.unlink()

    # GitHub zips extract into a single top-level folder like "repo-1.1.0/"
    extracted_root = next(p for p in dest_dir.iterdir() if p.is_dir())
    return extracted_root

def apply_update(extracted_root: Path, project_root: Path):

    for item in extracted_root.iterdir():
        if item.name in PRESERVE:
            continue

        target = project_root / item.name
        if target.exists():
            shutil.rmtree(target) if target.is_dir() else target.unlink()

        shutil.move(str(item), str(target))

def update():

    current = get_current_version()
    print(f'Current version: {current}')

    if not should_check():
        return

    mark_checked()
    print("Checking for updates...")
    try:
        release = get_latest_release()
    except Exception as e:
        print(f'Could not check for updates: {str(e)}')
        return

    latest = release["tag_name"].lstrip("v")
    if latest == current:
        print("Up to date!")
        return

    print(f'New version available: {latest}')
    confirm = input("Download and install? [y/N]\n> ").strip().lower()
    if confirm != 'y':
        print('Skipped...')
        return

    zip_url = release["zipball_url"]
    project_root = Path(__file__).parent.parent

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        print('Downloading...')
        extracted_root = download_n_extract(zip_url, tmp_path)
        print('Applying update...')
        apply_update(extracted_root, project_root)

    CURRENT_VERSION_FILE.write_text(latest)
    print(f"Updated v{latest}!")
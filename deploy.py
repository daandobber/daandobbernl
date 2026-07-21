#!/usr/bin/env python3
"""
Deploy script voor daandobber.nl
Upload dist folder naar VPS via FTP
"""

import os
import ftplib
from pathlib import Path

# FTP credentials are read from the environment and must never be committed.
FTP_HOST = os.environ.get("FTP_HOST", "")
FTP_USER = os.environ.get("FTP_USER", "")
FTP_PASS = os.environ.get("FTP_PASS", "")
REMOTE_DIR = os.environ.get("FTP_REMOTE_DIR", "httpdocs/dist")
LOCAL_DIR = "dist"

def upload_file(ftp, local_path, remote_path):
    """Upload een enkel bestand"""
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f"[OK] {remote_path}")

def ensure_remote_dir(ftp, path):
    """Zorg dat remote directory bestaat"""
    if not path:
        return

    dirs = path.split('/')
    current_path = ''

    for d in dirs:
        if not d:
            continue
        current_path = f"{current_path}/{d}" if current_path else d

        try:
            # Probeer naar directory te gaan
            ftp.cwd(f"/{current_path}")
        except:
            # Directory bestaat niet, maak aan
            try:
                ftp.mkd(f"/{current_path}")
            except:
                pass  # Directory bestaat al of kan niet aangemaakt worden

    # Ga terug naar root
    try:
        ftp.cwd('/')
    except:
        pass

def upload_directory(ftp, local_dir, remote_dir):
    """Upload een hele directory recursief"""
    local_path = Path(local_dir)

    for item in local_path.rglob('*'):
        if item.is_file():
            # Bereken relative path
            rel_path = item.relative_to(local_path)
            remote_path = f"{remote_dir}/{str(rel_path).replace(os.sep, '/')}"

            # Zorg dat de remote directory bestaat
            remote_file_dir = '/'.join(remote_path.split('/')[:-1])
            ensure_remote_dir(ftp, remote_file_dir)

            # Upload het bestand
            try:
                upload_file(ftp, str(item), remote_path)
            except Exception as e:
                # Skip encoding errors
                try:
                    error_msg = str(e)
                    print(f"[ERROR] Fout bij {remote_path}: {error_msg}")
                except:
                    print(f"[ERROR] Fout bij upload (encoding issue)")

def main():
    if not all((FTP_HOST, FTP_USER, FTP_PASS)):
        raise RuntimeError("Set FTP_HOST, FTP_USER and FTP_PASS before deploying")
    # Check of dist folder bestaat
    if not os.path.exists(LOCAL_DIR):
        print("[ERROR] dist/ folder bestaat niet. Run eerst: npm run build")
        return

    print("Start deployment naar daandobber.nl...")
    print(f"Upload {LOCAL_DIR}/ naar {REMOTE_DIR}/")

    # Verbind met FTP
    try:
        ftp = ftplib.FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("[OK] Verbonden met FTP server")

        # Upload dist directory
        upload_directory(ftp, LOCAL_DIR, REMOTE_DIR)

        ftp.quit()
        print("\n[SUCCESS] Deployment succesvol!")
        print("Check: https://daandobber.nl")

    except Exception as e:
        print(f"[ERROR] Deployment gefaald: {e}")

if __name__ == "__main__":
    main()

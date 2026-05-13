#!/usr/bin/env python3
"""Upload lesson PDFs to Google Drive via the Drive v3 API (service-account auth).

What this does
--------------
Given a lesson number and PDF paths, this script uploads to TWO separate
Google Drive folders:

  1. Student PDFs (Notes_*_SHARED.pdf, Materials_Camillo.pdf,
     Materials_Luciana.pdf) → STUDENT_FOLDER_ID / Lesson_NN subfolder
  2. Teacher PDF (Lesson_NN_teacher.pdf) → TEACHER_FOLDER_ID (flat, no subfolder)

If a file with the same name already exists in the target location, its
contents are updated in place so Drive share links stay stable.

Prints a JSON summary with student_subfolder_url and teacher_file_url.

Why service account
-------------------
No browser, no OAuth consent flow, no 7-day refresh-token expiry. Fully
non-interactive, safe to run headless. The trade-off: files uploaded this
way are *owned* by the service account, not by you. They still appear in
your Drive via the shared parent folders, but the "Owner" column shows the
service account's email. For regenerable lesson PDFs this is fine.

First-time setup (one-time, on your Mac)
----------------------------------------
  1. Go to https://console.cloud.google.com and create or pick a project.
  2. Enable the Google Drive API (APIs & Services > Library > "Google
     Drive API" > Enable).
  3. Create a service account:
       IAM & Admin > Service Accounts > "+ Create service account"
       Name: e.g. `english-tutoring-uploader`
       Skip the optional role-granting and user-access steps.
  4. Create a JSON key for the service account:
       Click the new service account > Keys tab > Add Key > Create new key
       > JSON > Create. The key file downloads to ~/Downloads.
  5. Move the key into place on this machine:
       mkdir -p ~/.config/create-lesson
       mv ~/Downloads/<key-file>.json ~/.config/create-lesson/service_account.json
       chmod 600 ~/.config/create-lesson/service_account.json
  6. Share BOTH Drive folders with the service account:
       - Copy the service account email (looks like
         english-tutoring-uploader@<project>.iam.gserviceaccount.com).
       - Open each parent Drive folder in the browser.
       - Click Share, paste the SA email, set role to "Editor", uncheck
         "Notify people", and click Share.

That is the whole setup. No consent flow, no token to refresh.

Security note
-------------
The JSON key grants full Drive access for anything that service account
can see. Keep the file outside any version-controlled directory. The
default location (~/.config/create-lesson/) is outside the project folder
for exactly this reason.

Dependencies
------------
  pip install --break-system-packages google-api-python-client google-auth-httplib2

Usage
-----
  python3 upload_to_drive.py \\
      --lesson 5 \\
      --student-pdf "/Users/shaneorr/Documents/English/Student Materials/Lesson_05/Notes_POSSESSIVES_SHARED.pdf" \\
      --student-pdf "/Users/shaneorr/Documents/English/Student Materials/Lesson_05/Materials_Camillo.pdf" \\
      --student-pdf "/Users/shaneorr/Documents/English/Student Materials/Lesson_05/Materials_Luciana.pdf" \\
      --teacher-pdf "/Users/shaneorr/Documents/English/Teacher Materials/Lesson_05_teacher.pdf"

Drive destinations
------------------
  Student PDFs → folder 1yO_leuifYFIMZItGECZ1BaqJ1nI2CJ1F / Lesson_NN subfolder
  Teacher PDF  → folder 1eIHmpZ7PQIKBLsi2WPhOcE4ItFOLXr_q (flat, no subfolder)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError as e:
    missing = getattr(e, "name", "a google-api library")
    sys.exit(
        f"Missing dependency: {missing}\n"
        "Install with:\n"
        "  pip install --break-system-packages google-api-python-client "
        "google-auth-httplib2"
    )


SCOPES = ["https://www.googleapis.com/auth/drive"]
CONFIG_DIR = Path.home() / ".config" / "create-lesson"
SA_KEY_PATH = CONFIG_DIR / "service_account.json"
FOLDER_MIME = "application/vnd.google-apps.folder"

# Student PDFs go here, inside a Lesson_NN subfolder.
STUDENT_FOLDER_ID = "1yO_leuifYFIMZItGECZ1BaqJ1nI2CJ1F"

# Teacher PDF goes here, flat (no subfolder).
TEACHER_FOLDER_ID = "1eIHmpZ7PQIKBLsi2WPhOcE4ItFOLXr_q"


def get_credentials() -> service_account.Credentials:
    if not SA_KEY_PATH.exists():
        sys.exit(
            f"Missing service account key at {SA_KEY_PATH}.\n"
            "Create a service account in Google Cloud Console, download its "
            "JSON key, save it there, and share BOTH target Drive folders with "
            "the service account's email. See the docstring at the top of "
            "this script for the full walkthrough."
        )
    return service_account.Credentials.from_service_account_file(
        str(SA_KEY_PATH), scopes=SCOPES
    )


def escape_drive_query(value: str) -> str:
    """Escape single quotes and backslashes for a Drive `q` parameter string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def find_or_create_subfolder(service, parent_id: str, name: str) -> tuple[str, str]:
    """Return (folder_id, action) where action is 'found' or 'created'."""
    q_name = escape_drive_query(name)
    q_parent = escape_drive_query(parent_id)
    query = (
        f"'{q_parent}' in parents "
        f"and name = '{q_name}' "
        f"and mimeType = '{FOLDER_MIME}' "
        f"and trashed = false"
    )
    resp = (
        service.files()
        .list(
            q=query,
            fields="files(id, name)",
            pageSize=10,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    existing = resp.get("files", [])
    if existing:
        return existing[0]["id"], "found"
    meta = {
        "name": name,
        "mimeType": FOLDER_MIME,
        "parents": [parent_id],
    }
    folder = (
        service.files()
        .create(body=meta, fields="id", supportsAllDrives=True)
        .execute()
    )
    return folder["id"], "created"


def upload_pdf(service, folder_id: str, pdf_path: Path) -> dict:
    """Upload or update a PDF in the given Drive folder."""
    q_folder = escape_drive_query(folder_id)
    q_name = escape_drive_query(pdf_path.name)
    query = (
        f"'{q_folder}' in parents "
        f"and name = '{q_name}' "
        f"and trashed = false"
    )
    resp = (
        service.files()
        .list(
            q=query,
            fields="files(id, name)",
            pageSize=5,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        )
        .execute()
    )
    existing = resp.get("files", [])
    media = MediaFileUpload(str(pdf_path), mimetype="application/pdf", resumable=False)
    if existing:
        file_id = existing[0]["id"]
        updated = (
            service.files()
            .update(
                fileId=file_id,
                media_body=media,
                fields="id, webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )
        return {
            "id": updated["id"],
            "name": pdf_path.name,
            "web_view_link": updated.get("webViewLink"),
            "action": "updated",
        }
    meta = {"name": pdf_path.name, "parents": [folder_id]}
    created = (
        service.files()
        .create(
            body=meta,
            media_body=media,
            fields="id, webViewLink",
            supportsAllDrives=True,
        )
        .execute()
    )
    return {
        "id": created["id"],
        "name": pdf_path.name,
        "web_view_link": created.get("webViewLink"),
        "action": "created",
    }


def drive_hint(creds, status) -> str:
    if status in (403, 404):
        return (
            "\nHint: a 403/404 here usually means the Drive folder has not "
            "been shared with the service account. Share both folders with "
            f"{creds.service_account_email!r} as Editor and retry."
        )
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upload lesson PDFs to two Google Drive folders using a service account.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--lesson",
        type=int,
        required=True,
        help="Lesson number (e.g. 5). Student subfolder named Lesson_NN (zero-padded).",
    )
    parser.add_argument(
        "--student-pdf",
        action="append",
        dest="student_pdfs",
        metavar="PATH",
        help=(
            "Local path to a student-facing PDF (Notes or Materials). "
            "Repeat for multiple files. Uploaded to STUDENT_FOLDER_ID/Lesson_NN/."
        ),
    )
    parser.add_argument(
        "--teacher-pdf",
        dest="teacher_pdf",
        metavar="PATH",
        help=(
            "Local path to the teacher lesson plan PDF. "
            "Uploaded flat into TEACHER_FOLDER_ID (no subfolder)."
        ),
    )
    args = parser.parse_args()

    if not 1 <= args.lesson <= 99:
        sys.exit("Lesson number must be between 1 and 99.")
    if not args.student_pdfs and not args.teacher_pdf:
        sys.exit("Provide at least one --student-pdf or --teacher-pdf.")

    student_paths = [Path(p).expanduser().resolve() for p in (args.student_pdfs or [])]
    teacher_path = Path(args.teacher_pdf).expanduser().resolve() if args.teacher_pdf else None

    missing = [p for p in student_paths if not p.is_file()]
    if teacher_path and not teacher_path.is_file():
        missing.append(teacher_path)
    if missing:
        sys.exit("Missing file(s):\n  " + "\n  ".join(str(p) for p in missing))

    creds = get_credentials()
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    subfolder_name = f"Lesson_{args.lesson:02d}"
    result: dict = {"lesson": subfolder_name, "uploaded_by": creds.service_account_email}

    # --- Student PDFs → STUDENT_FOLDER_ID / Lesson_NN subfolder ---
    if student_paths:
        try:
            subfolder_id, folder_action = find_or_create_subfolder(
                service, STUDENT_FOLDER_ID, subfolder_name
            )
            student_files = [upload_pdf(service, subfolder_id, p) for p in student_paths]
        except HttpError as e:
            status = getattr(getattr(e, "resp", None), "status", None)
            sys.exit(f"Google Drive API error (student folder): {e}{drive_hint(creds, status)}")

        result["student_subfolder_name"] = subfolder_name
        result["student_subfolder_id"] = subfolder_id
        result["student_subfolder_url"] = f"https://drive.google.com/drive/folders/{subfolder_id}"
        result["student_subfolder_action"] = folder_action
        result["student_files"] = student_files

    # --- Teacher PDF → TEACHER_FOLDER_ID (flat) ---
    if teacher_path:
        try:
            teacher_file = upload_pdf(service, TEACHER_FOLDER_ID, teacher_path)
        except HttpError as e:
            status = getattr(getattr(e, "resp", None), "status", None)
            sys.exit(f"Google Drive API error (teacher folder): {e}{drive_hint(creds, status)}")

        result["teacher_folder_id"] = TEACHER_FOLDER_ID
        result["teacher_folder_url"] = f"https://drive.google.com/drive/folders/{TEACHER_FOLDER_ID}"
        result["teacher_file"] = teacher_file

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

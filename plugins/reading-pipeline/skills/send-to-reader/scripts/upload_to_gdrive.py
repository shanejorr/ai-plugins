#!/usr/bin/env python3
"""
Upload a file to a specific Google Drive folder using the Google Drive API.

Folder IDs are read from a `folders.json` file keyed by device name (e.g.
"kobo", "remarkable") so personal folder IDs do not live in this script.
The script looks for the file in this order:

    1. --folders-config PATH                       (CLI flag)
    2. $READING_PIPELINE_FOLDERS_CONFIG            (environment variable)
    3. ~/.config/send-to-reader/folders.json       (preferred — survives plugin upgrades)
    4. <skill>/config/folders.json                 (legacy in-tree location)

The user-config path is preferred because the in-tree copy is wiped
whenever the plugin is reinstalled or upgraded.

OAuth credentials and the cached refresh token live in an out-of-tree
directory: `~/.config/gdrive-oauth/`.

Usage:
    python upload_to_gdrive.py <file_path> --device kobo
    python upload_to_gdrive.py <file_path> --device remarkable
    python upload_to_gdrive.py <file_path> --folder-id <FOLDER_ID>   # explicit override

Setup:
    1. mkdir -p ~/.config/gdrive-oauth && chmod 700 ~/.config/gdrive-oauth
    2. Go to https://console.cloud.google.com/
    3. Create a project (or use existing) and enable the Google Drive API
    4. APIs & Services > OAuth consent screen: include the scope
       `https://www.googleapis.com/auth/drive`
    5. Create OAuth 2.0 credentials of type "Desktop app"
    6. Download the credentials JSON and save it as
       ~/.config/gdrive-oauth/gdrive_credentials.json
    7. Copy <skill-dir>/config/folders.example.json into your user-config
       directory and fill in your folder IDs:
           mkdir -p ~/.config/send-to-reader
           cp config/folders.example.json ~/.config/send-to-reader/folders.json
       (The user-config path is preferred over the in-tree config/ path
       because the latter is wiped on plugin upgrade.)
    8. On first run, a browser opens for OAuth consent. The token is then
       cached in ~/.config/gdrive-oauth/gdrive_token.pickle for reuse.
"""

import argparse
import json
import os
import pickle
import sys

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError:
    print("ERROR: Google API packages not installed. Run:")
    print("  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib --break-system-packages")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/drive"]

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CREDENTIALS_PATH = os.path.expanduser(
    "~/.config/gdrive-oauth/gdrive_credentials.json"
)
DEFAULT_TOKEN_PATH = os.path.expanduser(
    "~/.config/gdrive-oauth/gdrive_token.pickle"
)
USER_CONFIG_FOLDERS = os.path.expanduser("~/.config/send-to-reader/folders.json")
INTREE_FOLDERS_CONFIG = os.path.join(SKILL_DIR, "config", "folders.json")
EXAMPLE_FOLDERS_CONFIG = os.path.join(SKILL_DIR, "config", "folders.example.json")


def resolve_folders_config(cli_value):
    """Pick the folders.json path: CLI > env var > user-config > in-tree.

    Returns the first path that exists, or the highest-priority default
    so error messages point at the preferred location.
    """
    if cli_value:
        return cli_value
    env_value = os.environ.get("READING_PIPELINE_FOLDERS_CONFIG")
    if env_value:
        return env_value
    if os.path.exists(USER_CONFIG_FOLDERS):
        return USER_CONFIG_FOLDERS
    if os.path.exists(INTREE_FOLDERS_CONFIG):
        return INTREE_FOLDERS_CONFIG
    return USER_CONFIG_FOLDERS


def resolve_folder_id(device: str, folders_config_path: str) -> str:
    if not os.path.exists(folders_config_path):
        print(f"ERROR: Folders config not found at {folders_config_path}")
        print(f"Copy the template and fill in your folder IDs:")
        print(f"  mkdir -p {os.path.dirname(USER_CONFIG_FOLDERS)}")
        print(f"  cp {EXAMPLE_FOLDERS_CONFIG} {USER_CONFIG_FOLDERS}")
        print(f"Then open each device's Drive folder in a browser and copy the")
        print(f"folder ID (the last segment of the URL) into the JSON.")
        print(f"The user-config path above is preferred — the in-tree plugin")
        print(f"config is wiped on every plugin upgrade.")
        sys.exit(1)

    with open(folders_config_path, "r") as f:
        folders = json.load(f)

    if device not in folders:
        print(f"ERROR: Device '{device}' not found in {folders_config_path}.")
        print(f"Known devices: {', '.join(folders.keys()) or '(none)'}")
        print(f"Add an entry for '{device}' or pick one of the known devices.")
        sys.exit(1)

    folder_id = folders[device]
    if not folder_id or folder_id.startswith("REPLACE_"):
        print(f"ERROR: Folder ID for device '{device}' is unset in {folders_config_path}.")
        print(f"Open the device's Drive folder in a browser and copy the folder ID")
        print(f"(the last segment of the URL) into the JSON file.")
        sys.exit(1)

    return folder_id


def get_credentials(credentials_path: str, token_path: str) -> Credentials:
    creds = None
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"ERROR: OAuth credentials file not found at {credentials_path}")
                print("See the setup instructions in this script's docstring.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "wb") as f:
            pickle.dump(creds, f)

    return creds


def upload_file(
    file_path: str,
    folder_id: str,
    device_label: str,
    credentials_path: str,
    token_path: str,
) -> str:
    creds = get_credentials(credentials_path, token_path)
    service = build("drive", "v3", credentials=creds)

    file_name = os.path.basename(file_path)
    if file_path.endswith(".epub") or file_path.endswith(".kepub.epub"):
        mime_type = "application/epub+zip"
    elif file_path.endswith(".pdf"):
        mime_type = "application/pdf"
    else:
        mime_type = "application/octet-stream"

    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, name, webViewLink",
        ).execute()
    except HttpError as e:
        status = getattr(e.resp, "status", None)
        if status in ("404", 404):
            print(
                f"ERROR: Google Drive folder '{folder_id}' (device: {device_label}) "
                f"was not found. Edit your folders.json (see --folders-config) and "
                f"replace the '{device_label}' value with a valid folder ID, or "
                f"check that the OAuth account you authorized actually has access "
                f"to that folder."
            )
            sys.exit(1)
        if status in ("403", 403):
            print(
                f"ERROR: Permission denied uploading to folder '{folder_id}' "
                f"(device: {device_label}). The OAuth account you authorized may "
                f"not have write access to that folder. Re-share the folder, "
                f"or update your folders.json (see --folders-config) with a "
                f"folder you own."
            )
            sys.exit(1)
        raise

    print(f"Uploaded: {file.get('name')}")
    print(f"Device:   {device_label}")
    print(f"File ID:  {file.get('id')}")
    print(f"Link:     {file.get('webViewLink')}")
    return file.get("id")


def main():
    parser = argparse.ArgumentParser(description="Upload a file to a Google Drive folder")
    parser.add_argument("file", help="Path to file to upload")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--device",
        help="Device key in folders.json (e.g. 'kobo', 'remarkable')",
    )
    group.add_argument(
        "--folder-id",
        help="Explicit Google Drive folder ID (bypasses folders.json lookup)",
    )
    parser.add_argument(
        "--folders-config",
        default=None,
        help=(
            "Path to folders.json. If omitted, the script searches: "
            "$READING_PIPELINE_FOLDERS_CONFIG → "
            f"{USER_CONFIG_FOLDERS} → {INTREE_FOLDERS_CONFIG}"
        ),
    )
    parser.add_argument(
        "--credentials",
        default=os.environ.get("GDRIVE_CREDENTIALS", DEFAULT_CREDENTIALS_PATH),
        help="Path to OAuth credentials JSON",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GDRIVE_TOKEN", DEFAULT_TOKEN_PATH),
        help="Path to saved auth token",
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    if args.device:
        folders_config_path = resolve_folders_config(args.folders_config)
        folder_id = resolve_folder_id(args.device, folders_config_path)
        device_label = args.device
    else:
        folder_id = args.folder_id
        device_label = "explicit folder-id"

    upload_file(args.file, folder_id, device_label, args.credentials, args.token)


if __name__ == "__main__":
    main()

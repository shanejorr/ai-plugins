---
name: send-to-reader
description: "Upload a PDF, EPUB, or KEPUB file to the user's Google Drive folder that syncs to their e-reader (Kobo Color or reMarkable Paper Pro). Use this skill whenever the user wants to send a document to their e-reader, sync a file to Kobo or reMarkable, or 'put this on my e-reader'. Trigger phrases include 'send to my Kobo', 'send to my reMarkable', 'sync this to my e-reader', 'upload this to my reader', or any time the user has a .pdf / .epub / .kepub.epub file and mentions Kobo, reMarkable, or Google Drive sync. Asks which device if not specified."
---

# Send to Reader Skill

## Purpose

Upload a `.pdf`, `.epub`, or `.kepub.epub` file to a Google Drive folder that syncs to one of the user's e-readers:

- **Kobo Color**
- **reMarkable Paper Pro**

Each device watches its own Drive folder. Folder IDs live in a gitignored config file (`config/folders.json`) so they can be shared on a public marketplace without leaking personal Drive locations.

## Step 1: Confirm the Input File

Verify the file exists and has a supported extension. Acceptable:
- `.pdf`
- `.epub`
- `.kepub.epub`

If the file is none of these, tell the user and stop. If they want to convert something to EPUB or KEPUB first, point them to the `convert-to-epub` skill.

## Step 2: Confirm the Target Device

If the user did not specify which device to send to, **ask**: Kobo or reMarkable.

The script accepts the device key (`kobo` or `remarkable`) and looks up the folder ID in `<skill-dir>/config/folders.json`.

## Step 3: Upload via Google Drive API

Install dependencies once:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib --break-system-packages
```

Run:

```bash
python <skill-path>/scripts/upload_to_gdrive.py <file_path> --device <kobo|remarkable>
```

The script:
- Reads the folder ID for the chosen device from `<skill-dir>/config/folders.json`.
- Reads OAuth client credentials from `<skill-dir>/credentials/gdrive_credentials.json`.
- Caches the refresh token at `<skill-dir>/credentials/gdrive_token.pickle`.

After the first successful run, subsequent uploads are non-interactive.

## Step 4: First-Time Setup

If `config/folders.json` or `credentials/gdrive_credentials.json` is missing, the script prints a targeted error pointing to the example template. Walk the user through this once:

1. Open https://console.cloud.google.com/, create or pick a project, and enable the Google Drive API.
2. Create OAuth 2.0 credentials of type "Desktop app". Download the JSON.
3. Save that JSON as `<skill-dir>/credentials/gdrive_credentials.json`.
4. Copy `<skill-dir>/config/folders.example.json` to `<skill-dir>/config/folders.json` and fill in the folder IDs. To get a folder ID, open the folder in a browser and copy the last segment of the URL (`drive.google.com/drive/folders/<THIS_PART>`).
5. On the first run, a browser opens for OAuth consent. The token is then cached for reuse.

Full setup steps also live in `<skill-dir>/credentials/README.md`.

## Error Handling

The script surfaces specific, actionable messages:

- **Folder ID config missing** → tells the user to copy `folders.example.json`.
- **Device not in config** → lists known devices and asks the user to add the missing one.
- **Folder ID is the placeholder string** → tells the user to fill in the real ID.
- **OAuth credentials JSON missing** → points to the setup instructions.
- **Drive returns 404 on the parent folder** → "folder `<id>` (device: `<device>`) not found — edit `config/folders.json` or check OAuth account access."
- **Drive returns 403** → "permission denied — the OAuth account may not have write access; re-share the folder or update the config."

If you (the model) see one of these messages, relay the exact remediation to the user — don't just say "upload failed."

## Step 5: Confirm

After a successful upload, report briefly:
- The filename
- Which device folder it was uploaded to
- That it should appear on the device on its next sync

Do not dump file contents into the chat.

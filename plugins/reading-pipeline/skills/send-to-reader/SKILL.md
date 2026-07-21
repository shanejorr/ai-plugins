---
name: send-to-reader
description: "Upload a file to the user's Google Drive folder that syncs to their e-reader (Kobo Color or reMarkable Paper Pro). Accepts ready-to-go .pdf / .epub / .kepub.epub files, OR .txt / .md files that this skill will auto-convert into the right format for the chosen device (KEPUB for Kobo, EPUB for reMarkable). Use this skill whenever the user wants to send a document to their e-reader, sync a file to Kobo or reMarkable, or 'put this on my e-reader'. Trigger phrases include 'send to my Kobo', 'send to my reMarkable', 'sync this to my e-reader', 'upload this to my reader', 'send this text file to my Kobo/reMarkable'. Asks which device if not specified."
user-invocable: true
disable-model-invocation: false
---

# Send to Reader Skill

## Purpose

Upload a file to a Google Drive folder that syncs to one of the user's e-readers:

- **Kobo Color**
- **reMarkable Paper Pro**

Accepts e-reader-ready files (`.pdf`, `.epub`, `.kepub.epub`) directly, and also accepts plain text / Markdown (`.txt`, `.md`) — in which case this skill converts them to the right format for the target device before uploading.

Each device watches its own Drive folder. Folder IDs live in a gitignored config file (`config/folders.json`) so they can be shared on a public marketplace without leaking personal Drive locations.

## Step 1: Confirm the Input File

Verify the file exists and has a supported extension. Acceptable:
- `.pdf`, `.epub`, `.kepub.epub` — uploaded as-is.
- `.txt`, `.md` — auto-converted in Step 3 before upload.

If the file is something else, tell the user and stop.

## Step 2: Confirm the Target Device

If the user did not specify which device to send to, **ask**: Kobo or reMarkable.

The script accepts the device key (`kobo` or `remarkable`) and looks up the folder ID in `<skill-dir>/config/folders.json`.

## Step 3: Convert if Needed (.txt / .md only)

If the input is `.txt` or `.md`, convert it to the device-appropriate e-book format before upload:

- **Kobo** → `.kepub.epub` (unlocks Kobo reading stats, annotations, and improved typography)
- **reMarkable** → `.epub`

The converter auto-installs its dependencies (`ebooklib`, `markdown`) into
whichever Python runs it, so no manual install is normally needed. To
pre-install, or if you set `READING_PIPELINE_NO_AUTO_INSTALL=1` to disable
auto-install:

```bash
pip install ebooklib markdown --break-system-packages
```

Run the bundled converter from the sibling `convert-to-epub` skill. The output path's extension drives the format (`.kepub.epub` → KEPUB, `.epub` → EPUB):

```bash
# Kobo
python <plugin-root>/skills/convert-to-epub/scripts/md_to_epub.py <input.txt|input.md> /tmp/<basename>.kepub.epub

# reMarkable
python <plugin-root>/skills/convert-to-epub/scripts/md_to_epub.py <input.txt|input.md> /tmp/<basename>.epub --format epub
```

Notes:
- Derive `<basename>` as a snake_case version of the input filename, under ~60 chars.
- The script auto-detects the title from the first `# Heading` and the author from a `**Author(s):**` line. Override with `--title` / `--author` only if the user asks.
- For `.pdf`/`.epub`/`.kepub.epub` inputs, skip this step entirely.

Then use the converted file as the upload target in Step 4.

## Step 4: Upload via Google Drive API

The upload script auto-installs its Google API dependencies into whichever
Python runs it (keyed to `sys.executable`, so the install and the run can
never target different interpreters). No manual install is normally needed.
To pre-install, or if you set `READING_PIPELINE_NO_AUTO_INSTALL=1` to disable
auto-install:

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib --break-system-packages
```

Run:

```bash
python <skill-path>/scripts/upload_to_gdrive.py <file_path> --device <kobo|remarkable>
```

The script:
- Reads the folder ID for the chosen device from `~/.config/send-to-reader/folders.json` (falling back to `<skill-dir>/config/folders.json`).
- Reads OAuth client credentials from `~/.config/gdrive-oauth/gdrive_credentials.json`.
- Caches the refresh token at `~/.config/gdrive-oauth/gdrive_token.pickle`.

After the first successful run, subsequent uploads are non-interactive.

## Step 5: First-Time Setup

If credentials or folders config are missing, the script prints a targeted error. Walk the user through this once:

1. Open https://console.cloud.google.com/, create or pick a project, and enable the Google Drive API.
2. Create OAuth 2.0 credentials of type "Desktop app". Download the JSON.
3. Save that JSON as `~/.config/gdrive-oauth/gdrive_credentials.json` (create the directory with `mkdir -p ~/.config/gdrive-oauth && chmod 700 ~/.config/gdrive-oauth`).
4. Copy `<skill-dir>/config/folders.example.json` to `~/.config/send-to-reader/folders.json` and fill in the folder IDs. To get a folder ID, open the folder in a browser and copy the last segment of the URL (`drive.google.com/drive/folders/<THIS_PART>`).
5. On the first run, a browser opens for OAuth consent. The token is then cached at `~/.config/gdrive-oauth/gdrive_token.pickle` for reuse.

## Error Handling

The script surfaces specific, actionable messages:

- **Folder ID config missing** → tells the user to copy `folders.example.json`.
- **Device not in config** → lists known devices and asks the user to add the missing one.
- **Folder ID is the placeholder string** → tells the user to fill in the real ID.
- **OAuth credentials JSON missing** → points to the setup instructions.
- **Drive returns 404 on the parent folder** → "folder `<id>` (device: `<device>`) not found — edit `~/.config/send-to-reader/folders.json` or check OAuth account access."
- **Drive returns 403** → "permission denied — the OAuth account may not have write access; re-share the folder or update `~/.config/send-to-reader/folders.json`."

If you (the model) see one of these messages, relay the exact remediation to the user — don't just say "upload failed."

## Step 6: Confirm

After a successful upload, report briefly:
- The filename
- Which device folder it was uploaded to
- That it should appear on the device on its next sync

Do not dump file contents into the chat.

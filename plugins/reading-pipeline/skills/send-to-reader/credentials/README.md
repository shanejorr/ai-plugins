# OAuth credentials for `send-to-reader`

This directory holds the secrets the `send-to-reader` skill needs to upload
files to your Google Drive on your behalf. Everything here except this README
and `.gitkeep` is gitignored — you must set it up locally on each machine.

## What goes here

- `gdrive_credentials.json` — OAuth 2.0 client credentials downloaded from
  the Google Cloud Console. **Required.** Never commit.
- `gdrive_token.pickle` — refresh token cached automatically after the first
  successful OAuth consent. **Created automatically.** Never commit.

## One-time setup

1. Go to <https://console.cloud.google.com/> and either create a new project
   or pick an existing one.
2. In **APIs & Services → Library**, enable the **Google Drive API**.
3. In **APIs & Services → Credentials**, click **Create Credentials → OAuth
   client ID**. Pick application type **Desktop app**. Name it something
   like "Claude reading-pipeline".
4. Download the resulting JSON. Save it as:
   ```
   plugins/reading-pipeline/skills/send-to-reader/credentials/gdrive_credentials.json
   ```
5. Copy the folders template and fill in your folder IDs:
   ```
   cp ../config/folders.example.json ../config/folders.json
   ```
   To find a folder ID, open the folder in a browser and copy the last
   segment of the URL (`drive.google.com/drive/folders/<THIS_PART>`).
6. The first time the skill runs, a browser window opens for OAuth consent.
   Approve. The refresh token is then cached as `gdrive_token.pickle` and
   subsequent runs are non-interactive.

## Re-authorizing

If uploads start failing with auth errors, delete `gdrive_token.pickle` and
run the skill again. A fresh browser consent flow will produce a new token.

## Scopes

The script requests `https://www.googleapis.com/auth/drive.file`, which
limits access to files this app creates or that you explicitly open with it.
It cannot read or modify the rest of your Drive.

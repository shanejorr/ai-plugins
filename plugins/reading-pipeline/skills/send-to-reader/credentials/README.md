# OAuth credentials (moved out of tree)

OAuth credentials and the cached refresh token used to live in this directory.
They now live in a **shared out-of-tree location** at:

```
~/.config/gdrive-oauth/
    gdrive_credentials.json    # OAuth client JSON from Google Cloud Console
    gdrive_token.pickle        # Cached refresh token (auto-created on first run)
```

## One-time setup

1. `mkdir -p ~/.config/gdrive-oauth && chmod 700 ~/.config/gdrive-oauth`
2. Go to <https://console.cloud.google.com/> and either create a new project
   or pick an existing one.
3. In **APIs & Services → Library**, enable the **Google Drive API**.
4. In **APIs & Services → OAuth consent screen**, make sure the scope
   `https://www.googleapis.com/auth/drive.file` is included.
5. In **APIs & Services → Credentials**, click **Create Credentials → OAuth
   client ID**. Pick application type **Desktop app**. Name it something
   like "Claude personal Drive client".
6. Download the resulting JSON. Save it as:
   ```
   ~/.config/gdrive-oauth/gdrive_credentials.json
   ```
7. Copy this skill's folders template and fill in your folder IDs:
   ```
   cp ../config/folders.example.json ../config/folders.json
   ```
   To find a folder ID, open the folder in a browser and copy the last
   segment of the URL (`drive.google.com/drive/folders/<THIS_PART>`).
8. The first time either skill runs, a browser window opens for OAuth
   consent. Approve. The refresh token is then cached as
   `~/.config/gdrive-oauth/gdrive_token.pickle` and subsequent runs (in
   either plugin) are non-interactive.

## Re-authorizing

If uploads start failing with auth errors, delete
`~/.config/gdrive-oauth/gdrive_token.pickle` and run any skill that uses it.
A fresh browser consent flow will produce a new token.

OAuth refresh tokens for apps in Google Cloud Console **Testing** status
expire after 7 days. To avoid weekly re-consent, go to **OAuth consent
screen → Publish app**. For a personal Desktop client this is a one-click
action.

## Scopes

The scripts request `https://www.googleapis.com/auth/drive.file`, which
only grants access to files the app itself creates.

# Instagram Automated Uploader

A fully automated Python bot that logs into multiple Instagram accounts, scans a local `media` folder, and uploads all pending photos and videos using a persistent queue system.

It supports session cookies, persistent Chrome profiles, auto-generated captions (filename without extension), duplicate prevention, and automatic dismissal of browser popups.

---

## 📁 Project Structure

```text
automated/
│
├── bot.py                          # Main script (all logic)
├── accounts.json                   # User credentials
├── media/                          # Place images/videos here
│   ├── cat.jpg
│   ├── video.mp4
│   └── ...
│
├── instagram_bot.log               # Detailed logs (auto-generated)
├── post_queue_<username>.json      # Upload queue for each account
├── cookies_<username>.pkl          # Saved session cookies
└── chrome_profile_<username>/      # Persistent Chrome profile
```

---

## 🚀 Features

- ✅ Multi-account support
- ✅ Session persistence using cookies and Chrome profiles
- ✅ Automatic captions generated from filenames
- ✅ Persistent upload queue
- ✅ Duplicate prevention
- ✅ Automatic popup dismissal
- ✅ Progress counter during uploads
- ✅ Clean console output with detailed log file
- ✅ Supports both photos and videos
- ✅ Resume uploads after interruption

---

## 🛠 Requirements

- Python **3.7+**
- Google Chrome installed
- ChromeDriver (installed automatically via `webdriver-manager`)

Install dependencies:

```bash
pip install selenium webdriver-manager
```

The script also uses built-in Python modules:

- json
- os
- glob
- pickle
- logging
- pathlib
- random
- time

No additional installation is required.

---

# 🔧 Setup

## 1. Download the project

Clone or download this repository.

```text
automated/
```

---

## 2. Install dependencies

```bash
pip install selenium webdriver-manager
```

---

## 3. Create `accounts.json`

```json
{
    "my_account1": {
        "password": "your_password"
    },
    "my_account2": {
        "password": "another_password"
    }
}
```

> ⚠️ Never commit or share this file.

---

## 4. Add media

Create a folder named **media**

```text
media/
    cat.jpg
    sunset.png
    reel.mp4
```

Supported formats:

- jpg
- jpeg
- png
- bmp
- gif
- webp
- mp4
- mov
- avi

---

## 5. Run

```bash
python bot.py
```

---

# 🔄 Workflow

For every account the bot will:

1. Launch a dedicated Chrome profile.
2. Load saved cookies if available.
3. Log in if necessary.
4. Save fresh cookies.
5. Dismiss login popups.
6. Scan the `media` folder.
7. Update the upload queue.
8. Remove duplicate queue entries.
9. Upload all pending media.
10. Save upload status.
11. Wait a random interval.
12. Continue with the next account.

---

# 📋 Queue File Example

Example:

```json
[
    {
        "file": "cat.jpg",
        "status": "uploaded"
    },
    {
        "file": "video.mp4",
        "status": "pending"
    },
    {
        "file": "sunset.png",
        "status": "failed"
    }
]
```

### Status meanings

| Status | Meaning |
|---------|---------|
| pending | Will be uploaded next run |
| uploaded | Successfully uploaded |
| failed | Upload failed |

To retry a failed upload, simply change its status back to `"pending"`.

---

# ⚙ Configuration

Some useful settings inside `bot.py`:

| Variable | Description |
|----------|-------------|
| `ALLOWED_EXTENSIONS` | File extensions to scan |
| `max_upload_wait` | Maximum wait time for upload completion |
| `random.uniform(8, 15)` | Delay between uploads |

Increase the delay if you want slower, more human-like behaviour.

---

# ❓ Troubleshooting

### Captcha or Challenge

Instagram may occasionally require a captcha or verification.

Complete it manually in the opened browser.

The bot will continue afterwards.

---

### Login Failed

- Verify your username.
- Verify your password.
- Check whether the account has been locked.

---

### "Not now" popup still appears

Instagram occasionally changes popup layouts.

Add the new popup text inside the `dismiss_save_password_popup()` function if needed.

---

### Uploaded file still marked as pending

Make sure the script has permission to write files.

Check whether the queue JSON file is being updated correctly.

---

### Image upload takes too long

Possible reasons:

- Slow internet
- Large media files
- Instagram processing delay

The bot waits for either:

- Upload confirmation
- "Done" button
- Success toast

before proceeding.

---

# 📝 Logging

A detailed log is written to:

```text
instagram_bot.log
```

To display more information in the console, change:

```python
console_handler.setLevel(logging.WARNING)
```

to

```python
console_handler.setLevel(logging.INFO)
```

---

# 🔒 Security Notes

- Keep `accounts.json` private.
- Do not commit passwords to GitHub.
- Consider storing credentials in environment variables for production use.

---

# 📄 License

This project is provided for educational purposes only.

Use it at your own risk.

The authors are not responsible for any account restrictions, suspensions, or bans that may result from using this software.

---

# 🙋 Support

If you encounter issues:

1. Check `instagram_bot.log`.
2. Ensure your dependencies are up to date.
3. Verify that Instagram has not changed its interface.

Contributions and improvements are welcome.

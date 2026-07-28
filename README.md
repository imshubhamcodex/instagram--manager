# Instagram Automated Uploader

A Python automation tool that manages uploads for multiple Instagram accounts by maintaining a local upload queue. The project scans a media folder, keeps track of pending uploads, supports reusable browser sessions, and allows custom captions through text files.

> **Disclaimer:** This project is intended for educational and personal automation purposes only. Use it responsibly and ensure your usage complies with Instagram's Terms of Service.

---

# Features

- Multiple Instagram account support
- Persistent Chrome profiles for each account
- Session persistence using cookies
- Automatic media scanning
- Persistent upload queue per account
- Duplicate upload prevention
- Custom captions from text files
- Filename fallback captions
- Automatic dismissal of common Instagram popups
- Supports images and videos
- Resume uploads after interruption
- Detailed logging
- Human-like delays between uploads

---

# Project Structure

```
automated/
│
├── bot.py                          # Main application
├── accounts.json                   # Instagram credentials
│
├── media/                          # Images & videos to upload
│   ├── image.jpg
│   ├── reel.mp4
│   └── ...
│
├── caption/                        # Optional captions
│   ├── image.txt
│   ├── reel.txt
│   └── ...
│
├── cookies/                        # Auto-created
│   └── cookies_<username>.pkl
│
├── postque/                        # Auto-created
│   └── post_queue_<username>.json
│
├── chrome_profile_<username>/      # Auto-created Chrome profile
│
└── instagram_bot.log               # Runtime logs
```

The following folders are created automatically if they do not exist:

- `caption/`
- `cookies/`
- `postque/`
- `chrome_profile_<username>/`

You only need to create:

- `media/`
- `accounts.json`

---

# Requirements

- Python 3.7+
- Google Chrome
- Internet connection

Install required packages:

```bash
pip install selenium webdriver-manager
```

The project also uses built-in Python modules:

- json
- os
- glob
- pickle
- logging
- random
- pathlib
- time

---

# Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/instagram-automated-uploader.git

cd instagram-automated-uploader
```

Install dependencies.

```bash
pip install selenium webdriver-manager
```

---

# Configuration

## 1. Create `accounts.json`

```json
{
    "my_account_1": {
        "password": "password_here"
    },
    "my_account_2": {
        "password": "password_here"
    }
}
```

Never upload this file to GitHub.

---

## 2. Add Media

Create a folder named `media`.

Example:

```
media/
    cat.jpg
    sunset.png
    travel.mp4
```

Supported formats:

### Images

- jpg
- jpeg
- png
- bmp
- gif
- webp

### Videos

- mp4
- mov
- avi

---

## 3. Optional Captions

If a caption file exists with the same filename, it will be used.

Example:

```
media/
    cat.jpg

caption/
    cat.txt
```

Contents of `cat.txt`:

```
My favourite cat 🐱

#cats #pets #cute
```

If no text file exists, the caption becomes:

```
cat
```

(the filename without extension)

---

# Running

Simply execute:

```bash
python bot.py
```

The bot will automatically process every account listed inside `accounts.json`.

---

# Workflow

For every account the bot performs the following steps:

1. Launch a dedicated Chrome profile.
2. Load previously saved cookies.
3. Log in if required.
4. Save updated cookies.
5. Dismiss Instagram popups.
6. Scan the media directory.
7. Update the upload queue.
8. Remove duplicate queue entries.
9. Upload every pending file.
10. Save upload status.
11. Wait a random interval.
12. Continue with the next account.

---

# Queue System

Each account maintains its own upload queue.

Example:

```
postque/post_queue_username.json
```

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
        "file": "holiday.png",
        "status": "failed"
    }
]
```

## Status Values

| Status | Description |
|---------|-------------|
| pending | Waiting to upload |
| uploaded | Successfully uploaded |
| failed | Upload failed |

To retry a failed upload, simply change:

```json
"failed"
```

to

```json
"pending"
```

---

# Caption System

The uploader supports two caption modes.

## 1. Caption File

```
media/
    reel.mp4

caption/
    reel.txt
```

Contents:

```
Weekend vibes 🎬

#travel #reels
```

The contents of `reel.txt` become the Instagram caption.

---

## 2. Filename Fallback

If no text file exists,

```
media/
    mountain.mp4
```

Caption becomes:

```
mountain
```

---

# Logging

Every run creates or updates:

```
instagram_bot.log
```

To show more information in the console, change:

```python
console_handler.setLevel(logging.WARNING)
```

to

```python
console_handler.setLevel(logging.INFO)
```

---

# Configuration Options

Some useful values inside `bot.py`:

| Setting | Description |
|----------|-------------|
| ALLOWED_EXTENSIONS | Media file types |
| max_upload_wait | Maximum upload timeout |
| random.uniform(8, 15) | Delay between uploads |

Increasing the random delay results in slower, more natural upload behaviour.

---

# Troubleshooting

## Login Failed

- Verify your username.
- Verify your password.
- Check whether Instagram has locked the account.

---

## Verification Required

Instagram may occasionally require:

- Email verification
- SMS verification
- CAPTCHA
- Security challenge

Complete the verification manually inside the opened browser.

The session will be saved afterwards.

---

## Popup Still Appears

Instagram periodically changes its interface.

Update the popup text inside:

```
dismiss_save_password_popup()
```

if necessary.

---

## Upload Stuck

Possible causes:

- Slow internet
- Large video files
- Instagram processing delay

The bot waits for upload confirmation before continuing.

---

## Queue Not Updating

Ensure the script has permission to write inside:

```
postque/
```

Also verify the JSON file is not read-only.

---

# Security

- Never commit `accounts.json`.
- Never share passwords publicly.
- Consider using environment variables for production deployments.
- Keep cookie files private.

---

# Notes

- Chrome profiles are stored separately for every account.
- Sessions are automatically reused whenever possible.
- Queue files prevent duplicate uploads.
- Upload progress is preserved between runs.

---

# Disclaimer

This project is provided solely for educational purposes.

Users are responsible for ensuring that their use of this software complies with Instagram's Terms of Service and all applicable laws.

The author assumes no responsibility for account restrictions, suspensions, or any other consequences resulting from the use of this software.

---

# License

This project is released under the MIT License.

Feel free to modify and improve it for your own projects.

---

# Contributing

Contributions are welcome.

If you find a bug or have an improvement:

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Open a Pull Request.

---

# Author

Developed using Python, Selenium, and Chrome WebDriver.

If you found this project useful, consider giving it a ⭐ on GitHub.

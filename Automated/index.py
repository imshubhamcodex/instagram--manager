import json
import time
import random
import logging
import os
import pickle
import sys
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import tempfile

# Windows console encoding fix
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Logger configuration: INFO+ to file, WARNING+ to console
file_handler = logging.FileHandler('instagram_bot.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.WARNING)      # only warnings and errors on screen

logging.basicConfig(
    level=logging.INFO,                         # root level INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Suppress noisy third‑party loggers
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('WDM').setLevel(logging.WARNING)

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'mov', 'avi']

# ---------- NEW: Directory constants ----------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_DIR = os.path.join(SCRIPT_DIR, "cookies")
POSTQUEUE_DIR = os.path.join(SCRIPT_DIR, "postque")
CAPTION_DIR = os.path.join(SCRIPT_DIR, "caption")

# Ensure the directories exist
os.makedirs(COOKIES_DIR, exist_ok=True)
os.makedirs(POSTQUEUE_DIR, exist_ok=True)
os.makedirs(CAPTION_DIR, exist_ok=True)
# -----------------------------------------------


class InstagramLoginBot:
    def __init__(self):
        self.driver = None
        self.accounts_file = "accounts.json"
        self.profile_dir = None

    def create_driver(self, use_persistent_profile=True, profile_name=None):
        chrome_options = Options()
        if use_persistent_profile:
            if profile_name:
                self.profile_dir = os.path.join(os.getcwd(), f"chrome_profile_{profile_name}")
            else:
                self.profile_dir = os.path.join(tempfile.gettempdir(), "instagram_bot_profile")
            os.makedirs(self.profile_dir, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={self.profile_dir}')
            logger.info(f"Persistent profile: {self.profile_dir}")

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_argument('--window-size=1280,800')

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        selected_ua = random.choice(user_agents)
        chrome_options.add_argument(f'--user-agent={selected_ua}')
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')

        try:
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": selected_ua})
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
            logger.info("Browser opened successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            return False

    def human_like_delay(self, min_sec=0.5, max_sec=2.0):
        time.sleep(random.uniform(min_sec, max_sec))
        
    def _select_original_crop(self):
        """If this is an image, select 'Original' crop to preserve aspect ratio."""
        try:
            # Wait a moment for the crop button to appear
            self.human_like_delay(1.5, 2.5)
            crop_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Select crop"]'))
            )
            crop_btn.click()
            logger.info("Clicked 'Select crop'")
            self.human_like_delay(0.5, 1)
            
            # Now click the "Original" option in the dropdown
            original_option = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[@role="button"][.//span[text()="Original"]]'))
            )
            original_option.click()
            logger.info("Selected 'Original' crop")
            self.human_like_delay(0.5, 1)
        except Exception:
            # Videos or UI differences – just skip
            logger.debug("Could not select original crop (probably a video or UI changed).")

    def login_manual_fallback(self, username, password):
        logger.info("Manual login with human-like typing...")
        try:
            username_field = None
            for selector in ['input[name="username"]', 'input[type="text"]']:
                try:
                    username_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if username_field.is_displayed():
                        break
                except:
                    continue

            password_field = None
            for selector in ['input[name="password"]', 'input[type="password"]']:
                try:
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if password_field.is_displayed():
                        break
                except:
                    continue

            if username_field and password_field:
                username_field.clear()
                password_field.clear()
                self.human_like_delay(0.5, 1)
                for char in username:
                    username_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                self.human_like_delay(0.5, 1.5)
                for char in password:
                    password_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                self.human_like_delay(0.5, 1)
                password_field.send_keys(Keys.RETURN)
                logger.info("Form submitted")
                return True
        except Exception as e:
            logger.error(f"Manual login error: {e}")
        return False

    def handle_recaptcha(self):
        current_url = self.driver.current_url.lower()
        if 'recaptcha' in current_url or 'challenge' in current_url:
            print("\n" + "=" * 100)
            print("SECURITY CHECK REQUIRED")
            print("=" * 100)
            print("Complete the captcha in the browser, then the script continues...")
            for i in range(60):
                time.sleep(5)
                current_url = self.driver.current_url.lower()
                if 'recaptcha' not in current_url and 'challenge' not in current_url:
                    print("\nChallenge completed!")
                    time.sleep(3)
                    return True
                if i % 12 == 0 and i > 0:
                    print(f"Waiting... ({i * 5}s elapsed)")
            print("Timeout waiting for challenge.")
            return False
        return True

    def check_login_success(self):
        time.sleep(5)
        if not self.handle_recaptcha():
            return 'captcha_timeout'
        current_url = self.driver.current_url.lower()
        if 'instagram.com' in current_url and 'login' not in current_url and 'challenge' not in current_url:
            return True
        return False

    def login(self, username, password):
        try:
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(3)
            if self.login_manual_fallback(username, password):
                result = self.check_login_success()
                if result == True:
                    print("\n[SUCCESS] Login successful!")
                    return True
                elif result == 'captcha_timeout':
                    return False
            print("\n[FAILED] Could not login.")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    # ==================== ROBUST "NOT NOW" POPUP DISMISSAL ====================
    def dismiss_save_password_popup(self):
        """
        Dismiss any popup/dialog that contains a 'Not now' (or similar) button.
        Handles both <button> and <div role="button"> elements.
        """
        self.human_like_delay(1, 2)  # Wait for the popup to appear

        # Texts we want to match (case‑insensitive)
        target_texts = ["not now", "not now", "never", "no thanks", "cancel"]

        for _ in range(5):  # retry a few times if the popup is delayed
            try:
                # Look for any clickable element with a matching text
                # This covers: <button>, <div role="button">, <span role="button">, etc.
                xpath_expression = " | ".join([
                    f'//button[contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text}")]'
                    for text in target_texts
                ])
                # Also include div/span with role="button"
                xpath_expression += " | " + " | ".join([
                    f'//div[@role="button" and contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text}")]'
                    for text in target_texts
                ])
                xpath_expression += " | " + " | ".join([
                    f'//span[@role="button" and contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text}")]'
                    for text in target_texts
                ])

                elements = self.driver.find_elements(By.XPATH, xpath_expression)
                for el in elements:
                    try:
                        if el.is_displayed() and el.is_enabled():
                            el.click()
                            logger.info(f"Dismissed popup with element: <{el.tag_name}> '{el.text}'")
                            return
                    except:
                        continue
            except:
                pass
            time.sleep(1)

        logger.debug("No dismissable popup found.")

    # ==================== QUEUE DEDUPLICATION ====================
    @staticmethod
    def deduplicate_queue(queue):
        seen = {}
        priority = {'uploaded': 2, 'pending': 1, 'failed': 0}
        for item in queue:
            fname = item['file']
            cur = priority.get(item['status'], -1)
            if fname not in seen or cur > priority.get(seen[fname]['status'], -1):
                seen[fname] = item
        deduped = list(seen.values())
        if len(deduped) != len(queue):
            logger.info(f"Queue deduplicated: {len(queue)} → {len(deduped)} items.")
        return deduped

    def post_media(self, file_path, caption=""):
        if not self.driver:
            logger.error("Driver not available.")
            return False

        try:
            logger.info(f"Uploading: {file_path}")

            try:
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element_located((By.ID, "splash-screen"))
                )
                logger.info("Splash screen gone.")
            except:
                logger.warning("No splash screen.")

            new_post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
            )
            new_post_btn.click()
            logger.info("Clicked 'New post'")
            self.human_like_delay(1.5, 2.5)

            try:
                post_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Post"]'))
                )
                post_option.click()
                logger.info("Clicked 'Post' in menu.")
            except:
                logger.warning("'Post' menu option not found – trying anyway.")
            self.human_like_delay(1, 2)

            try:
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                file_input.send_keys(file_path)
                logger.info("File path sent directly.")
            except Exception as e:
                logger.warning("Direct input failed, trying fallback.")
                try:
                    select_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//button[contains(text(),"Select from computer")]')
                        )
                    )
                    select_btn.click()
                    logger.info("Fallback: clicked 'Select from computer'")
                    file_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                    )
                    file_input.send_keys(file_path)
                    logger.info("Fallback: file path sent.")
                except Exception as e2:
                    logger.error(f"All upload attempts failed: {e2}")
                    return False
            self.human_like_delay(2, 3)

            try:
                ok_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
                )
                ok_btn.click()
                logger.info("Clicked 'OK' on short video popup.")
                self.human_like_delay(1, 2)
            except:
                logger.info("No video confirmation popup.")
                
            self._select_original_crop()

            next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Next")]'))
            )
            next_btn.click()
            logger.info("Clicked first 'Next'")
            self.human_like_delay(1, 2)

            next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Next")]'))
            )
            next_btn.click()
            logger.info("Clicked second 'Next'")
            self.human_like_delay(1, 2)

            if caption:
                caption_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]'))
                )
                caption_box.click()
                for char in caption:
                    caption_box.send_keys(char)
                    time.sleep(random.uniform(0.03, 0.1))
                logger.info(f"Caption added: {caption}")

            share_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Share")]'))
            )
            share_btn.click()
            logger.info("Clicked 'Share', waiting for upload...")

            file_is_video = file_path.lower().endswith(('.mp4', '.mov', '.avi'))
            max_upload_wait = 300 if file_is_video else 60

            try:
                WebDriverWait(self.driver, max_upload_wait).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@role="button" and normalize-space()="Done"]')
                    )
                )
                logger.info("'Done' button visible – upload finished.")
            except:
                logger.warning("Neither toast nor 'Done' button appeared within timeout.")
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                self.human_like_delay(2, 3)
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
                    )
                    logger.info("Feed is back – upload likely succeeded.")
                    return True
                except:
                    logger.error("Feed not accessible. Upload might have failed.")
                    return False

            self.human_like_delay(1.5, 2.5)
            done_clicked = False
            for btn_xpath in [
                '//div[@role="button" and normalize-space()="Done"]',
                '//button[normalize-space()="Done"]',
                '//*[@role="button" and normalize-space()="Done"]',
            ]:
                try:
                    done_btn = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, btn_xpath))
                    )
                    self.driver.execute_script("arguments[0].click();", done_btn)
                    logger.info(f"JS clicked 'Done' button: {btn_xpath}")
                    done_clicked = True
                    break
                except:
                    continue

            if not done_clicked:
                logger.warning("No 'Done' button – pressing Escape.")
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                self.human_like_delay(1, 2)


            logger.info("Upload completed!")
            return True

        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False

    def upload_media_from_folder(self, folder_path, caption_prefix=""):
        """Upload all pending files listed in the queue file."""
        files = set()
        for ext in ALLOWED_EXTENSIONS:
            files.update(glob.glob(os.path.join(folder_path, f'*.{ext}')))
            files.update(glob.glob(os.path.join(folder_path, f'*.{ext.upper()}')))
        files = sorted(files)

        if not files:
            print("No compatible media files found in folder.")
            return 0, 0

        print(f"\nFound {len(files)} media file(s):")
        for i, f in enumerate(files, 1):
            print(f"  {i}. {os.path.basename(f)}")

        selected = files
        print(f"\nUploading {len(selected)} file(s)...")
        success = 0
        fail = 0

        for idx, path in enumerate(selected, 1):
            print(f"\n[{idx}/{len(selected)}] {os.path.basename(path)}")
            caption = f"{caption_prefix} {idx}" if caption_prefix else ""
            if self.post_media(path, caption):
                success += 1
                print("Success")
            else:
                fail += 1
                print("Failed")

            print("Refreshing page for next upload...")
            self.driver.get('https://www.instagram.com/')
            self.human_like_delay(3, 5)

            if idx < len(selected):
                wait = random.uniform(8, 15)
                print(f"   Waiting {wait:.1f}s...")
                time.sleep(wait)

        return success, fail

    # ---------- MODIFIED: Cookies now stored in COOKIES_DIR ----------
    def save_cookies(self, username):
        try:
            cookies_path = os.path.join(COOKIES_DIR, f"cookies_{username}.pkl")
            with open(cookies_path, "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info(f"Cookies saved for {username} at {cookies_path}")
        except Exception as e:
            logger.error(f"Save cookies error: {e}")

    def load_cookies(self, username):
        try:
            cookies_path = os.path.join(COOKIES_DIR, f"cookies_{username}.pkl")
            if os.path.exists(cookies_path):
                self.driver.get('https://www.instagram.com/')
                time.sleep(2)
                with open(cookies_path, "rb") as f:
                    cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                self.driver.refresh()
                time.sleep(3)
                if 'login' not in self.driver.current_url.lower():
                    logger.info("Logged in via cookies")
                    return True
        except Exception as e:
            logger.error(f"Load cookies error: {e}")
        return False

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


# ---------- QUEUE MANAGEMENT ----------
def load_queue(queue_file):
    if os.path.exists(queue_file):
        with open(queue_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_queue(queue_file, queue):
    with open(queue_file, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2)


def update_queue_from_folder(queue, folder_path):
    existing_files = {item['file'] for item in queue}
    new_items = []
    for ext in ALLOWED_EXTENSIONS:
        for fpath in glob.glob(os.path.join(folder_path, f'*.{ext}')):
            fname = os.path.basename(fpath)
            if fname not in existing_files:
                new_items.append({'file': fname, 'status': 'pending'})
    if new_items:
        print(f"Added {len(new_items)} new files to queue.")
        queue.extend(new_items)
    return queue


# ---------- NEW: Helper to get caption for a media file ----------
def get_caption_for_file(media_filename):
    """Look for a .txt file with the same base name in CAPTION_DIR.
    Return its content (stripped) if found; otherwise fall back to the filename without extension.
    """
    base, _ = os.path.splitext(media_filename)
    caption_file = os.path.join(CAPTION_DIR, base + ".txt")
    if os.path.isfile(caption_file):
        try:
            with open(caption_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:  # if file is not empty
                logger.info(f"Caption loaded from {caption_file}")
                return content
        except Exception as e:
            logger.warning(f"Could not read caption file {caption_file}: {e}")
    # Fallback: use the file's base name as before
    return base


def process_queue_for_user(bot, username, folder_path, queue_file):
    """Login, build queue, upload pending items with progress counter."""
    # Login
    if not bot.load_cookies(username):
        with open(bot.accounts_file, 'r') as f:
            accounts = json.load(f)
        if username not in accounts:
            print(f"Account '{username}' not found in {bot.accounts_file}")
            return
        password = accounts[username].get('password')
        if not password:
            print(f"No password for user {username}")
            return
        if bot.login(username, password):
            bot.save_cookies(username)
            # Dismiss the "Save password?" popup (robust version)
            bot.dismiss_save_password_popup()
        else:
            print(f"Login failed for {username}")
            return
    else:
        print(f"Session restored for {username}")

    # Queue operations
    queue = load_queue(queue_file)
    queue = update_queue_from_folder(queue, folder_path)
    queue = bot.deduplicate_queue(queue)
    save_queue(queue_file, queue)

    pending = [item for item in queue if item['status'] == 'pending']
    if not pending:
        print(f"No pending files for {username}. Everything is up to date.")
        return

    print(f"\n================== {len(pending)} file(s) to upload for {username} ==================")
    for idx, item in enumerate(pending, 1):
        full_path = os.path.join(folder_path, item['file'])
        if not os.path.exists(full_path):
            print(f"[{idx}/{len(pending)}] MISSING: {item['file']} → failed")
            item['status'] = 'failed'
            save_queue(queue_file, queue)
            continue

        # ---------- MODIFIED: caption from .txt file or filename fallback ----------
        caption = get_caption_for_file(item['file'])
        print(f"[{idx}/{len(pending)}] Uploading: {item['file']} (caption: '{caption}')")

        if bot.post_media(full_path, caption):
            item['status'] = 'uploaded'
            print(f"[Success]")
        else:
            item['status'] = 'failed'
            print(f"[Failed]")
        save_queue(queue_file, queue)

        # Refresh and wait between uploads
        bot.driver.get('https://www.instagram.com/')
        bot.human_like_delay(3, 5)
        if idx < len(pending):
            wait = random.uniform(8, 15)
            print(f"   Waiting {wait:.1f}s before next file...")
            time.sleep(wait)


def main():
    print("\n" + "=" * 100)
    print("Instagram Automated Uploader (Queue based)")
    print("=" * 100)

    if not os.path.exists("accounts.json"):
        print("accounts.json not found. Please create it first.")
        return
    with open("accounts.json", 'r') as f:
        accounts = json.load(f)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    media_folder = os.path.join(script_dir, "media")
    if not os.path.isdir(media_folder):
        print(f"'media' folder not found at {media_folder}. Please create it and add files.")
        return

    for username in accounts:
        print(f"{'='*30} Processing account: {username} {'='*30}")
        # ---------- MODIFIED: queue file placed in POSTQUEUE_DIR ----------
        queue_file = os.path.join(POSTQUEUE_DIR, f"post_queue_{username}.json")
        bot = InstagramLoginBot()

        try:
            if not bot.create_driver(use_persistent_profile=True, profile_name=username):
                continue
            process_queue_for_user(bot, username, media_folder, queue_file)
        except Exception as e:
            print(f"Unexpected error with {username}: {e}")
        finally:
            bot.close()
            time.sleep(2)

    print("\nAll accounts processed. Done!")


if __name__ == "__main__":
    main()
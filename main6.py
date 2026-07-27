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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('WDM').setLevel(logging.WARNING)

# Allowed media file extensions
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'mp4', 'mov', 'avi']


class InstagramLoginBot:
    def __init__(self):
        self.driver = None
        self.accounts_file = "accounts.json"
        self.profile_dir = None

    def create_driver(self, use_persistent_profile=True, profile_name=None):
        """Create Chrome driver with persistent profile & anti‑detection"""
        chrome_options = Options()

        if use_persistent_profile:
            if profile_name:
                self.profile_dir = os.path.join(os.getcwd(), f"chrome_profile_{profile_name}")
            else:
                self.profile_dir = os.path.join(tempfile.gettempdir(), "instagram_bot_profile")
            os.makedirs(self.profile_dir, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={self.profile_dir}')
            logger.info(f"Persistent profile: {self.profile_dir}")

        # Anti‑detection and stealth options
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

    def login_manual_fallback(self, username, password):
        """Type credentials character by character (most human‑like)"""
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
        """Wait for manual captcha solving (up to 5 minutes)"""
        current_url = self.driver.current_url.lower()
        if 'recaptcha' in current_url or 'challenge' in current_url:
            print("\n" + "=" * 60)
            print("SECURITY CHECK REQUIRED")
            print("=" * 60)
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
        """Check if we landed on the home page (not login/challenge)"""
        time.sleep(5)
        if not self.handle_recaptcha():
            return 'captcha_timeout'
        current_url = self.driver.current_url.lower()
        if 'instagram.com' in current_url and 'login' not in current_url and 'challenge' not in current_url:
            return True
        return False

    def login(self, username, password):
        """Main login flow"""
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
            # If manual fails, we skip the JS fallback (it rarely works) – manual is enough
            print("\n[FAILED] Could not login.")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    # ==================== MEDIA UPLOAD ====================
    def post_media(self, file_path, caption=""):
        if not self.driver:
            logger.error("Driver not available. Cannot post.")
            return False

        try:
            logger.info(f"Uploading: {file_path}")

            # 1. Wait for splash screen
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element_located((By.ID, "splash-screen"))
                )
                logger.info("Splash screen gone.")
            except:
                logger.warning("No splash screen.")

            # 2. Click the '+' icon (New post)
            new_post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
            )
            new_post_btn.click()
            logger.info("Clicked 'New post'")
            self.human_like_delay(1.5, 2.5)

            # 3. Click 'Post' in the dropdown
            try:
                post_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Post"]'))
                )
                post_option.click()
                logger.info("Clicked 'Post' in menu.")
            except:
                logger.warning("'Post' menu option not found – trying anyway.")
            self.human_like_delay(1, 2)

            # 4. Bypass "Select from computer" – send file directly to hidden input
            try:
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
                )
                self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                file_input.send_keys(file_path)
                logger.info("File path sent directly (no OS dialog).")
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

            # 5. Handle "OK" popup for short videos (if it appears)
            try:
                ok_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[text()="OK"]'))
                )
                ok_btn.click()
                logger.info("Clicked 'OK' on short video popup.")
                self.human_like_delay(1, 2)
            except:
                logger.info("No video confirmation popup.")

            # 6. First 'Next'
            next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Next")]'))
            )
            next_btn.click()
            logger.info("Clicked first 'Next'")
            self.human_like_delay(1, 2)

            # 7. Second 'Next'
            next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Next")]'))
            )
            next_btn.click()
            logger.info("Clicked second 'Next'")
            self.human_like_delay(1, 2)

            # 8. Caption
            if caption:
                caption_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]'))
                )
                caption_box.click()
                for char in caption:
                    caption_box.send_keys(char)
                    time.sleep(random.uniform(0.03, 0.1))
                logger.info(f"Caption added: {caption}")

            # 9. Click 'Share'
            share_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Share")]'))
            )
            share_btn.click()
            logger.info("Clicked 'Share', waiting for upload...")

            
            # 10. Wait for upload to finish and dismiss the final dialog
            file_is_video = file_path.lower().endswith(('.mp4', '.mov', '.avi'))
            max_upload_wait = 300 if file_is_video else 60   # generous for large videos

            # a) Wait for the success toast (the <h3> with the message)
            #    OR the "Done" button – whichever appears first means upload is finished.
            try:
                # First try the h3 toast with the exact text
                toast = WebDriverWait(self.driver, max_upload_wait).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//h3[contains(text(),"Your reel has been shared.") or contains(text(),"Post shared")]')
                    )
                )
                logger.info(f"Upload confirmation detected: {toast.text}")
            except:
                # Toast didn't show – maybe the "Done" button is already visible
                logger.warning("Toast not found, looking for 'Done' button instead...")
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@role="button" and normalize-space()="Done"]')
                        )
                    )
                    logger.info("'Done' button is visible – upload finished.")
                except:
                    logger.warning("Neither toast nor 'Done' button appeared within timeout.")
                    # Last resort: press Escape and hope for the best
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    self.human_like_delay(2, 3)
                    # Check if we're back on the feed
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
                        )
                        logger.info("Feed is back – upload likely succeeded.")
                        return True
                    except:
                        logger.error("Feed not accessible. Upload might have failed.")
                        return False

            # b) Dismiss the dialog by clicking "Done" (JavaScript click to avoid interception)
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
                    logger.info(f"JavaScript clicked 'Done' button: {btn_xpath}")
                    done_clicked = True
                    break
                except:
                    continue

            # c) Fallback: if no button, press Escape
            if not done_clicked:
                logger.warning("No 'Done' button – pressing Escape.")
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                self.human_like_delay(1, 2)

            # d) Wait for the main feed (New post icon) to be clickable
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
                )
                logger.info("Main feed is back – dialog closed.")
            except:
                logger.warning("Main feed not fully loaded, but continuing.")

            logger.info("Upload completed!")
            return True
    
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return False

    def upload_media_from_folder(self, folder_path, caption_prefix=""):
        """Upload all compatible media files from a folder."""
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

        upload_all = input("\nUpload all? (y/n, default: y): ").strip().lower()
        if upload_all != 'n':
            selected = files
        else:
            indices = input("Enter file numbers (e.g., 1,3,5): ").strip()
            try:
                idx_list = [int(x.strip()) for x in indices.split(',')]
                selected = [files[i-1] for i in idx_list if 1 <= i <= len(files)]
            except:
                print("Invalid input.")
                return 0, 0

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
                
             # --- REFRESH PAGE AFTER EACH UPLOAD ---
            print("Refreshing page for next upload...")
            self.driver.get('https://www.instagram.com/')
            self.human_like_delay(3, 5)   # wait for the feed to load
            # ------------------------------------

            if idx < len(selected):
                wait = random.uniform(8, 15)  # longer wait for videos
                print(f"   Waiting {wait:.1f}s...")
                time.sleep(wait)

        return success, fail

    # ==================== COOKIES & SESSION ====================
    def save_cookies(self, username):
        try:
            with open(f"cookies_{username}.pkl", "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)
            logger.info(f"Cookies saved for {username}")
        except Exception as e:
            logger.error(f"Save cookies error: {e}")

    def load_cookies(self, username):
        try:
            cookies_file = f"cookies_{username}.pkl"
            if os.path.exists(cookies_file):
                self.driver.get('https://www.instagram.com/')
                time.sleep(2)
                with open(cookies_file, "rb") as f:
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


def main():
    print("\n" + "=" * 60)
    print("Instagram Media Uploader")
    print("=" * 60)
    print("1. Login to account")
    print("2. Add new account")
    print("3. Exit")
    choice = input("\nChoice (1-3): ").strip()

    if choice == '3':
        print("Goodbye!")
        return

    if choice == '2':
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        accounts = {}
        if os.path.exists("accounts.json"):
            with open("accounts.json", 'r') as f:
                accounts = json.load(f)
        accounts[username] = {'password': password, 'added': datetime.now().isoformat()}
        with open("accounts.json", 'w') as f:
            json.dump(accounts, f, indent=2)
        print(f"Account {username} saved.")
        choice = '1'

    if choice == '1':
        username = input("Username: ").strip()
        password = None
        if os.path.exists("accounts.json"):
            with open("accounts.json", 'r') as f:
                accounts = json.load(f)
                if username in accounts:
                    use_saved = input(f"Use saved password for {username}? (y/n): ").strip().lower()
                    if use_saved == 'y':
                        password = accounts[username]['password']
        if not password:
            password = input("Password: ").strip()

        if not username or not password:
            print("Credentials required!")
            return

        use_persistent = input("Use persistent profile? (y/n, default: y): ").strip().lower()
        use_persistent = use_persistent != 'n'

        bot = InstagramLoginBot()
        try:
            if not bot.create_driver(
                use_persistent_profile=use_persistent,
                profile_name=username if use_persistent else None
            ):
                return

            # Cookie session first
            if not bot.load_cookies(username):
                if bot.login(username, password):
                    bot.save_cookies(username)
                else:
                    print("\n[FAILED] Login unsuccessful.")
                    input("Press Enter to close...")
                    return
            else:
                print("\n[SUCCESS] Logged in via saved session!")

            # ===== UPLOAD FROM DEFAULT 'media' FOLDER =====
            script_dir = os.path.dirname(os.path.abspath(__file__))
            media_dir = os.path.join(script_dir, "media")
            print(f"\nMedia folder: {media_dir}")
            if os.path.isdir(media_dir):
                # Gather any media file
                files = set()
                for ext in ALLOWED_EXTENSIONS:
                    files.update(glob.glob(os.path.join(media_dir, f'*.{ext}')))
                    files.update(glob.glob(os.path.join(media_dir, f'*.{ext.upper()}')))
                files = sorted(files)
                if files:
                    print(f"Found {len(files)} file(s).")
                    upload_now = input("Upload them now? (y/n, default: y): ").strip().lower()
                    if upload_now != 'n':
                        cap_prefix = input("Caption prefix (optional): ").strip()
                        success, fail = bot.upload_media_from_folder(media_dir, cap_prefix)
                        print(f"\nUpload finished: {success} succeeded, {fail} failed.")
                else:
                    print("No media files found in 'media' folder.")
            else:
                print("'media' folder not found. Create one next to the script and place files inside.")
                manual = input("Enter a different folder path? (y/n): ").strip().lower()
                if manual == 'y':
                    folder = input("Path: ").strip()
                    if os.path.isdir(folder):
                        cap_prefix = input("Caption prefix (optional): ").strip()
                        success, fail = bot.upload_media_from_folder(folder, cap_prefix)
                        print(f"\nUpload finished: {success} succeeded, {fail} failed.")
                    else:
                        print("Folder not found.")

            print("\nSession active. Press Enter to close...")
            input()

        except KeyboardInterrupt:
            print("\nInterrupted.")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
        finally:
            bot.close()
            print("Done!")


if __name__ == "__main__":
    main()
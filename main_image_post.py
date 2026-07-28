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

# Fix encoding for Windows console
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

class InstagramLoginBot:
    def __init__(self):
        self.driver = None
        self.accounts_file = "accounts.json"
        self.profile_dir = None

    def create_driver(self, use_persistent_profile=True, profile_name=None):
        """Create Chrome driver with persistent profile to avoid repeated captchas"""
        chrome_options = Options()

        if use_persistent_profile:
            if profile_name:
                self.profile_dir = os.path.join(os.getcwd(), f"chrome_profile_{profile_name}")
            else:
                self.profile_dir = os.path.join(tempfile.gettempdir(), "instagram_bot_profile")

            os.makedirs(self.profile_dir, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={self.profile_dir}')
            logger.info(f"Using persistent profile: {self.profile_dir}")

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "excludeSwitches": ["enable-automation"],
            "useAutomationExtension": False
        }
        chrome_options.add_experimental_option("prefs", prefs)

        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        chrome_options.add_argument('--window-size=1280,800')

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')

        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')

        try:
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(user_agents)
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)

            logger.info("Browser opened successfully with anti-detection measures")
            return True
        except Exception as e:
            logger.error(f"Failed to create driver: {e}")
            return False

    def human_like_delay(self, min_sec=0.5, max_sec=2.0):
        time.sleep(random.uniform(min_sec, max_sec))

    def simulate_human_behavior(self):
        try:
            self.driver.execute_script("window.scrollBy(0, 100);")
            self.human_like_delay(0.5, 1)
            self.driver.execute_script("window.scrollBy(0, -50);")
            self.human_like_delay(0.5, 1)
            self.driver.execute_script("""
                var event = new MouseEvent('mousemove', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: Math.random() * 500,
                    clientY: Math.random() * 500
                });
                document.dispatchEvent(event);
            """)
        except:
            pass

    def login_with_javascript(self, username, password):
        try:
            logger.info("Attempting JavaScript login...")
            time.sleep(3)
            self.simulate_human_behavior()

            js_script = """
            function findInputs() {
                let inputs = document.getElementsByTagName('input');
                let usernameField = null;
                let passwordField = null;
                
                for (let input of inputs) {
                    let type = input.type.toLowerCase();
                    let name = (input.name || '').toLowerCase();
                    let ariaLabel = (input.getAttribute('aria-label') || '').toLowerCase();
                    let placeholder = (input.placeholder || '').toLowerCase();
                    let autocomplete = (input.getAttribute('autocomplete') || '').toLowerCase();
                    
                    if (type === 'text' || 
                        name.includes('user') || 
                        name.includes('email') || 
                        ariaLabel.includes('username') || 
                        ariaLabel.includes('phone') || 
                        ariaLabel.includes('email') || 
                        placeholder.includes('username') ||
                        placeholder.includes('phone') ||
                        autocomplete.includes('username')) {
                        usernameField = input;
                    }
                    
                    if (type === 'password' || 
                        name.includes('pass') || 
                        ariaLabel.includes('password') ||
                        autocomplete.includes('password')) {
                        passwordField = input;
                    }
                }
                
                return {username: usernameField, password: passwordField};
            }
            
            let fields = findInputs();
            
            if (fields.username && fields.password) {
                fields.username.value = '';
                fields.password.value = '';
                
                fields.username.value = arguments[0];
                fields.password.value = arguments[1];
                
                ['input', 'change', 'blur'].forEach(eventType => {
                    fields.username.dispatchEvent(new Event(eventType, { bubbles: true }));
                    fields.password.dispatchEvent(new Event(eventType, { bubbles: true }));
                });
                
                setTimeout(() => {
                    let buttons = document.getElementsByTagName('button');
                    let loginBtn = null;
                    
                    for (let btn of buttons) {
                        let text = btn.innerText.toLowerCase();
                        if (btn.type === 'submit' || 
                            text.includes('log in') || 
                            text.includes('login') ||
                            text.includes('sign in')) {
                            loginBtn = btn;
                            break;
                        }
                    }
                    
                    if (loginBtn) {
                        loginBtn.click();
                        return 'clicked_button';
                    } else {
                        let form = document.querySelector('form');
                        if (form) {
                            form.submit();
                            return 'submitted_form';
                        }
                        fields.password.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, bubbles: true}));
                        return 'pressed_enter';
                    }
                }, Math.random() * 1000 + 500);
                
                return 'fields_filled';
            } else {
                return 'fields_not_found';
            }
            
            function random() {
                return Math.random();
            }
            """

            result = self.driver.execute_script(js_script, username, password)
            logger.info(f"JavaScript execution result: {result}")
            return 'fields_filled' in result or 'clicked' in result or 'submitted' in result or 'pressed' in result

        except Exception as e:
            logger.error(f"JavaScript login error: {e}")
            return False

    def login_manual_fallback(self, username, password):
        logger.info("Trying manual element finding...")
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
                logger.info("Form submitted with human-like typing")
                return True

        except Exception as e:
            logger.error(f"Manual login error: {e}")
        return False

    def handle_recaptcha(self):
        current_url = self.driver.current_url.lower()
        if 'recaptcha' in current_url or 'challenge' in current_url:
            print("\n" + "="*60)
            print("SECURITY CHECK REQUIRED")
            print("="*60)
            print("\nPlease complete the captcha in the browser window.")
            for i in range(60):
                time.sleep(5)
                current_url = self.driver.current_url.lower()
                if 'recaptcha' not in current_url and 'challenge' not in current_url:
                    print("\nChallenge completed! Continuing...")
                    time.sleep(3)
                    return True
                if i % 12 == 0 and i > 0:
                    print(f"Still waiting... ({i*5} seconds elapsed)")
            print("\nTimeout waiting for challenge completion.")
            return False
        return True

    def check_login_success(self):
        time.sleep(5)
        if not self.handle_recaptcha():
            return 'captcha_timeout'
        current_url = self.driver.current_url.lower()
        logger.info(f"Current URL: {current_url}")
        if 'instagram.com' in current_url and 'login' not in current_url and 'challenge' not in current_url and 'recaptcha' not in current_url:
            logger.info("Login successful!")
            return True
        return False

    def login(self, username, password):
        try:
            logger.info("Navigating to Instagram...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(3)

            logger.info("Attempting human-like manual login...")
            if self.login_manual_fallback(username, password):
                result = self.check_login_success()
                if result == True:
                    print("\n[SUCCESS] Login successful!")
                    return True
                elif result == 'captcha_timeout':
                    return False
            else:
                logger.info("Manual method failed, trying JavaScript...")
                if self.login_with_javascript(username, password):
                    result = self.check_login_success()
                    if result == True:
                        print("\n[SUCCESS] Login successful!")
                        return True

            print("\n[FAILED] Could not login.")
            return False
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    # ==================== IMAGE POSTING METHODS ====================
    def post_image(self, image_path, caption=""):
        if not self.driver:
            logger.error("Driver not available. Cannot post.")
            return False

        try:
            logger.info("Starting image posting process...")

            # 1. Wait for splash screen to disappear
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element_located((By.ID, "splash-screen"))
                )
                logger.info("Splash screen disappeared.")
            except:
                logger.warning("Splash screen not found or already gone – continuing.")

            # 2. Click the '+' icon in the top bar
            new_post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
            )
            new_post_btn.click()
            logger.info("Clicked on 'New post' icon.")
            self.human_like_delay(1.5, 2.5)

            # 3. Instagram now shows a dropdown menu. Click the "Post" option.
            try:
                post_option = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Post"]'))
                )
                post_option.click()
                logger.info("Clicked on 'Post' option in menu.")
            except:
                logger.warning("'Post' menu option not found – trying to continue anyway.")
            self.human_like_delay(1, 2)

            # 4. Click "Select from computer" button (the upload dialog is now visible)
            try:
                select_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//button[contains(text(),"Select from computer")]')
                    )
                )
                select_btn.click()
                logger.info("Clicked 'Select from computer' button.")
            except:
                # If the button is not there, maybe the file input is already available
                logger.warning("'Select from computer' button not found – looking for file input directly.")
            self.human_like_delay(1, 2)

            # 5. Wait for the file input and send the image path
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )
            file_input.send_keys(image_path)
            logger.info(f"Image file '{image_path}' selected.")
            self.human_like_delay(2, 3)

            # 6. Click first 'Next' (crop stage)
            next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Next")]'))
            )
            next_btn.click()
            logger.info("Clicked first 'Next'.")
            self.human_like_delay(1, 2)

            # 7. Click second 'Next' (filter stage)
            next_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="button" and contains(text(),"Next")]'))
            )
            next_btn.click()
            logger.info("Clicked second 'Next'.")
            self.human_like_delay(1, 2)

            # 8. Add caption (optional)
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
            logger.info("Clicked 'Share'. Waiting for upload...")

            # 10. Wait until the dialog box disappears
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, '//div[@role="dialog"]'))
            )
            logger.info("Post shared successfully!")
            return True

        except Exception as e:
            logger.error(f"Error during image posting: {e}")
            return False

    def post_images_from_folder(self, folder_path, caption_prefix=""):
        """
        Upload all images from a folder (jpg, jpeg, png).
        Returns (success_count, fail_count).
        """
        # Gather images
        extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        images = set()  # Use a set to avoid duplicates
        for ext in extensions:
            images.update(glob.glob(os.path.join(folder_path, f'*.{ext}')))
            images.update(glob.glob(os.path.join(folder_path, f'*.{ext.upper()}')))
        images = sorted(images) 
        if not images:
            print("No image files found in the folder.")
            return 0, 0

        print(f"\nFound {len(images)} image(s) in folder:")
        for i, img in enumerate(images, 1):
            print(f"  {i}. {os.path.basename(img)}")

        upload_all = input("\nUpload all? (y/n, default: y): ").strip().lower()
        if upload_all != 'n':
            selected = images
        else:
            indices = input("Enter file numbers separated by commas (e.g., 1,3,5): ").strip()
            try:
                idx_list = [int(x.strip()) for x in indices.split(',')]
                selected = [images[i-1] for i in idx_list if 1 <= i <= len(images)]
            except:
                print("Invalid input. Aborting upload.")
                return 0, 0

        print(f"\nUploading {len(selected)} image(s)...")
        success = 0
        fail = 0

        for idx, img_path in enumerate(selected, 1):
            print(f"\n[{idx}/{len(selected)}] Uploading: {os.path.basename(img_path)}")
            caption = f"{caption_prefix} {idx}" if caption_prefix else ""
            if self.post_image(img_path, caption):
                success += 1
                print(f"   ✓ Uploaded successfully.")
            else:
                fail += 1
                print(f"   ✗ Upload failed. Check logs.")

            # Wait between posts to avoid spam detection
            if idx < len(selected):
                wait_time = random.uniform(5, 10)
                print(f"   Waiting {wait_time:.1f} seconds before next upload...")
                time.sleep(wait_time)

        return success, fail

    # ==================== END OF IMAGE POSTING ====================

    def save_cookies(self, username):
        try:
            cookies_file = f"cookies_{username}.pkl"
            pickle.dump(self.driver.get_cookies(), open(cookies_file, "wb"))
            logger.info(f"Cookies saved for {username}")
        except Exception as e:
            logger.error(f"Error saving cookies: {e}")

    def load_cookies(self, username):
        try:
            cookies_file = f"cookies_{username}.pkl"
            if os.path.exists(cookies_file):
                self.driver.get('https://www.instagram.com/')
                time.sleep(2)
                cookies = pickle.load(open(cookies_file, "rb"))
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
                self.driver.refresh()
                time.sleep(3)

                if 'login' not in self.driver.current_url.lower():
                    logger.info("Logged in using saved cookies")
                    return True
        except Exception as e:
            logger.error(f"Error loading cookies: {e}")
        return False

    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


def main():
    print("\n" + "="*60)
    print("Instagram Multi-Account Manager (with Folder Upload)")
    print("="*60)
    print("\nTIPS TO AVOID REPEATED CAPTCHAS:")
    print("  1. Use 'persistent profile' option - keeps you logged in")
    print("  2. Don't login/logout frequently")
    print("  3. Complete captchas carefully when they appear")
    print("  4. Keep the browser session alive as long as possible")
    print("="*60 + "\n")

    print("1. Login to account")
    print("2. Add new account")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == '3':
        print("Goodbye!")
        return

    if choice == '2':
        username = input("Enter Instagram username: ").strip()
        password = input("Enter Instagram password: ").strip()

        accounts = {}
        if os.path.exists("accounts.json"):
            with open("accounts.json", 'r') as f:
                accounts = json.load(f)

        accounts[username] = {
            'password': password,
            'added': datetime.now().isoformat()
        }

        with open("accounts.json", 'w') as f:
            json.dump(accounts, f, indent=2)

        print(f"\nAccount {username} saved!")
        choice = '1'

    if choice == '1':
        username = input("Enter Instagram username: ").strip()

        password = None
        if os.path.exists("accounts.json"):
            with open("accounts.json", 'r') as f:
                accounts = json.load(f)
                if username in accounts:
                    use_saved = input(f"Use saved password for {username}? (y/n): ").strip().lower()
                    if use_saved == 'y':
                        password = accounts[username]['password']

        if not password:
            password = input("Enter Instagram password: ").strip()

        if not username or not password:
            print("Error: Username and password are required!")
            return

        print("\nUse persistent profile? (Recommended to avoid repeated captchas)")
        print("This saves your browser session so you stay logged in longer.")
        use_persistent = input("Use persistent profile? (y/n, default: y): ").strip().lower()
        use_persistent = use_persistent != 'n'

        bot = InstagramLoginBot()

        try:
            if not bot.create_driver(
                use_persistent_profile=use_persistent,
                profile_name=username if use_persistent else None
            ):
                print("Failed to open browser. Exiting...")
                return

            # Try cookies first
            if not bot.load_cookies(username):
                # Login
                print("\nAttempting to login...")
                success = bot.login(username, password)
                if success:
                    bot.save_cookies(username)
                    print("\n[SUCCESS] Login successful!")
                else:
                    print("\n[FAILED] Login unsuccessful")
                    print("\nBrowser will stay open. Press Enter to close...")
                    input()
                    return
            else:
                print("\n[SUCCESS] Logged in using saved session!")

             # ===================== AUTO FOLDER UPLOAD =====================
            script_dir = os.path.dirname(os.path.abspath(__file__))
            default_media_folder = os.path.join(script_dir, "media")

            print(f"\nLooking for media folder: {default_media_folder}")
            if os.path.isdir(default_media_folder):
                extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
                images = set()  # Use a set to avoid duplicates
                for ext in extensions:
                    images.update(glob.glob(os.path.join(default_media_folder, f'*.{ext}')))
                    images.update(glob.glob(os.path.join(default_media_folder, f'*.{ext.upper()}')))
                images = sorted(images) 
    
                if images:
                    print(f"Found {len(images)} image(s) in the 'media' folder.")
                    upload_now = input("Upload them now? (y/n, default: y): ").strip().lower()
                    if upload_now != 'n':
                        cap_prefix = input("Enter caption prefix (optional, press Enter to skip): ").strip()
                        success, fail = bot.post_images_from_folder(default_media_folder, cap_prefix)
                        print(f"\nUpload complete: {success} succeeded, {fail} failed.")
                else:
                    print("No images found in the 'media' folder.")
            else:
                print(f"Folder '{default_media_folder}' does not exist. Skipping automatic upload.")
                manual = input("Do you want to specify a different folder? (y/n): ").strip().lower()
                if manual == 'y':
                    folder = input("Enter full folder path: ").strip()
                    if os.path.isdir(folder):
                        cap_prefix = input("Enter caption prefix (optional): ").strip()
                        success, fail = bot.post_images_from_folder(folder, cap_prefix)
                        print(f"\nUpload complete: {success} succeeded, {fail} failed.")
                    else:
                        print("Folder not found.")
            # ===============================================================

            print("\nSession active. Press Enter to close...")
            input()

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
        finally:
            print("\nClosing browser...")
            bot.close()
            print("Done!")


if __name__ == "__main__":
    main()

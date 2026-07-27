import json
import time
import random
import logging
import os
import pickle
import sys
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
        
        # CRITICAL: Use a persistent profile directory
        # This saves cookies, localStorage, and browser fingerprint
        if use_persistent_profile:
            if profile_name:
                self.profile_dir = os.path.join(os.getcwd(), f"chrome_profile_{profile_name}")
            else:
                self.profile_dir = os.path.join(tempfile.gettempdir(), "instagram_bot_profile")
            
            os.makedirs(self.profile_dir, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={self.profile_dir}')
            logger.info(f"Using persistent profile: {self.profile_dir}")
        
        # Anti-detection options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Disable automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Add real browser preferences
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "excludeSwitches": ["enable-automation"],
            "useAutomationExtension": False
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Disable logging
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--silent')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Window size
        chrome_options.add_argument('--window-size=1280,800')
        
        # Randomize user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Additional evasion techniques
        chrome_options.add_argument('--disable-features=TranslateUI')
        chrome_options.add_argument('--disable-ipc-flooding-protection')
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute CDP commands to hide automation
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": random.choice(user_agents)
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Add more realistic browser properties
            self.driver.execute_script("""
                // Overwrite navigator properties
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
        """Add random delay to mimic human behavior"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def simulate_human_behavior(self):
        """Simulate human-like behavior before login"""
        try:
            # Scroll slightly
            self.driver.execute_script("window.scrollBy(0, 100);")
            self.human_like_delay(0.5, 1)
            self.driver.execute_script("window.scrollBy(0, -50);")
            self.human_like_delay(0.5, 1)
            
            # Move mouse randomly (simulate human cursor movement)
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
        """Login using JavaScript injection with human-like typing simulation"""
        try:
            logger.info("Attempting JavaScript login...")
            time.sleep(3)
            
            # Simulate human behavior
            self.simulate_human_behavior()
            
            # Enhanced JavaScript with better field detection
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
                    
                    // Username detection
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
                    
                    // Password detection
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
                // Clear fields first
                fields.username.value = '';
                fields.password.value = '';
                
                // Set values
                fields.username.value = arguments[0];
                fields.password.value = arguments[1];
                
                // Trigger events
                ['input', 'change', 'blur'].forEach(eventType => {
                    fields.username.dispatchEvent(new Event(eventType, { bubbles: true }));
                    fields.password.dispatchEvent(new Event(eventType, { bubbles: true }));
                });
                
                // Find and click login button with delay
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
                        // Try form submission
                        let form = document.querySelector('form');
                        if (form) {
                            form.submit();
                            return 'submitted_form';
                        }
                        fields.password.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13, bubbles: true}));
                        return 'pressed_enter';
                    }
                }, random() * 1000 + 500);
                
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
        """Manual login with human-like typing"""
        logger.info("Trying manual element finding...")
        
        try:
            # Find username field
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
            
            # Find password field
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
                # Clear fields
                username_field.clear()
                password_field.clear()
                self.human_like_delay(0.5, 1)
                
                # Type username like a human (character by character)
                for char in username:
                    username_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_like_delay(0.5, 1.5)
                
                # Type password like a human
                for char in password:
                    password_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
                
                self.human_like_delay(0.5, 1)
                
                # Submit
                password_field.send_keys(Keys.RETURN)
                logger.info("Form submitted with human-like typing")
                return True
                
        except Exception as e:
            logger.error(f"Manual login error: {e}")
        
        return False
    
    def handle_recaptcha(self):
        """Handle reCAPTCHA challenge"""
        current_url = self.driver.current_url.lower()
        
        if 'recaptcha' in current_url or 'challenge' in current_url:
            print("\n" + "="*60)
            print("SECURITY CHECK REQUIRED")
            print("="*60)
            print("\nInstagram is asking for verification.")
            print("\nIMPORTANT TIPS TO REDUCE FUTURE CAPTCHAS:")
            print("  1. Complete the captcha carefully")
            print("  2. Don't close the browser - keep session alive")
            print("  3. The persistent profile will help reduce captchas")
            print("\nPlease complete the captcha in the browser window.")
            print("\nWaiting for you to complete it...")
            print("="*60 + "\n")
            
            # Wait for challenge completion
            for i in range(60):  # 5 minutes max
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
        """Check if login was successful"""
        time.sleep(5)
        
        if not self.handle_recaptcha():
            return 'captcha_timeout'
        
        current_url = self.driver.current_url.lower()
        logger.info(f"Current URL: {current_url}")
        
        # Success check
        if 'instagram.com' in current_url and 'login' not in current_url and 'challenge' not in current_url and 'recaptcha' not in current_url:
            logger.info("Login successful!")
            return True
        
        return False
    
    def login(self, username, password):
        """Main login function"""
        try:
            logger.info("Navigating to Instagram...")
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(3)
            
            # Try manual method first (more human-like)
            logger.info("Attempting human-like manual login...")
            if self.login_manual_fallback(username, password):
                result = self.check_login_success()
                if result == True:
                    print("\n[SUCCESS] Login successful!")
                    return True
                elif result == 'captcha_timeout':
                    return False
            else:
                # Fallback to JavaScript
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
    
    def save_cookies(self, username):
        """Save cookies"""
        try:
            cookies_file = f"cookies_{username}.pkl"
            pickle.dump(self.driver.get_cookies(), open(cookies_file, "wb"))
            logger.info(f"Cookies saved for {username}")
        except Exception as e:
            logger.error(f"Error saving cookies: {e}")
    
    def load_cookies(self, username):
        """Load saved cookies"""
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
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    print("\n" + "="*60)
    print("Instagram Multi-Account Manager")
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
        
        # Ask about persistent profile
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
            if bot.load_cookies(username):
                print("\n[SUCCESS] Logged in using saved session!")
                print("\nSession active. Press Enter to close...")
                input()
                return
            
            # Login
            print("\nAttempting to login...")
            success = bot.login(username, password)
            
            if success:
                bot.save_cookies(username)
                print("\n[SUCCESS] Login successful!")
                if use_persistent:
                    print("[INFO] Persistent profile will help avoid future captchas")
                print("\nSession active. Press Enter to close...")
                input()
            else:
                print("\n[FAILED] Login unsuccessful")
                print("\nBrowser will stay open. Press Enter to close...")
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
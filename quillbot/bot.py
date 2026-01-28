import os
import re
import time
import shutil
import tempfile
from typing import List, Optional, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class Quillbot:
    """
    A class to automate interactions with Quillbot's Paraphrasing and AI Humanizer tools.
    """

    def __init__(
        self,
        headless: bool = True,
        user_data_dir: Optional[str] = None,
        profile_directory: str = "Default",
        copy_profile: bool = False
    ):
        """
        Initialize the Quillbot automation instance.

        Args:
            headless (bool): Whether to run the browser in headless mode.
            user_data_dir (str, optional): Path to the Chrome User Data directory.
            profile_directory (str): Name of the Chrome profile directory (e.g., "Default").
            copy_profile (bool): Whether to copy the profile to a temporary directory to avoid locking.
        """
        self.headless = headless
        self.temp_dir: Optional[str] = None
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        if user_data_dir:
            final_user_data_dir = user_data_dir
            
            if copy_profile:
                print(f"Copying profile from {user_data_dir} to temp directory...")
                self.temp_dir = tempfile.mkdtemp()
                final_user_data_dir = self.temp_dir
                
                try:
                    def ignore_patterns(path, names):
                        ignored = [
                            'Cache', 'Code Cache', 'GPUCache', 'ShaderCache', 
                            'Service Worker', 'CacheStorage',
                            'SingletonLock', 'SingletonSocket', 'SingletonCookie', 
                            'RunningChromeVersion', 'lockfile'
                        ]
                        return [n for n in names if n in ignored]

                    shutil.copytree(
                        user_data_dir, 
                        os.path.join(self.temp_dir, "User Data"), 
                        ignore=ignore_patterns, 
                        dirs_exist_ok=True
                    )
                    final_user_data_dir = os.path.join(self.temp_dir, "User Data")
                    print(f"Profile copied to {final_user_data_dir}")
                except Exception as e:
                    print(f"Error copying profile: {e}")
                    # Fallback to original if copy fails
                    final_user_data_dir = user_data_dir

            chrome_options.add_argument(f"--user-data-dir={final_user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={profile_directory}")
            
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def close(self):
        """Closes the browser and cleans up temporary directories."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
                
        if self.temp_dir:
            try:
                print(f"Cleaning up temp profile at {self.temp_dir}...")
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp profile: {e}")

    def _split_text(self, text: str, limit: int = 125) -> List[str]:
        """
        Splits text into chunks of at most `limit` words, respecting sentence boundaries where possible.
        
        Args:
            text (str): The text to split.
            limit (int): Maximum words per chunk.
            
        Returns:
            List[str]: A list of text chunks.
        """
        words = re.findall(r'\b[\w\']+\b', text)
        if len(words) <= limit:
            return [text]
        
        chunks = []
        current_word_count = 0
        
        # Split by sentence endings
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk_str = ""
        
        for sentence in sentences:
            sentence_word_count = len(re.findall(r'\b[\w\']+\b', sentence))
            
            if current_word_count + sentence_word_count <= limit:
                current_chunk_str += sentence + " "
                current_word_count += sentence_word_count
            else:
                if sentence_word_count > limit:
                    # Handle extremely long sentences by forcing a split
                     if current_chunk_str:
                         chunks.append(current_chunk_str.strip())
                     chunks.append(sentence.strip())
                     current_chunk_str = ""
                     current_word_count = 0
                else:
                    chunks.append(current_chunk_str.strip())
                    current_chunk_str = sentence + " "
                    current_word_count = sentence_word_count
        
        if current_chunk_str:
            chunks.append(current_chunk_str.strip())
            
        return chunks

    def _clear_input(self, input_element):
        """Clears the input element using JavaScript events."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
            time.sleep(0.5)
            
            self.driver.execute_script("""
                arguments[0].textContent = '';
                arguments[0].innerHTML = '';
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, input_element)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error clearing input: {e}")

    def _input_text(self, input_element, text: str):
        """Inputs text into the element using ActionChains to simulate real typing."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", input_element)
            
            actions = ActionChains(self.driver)
            actions.move_to_element(input_element).click().perform()
            time.sleep(0.5)
            
            actions.send_keys(text).perform()
            time.sleep(0.5)
            
            # Trigger input event just in case
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_element)
            
        except Exception as e:
            print(f"Error inputting text: {e}")

    def _get_output(self) -> Optional[str]:
        """Retrieves the text from the output box."""
        try:
            output_element = self.wait.until(EC.presence_of_element_located((By.ID, "paraphraser-output-box")))
            
            # Wait for processing to potentially finish/start
            time.sleep(5)
            
            text = output_element.text
            if not text:
                # Try getting text from child div if exists (common in Quillbot's editor)
                try:
                    child = output_element.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
                    text = child.text
                except Exception:
                    pass
            
            return text
        except Exception as e:
            print(f"Error getting output: {e}")
            return None

    def _click_button(self, xpath_text: str, css_selector: Optional[str] = None) -> bool:
        """
        Robustly finds and clicks a button using multiple strategies.
        
        Args:
            xpath_text (str): Text to search for in the button (e.g., "Paraphrase").
            css_selector (str, optional): Fallback CSS selector.
            
        Returns:
            bool: True if clicked successfully, False otherwise.
        """
        button = None
        
        # Strategy 1: XPath with text
        try:
            candidates = self.driver.find_elements(By.XPATH, f"//button[contains(., '{xpath_text}')]")
            for btn in candidates:
                if btn.is_displayed():
                    button = btn
                    break
        except Exception:
            pass
            
        # Strategy 2: CSS Selector fallback
        if not button and css_selector:
            try:
                candidates = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                for btn in candidates:
                    if xpath_text in btn.text and btn.is_displayed():
                        button = btn
                        break
            except Exception:
                pass
                
        if button:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                actions = ActionChains(self.driver)
                actions.move_to_element(button).click().perform()
                return True
            except Exception as e:
                print(f"Error clicking button '{xpath_text}': {e}")
                return False
        
        return False

    def paraphrase(self, text: str) -> str:
        """
        Paraphrases the given text.
        
        Args:
            text (str): Input text.
            
        Returns:
            str: Paraphrased text.
        """
        chunks = self._split_text(text)
        full_output = ""
        
        self.driver.get("https://quillbot.com/paraphrasing-tool")
        time.sleep(2)
        
        for i, chunk in enumerate(chunks):
            try:
                input_box = self.wait.until(EC.presence_of_element_located((By.ID, "paraphraser-input-box")))
                self._clear_input(input_box)
                self._input_text(input_box, chunk)
                
                if self._click_button("Paraphrase", "button.MuiButton-containedPrimary"):
                    time.sleep(15) # Wait for processing
                    output = self._get_output()
                    if output:
                        full_output += output + " "
                else:
                    print("Paraphrase button not found")
                    
            except Exception as e:
                print(f"Error processing chunk {i+1}: {e}")
                
        return full_output.strip()

    def humanize(self, text: str, mode: str = "Basic") -> str:
        """
        Humanizes the given text using the AI Humanizer.
        
        Args:
            text (str): Input text.
            mode (str): "Basic" or "Advanced". Note: Advanced requires a logged-in session.
            
        Returns:
            str: Humanized text.
        """
        chunks = self._split_text(text)
        full_output = ""
        
        self.driver.get("https://quillbot.com/ai-humanizer")
        time.sleep(2)
        
        # Select mode
        try:
            mode_selector = None
            if mode == "Basic":
                mode_selector = "#Paraphraser-mode-tab-0"
            elif mode == "Advanced":
                mode_selector = "#Paraphraser-mode-tab-1"
            
            if mode_selector:
                tab = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, mode_selector)))
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
                ActionChains(self.driver).move_to_element(tab).click().perform()
                time.sleep(1)
                
                # Check for "Sign up" popup
                try:
                    popup = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign up to use Advanced Humanize')]")
                    if popup and any(p.is_displayed() for p in popup):
                        print("WARNING: Advanced mode requires sign-up. The automation may fail or require manual intervention.")
                except Exception:
                    pass
            else:
                print(f"Unknown mode: {mode}. Using default.")
        except Exception as e:
            print(f"Error selecting mode: {e}")

        for i, chunk in enumerate(chunks):
            try:
                input_box = self.wait.until(EC.presence_of_element_located((By.ID, "paraphraser-input-box")))
                self._clear_input(input_box)
                self._input_text(input_box, chunk)
                
                if self._click_button("Humanize"):
                    time.sleep(15)
                    output = self._get_output()
                    if output:
                        full_output += output + " "
                else:
                    print("Humanize button not found")
                    
            except Exception as e:
                print(f"Error processing chunk {i+1}: {e}")
                
        return full_output.strip()

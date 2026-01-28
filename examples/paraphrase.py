import os
import sys

# Add parent directory to path so we can import the package without installing it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from quillbot.bot import Quillbot

def main():
    print("Initializing Quillbot Automation...")
    
    # --- CONFIGURATION ---
    # You can set these via environment variables or modify them here
    HEADLESS = os.getenv("HEADLESS", "True").lower() == "true"
    
    # Chrome Profile Configuration
    # Set this to your Chrome User Data directory to use your logged-in session.
    # Default Windows path: "C:\Users\mark\AppData\Local\Google\Chrome\User Data"
    # macOS: "/Users/<username>/Library/Application Support/Google/Chrome"
    # Can be overridden via CHROME_USER_DATA_DIR environment variable
    USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR") or os.path.join(
        os.path.expanduser("~"), 
        "AppData", 
        "Local", 
        "Google", 
        "Chrome", 
        "User Data"
    )
    
    PROFILE_DIR = os.getenv("CHROME_PROFILE_DIR", "Default")
    
    # Set to True to copy the profile to a temp directory.
    # Recommended to avoid "Chrome instance exited" errors if Chrome is already open.
    COPY_PROFILE = os.getenv("COPY_PROFILE", "True").lower() == "true"
    # ---------------------

    print(f"Configuration: Headless={HEADLESS}, Profile={USER_DATA_DIR}, Copy={COPY_PROFILE}")

    bot = Quillbot(
        headless=HEADLESS, 
        user_data_dir=USER_DATA_DIR, 
        profile_directory=PROFILE_DIR, 
        copy_profile=COPY_PROFILE
    )
    
    try:
        # 1. Paraphrasing Example
        # Read input text from file
        # Note: Text is read as plain text, so markdown syntax (like *, **, ----) 
        # will be preserved in the text and sent to Quillbot as-is
        input_file = os.path.join(os.path.dirname(__file__), '..', 'input', 'paraphrase.txt')
        input_file = os.path.abspath(input_file)
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Read file as plain text - markdown syntax is treated as regular text characters
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        print(f"\n--- Paraphrasing ---\nInput: {text}")
        res = bot.paraphrase(text)
        print(f"Result: {res}")
        
        # Save result to file
        result_file = os.path.join(os.path.dirname(__file__), '..', 'result', 'paraphrased.txt')
        result_file = os.path.abspath(result_file)
        os.makedirs(os.path.dirname(result_file), exist_ok=True)
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(res)
        print(f"\nResult saved to: {result_file}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        bot.close()
        print("\nBrowser closed.")

if __name__ == "__main__":
    main()

"""
n8n Code (Python) Node - Ready-to-Paste Code Snippet

Copy and paste the code below into your n8n Code (Python) node.

VERSION 1: Reads from input file (like paraphrase.py)
VERSION 2: Reads from n8n items (from previous node)
"""

# ============================================================================
# VERSION 1: Read from input file (input/paraphrase.txt)
# ============================================================================
VERSION_1_FILE_INPUT = """
import os
import sys

# Add project path to access quillbot module
# ADJUST THIS PATH to match your project location
project_path = r"C:\\Users\\mark\\Desktop\\Quillbot_api-main"
sys.path.insert(0, project_path)

from quillbot.bot import Quillbot

# Configuration from environment variables or defaults
headless = os.getenv('HEADLESS', 'True').lower() == 'true'
user_data_dir = os.getenv('CHROME_USER_DATA_DIR')
if not user_data_dir:
    # Default Windows path
    user_data_dir = os.path.join(
        os.path.expanduser('~'),
        'AppData', 'Local', 'Google', 'Chrome', 'User Data'
    )

profile_dir = os.getenv('CHROME_PROFILE_DIR', 'Default')
copy_profile = os.getenv('COPY_PROFILE', 'True').lower() == 'true'

# Initialize result fields in items
items[0]['json']['success'] = False
items[0]['json']['result'] = None
items[0]['json']['error'] = None

bot = None
try:
    # Read input file
    input_file = os.path.join(project_path, 'input', 'paraphrase.txt')
    if not os.path.exists(input_file):
        items[0]['json']['error'] = f'Input file not found: {input_file}'
        return items
    
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    
    if not text:
        items[0]['json']['error'] = 'Input file is empty'
        return items
    
    # Initialize bot
    bot = Quillbot(
        headless=headless,
        user_data_dir=user_data_dir,
        profile_directory=profile_dir,
        copy_profile=copy_profile
    )
    
    # Paraphrase the text
    result = bot.paraphrase(text)
    
    # Save to result file
    result_file = os.path.join(project_path, 'result', 'paraphrased.txt')
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    # Return success with result
    items[0]['json']['result'] = result
    items[0]['json']['success'] = True
    items[0]['json']['input_text'] = text  # Include original text for reference
    
except Exception as e:
    # Handle errors
    items[0]['json']['error'] = str(e)
    items[0]['json']['success'] = False
    
finally:
    # Always cleanup
    if bot:
        try:
            bot.close()
        except Exception:
            pass

return items
"""


# ============================================================================
# VERSION 2: Read from n8n items (from previous node)
# ============================================================================
VERSION_2_ITEMS_INPUT = """
import os
import sys

# Add project path to access quillbot module
# ADJUST THIS PATH to match your project location
project_path = r"C:\\Users\\mark\\Desktop\\Quillbot_api-main"
sys.path.insert(0, project_path)

from quillbot.bot import Quillbot

# Get text from n8n items (from previous node)
# Adjust the path based on your input structure:
# - items[0]['json']['text'] - if text is in 'text' field
# - items[0]['json']['body']['text'] - if text is in webhook body
# - items[0]['json']['body'] - if entire body is the text
text = items[0]['json'].get('text') or items[0]['json'].get('body', '')

# If body is a dict, try to get text from it
if isinstance(text, dict):
    text = text.get('text', '')

# If still empty, try other common field names
if not text:
    text = items[0]['json'].get('content', '') or items[0]['json'].get('message', '')

# Validate input
if not text or not text.strip():
    items[0]['json']['error'] = 'No text provided in input. Expected: items[0][\'json\'][\'text\']'
    items[0]['json']['success'] = False
    return items

# Configuration from environment variables or defaults
headless = os.getenv('HEADLESS', 'True').lower() == 'true'
user_data_dir = os.getenv('CHROME_USER_DATA_DIR')
if not user_data_dir:
    # Default Windows path
    user_data_dir = os.path.join(
        os.path.expanduser('~'),
        'AppData', 'Local', 'Google', 'Chrome', 'User Data'
    )

profile_dir = os.getenv('CHROME_PROFILE_DIR', 'Default')
copy_profile = os.getenv('COPY_PROFILE', 'True').lower() == 'true'

# Initialize result fields
items[0]['json']['success'] = False
items[0]['json']['result'] = None
items[0]['json']['error'] = None

bot = None
try:
    # Initialize bot
    bot = Quillbot(
        headless=headless,
        user_data_dir=user_data_dir,
        profile_directory=profile_dir,
        copy_profile=copy_profile
    )
    
    # Paraphrase the text
    result = bot.paraphrase(text.strip())
    
    # Save to result file (optional)
    result_file = os.path.join(project_path, 'result', 'paraphrased.txt')
    os.makedirs(os.path.dirname(result_file), exist_ok=True)
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    # Return success with result
    items[0]['json']['result'] = result
    items[0]['json']['success'] = True
    items[0]['json']['original_text'] = text  # Keep original for reference
    
except Exception as e:
    # Handle errors
    items[0]['json']['error'] = str(e)
    items[0]['json']['success'] = False
    
finally:
    # Always cleanup
    if bot:
        try:
            bot.close()
        except Exception:
            pass

return items
"""


# ============================================================================
# VERSION 3: Minimal version (no file saving, just return result)
# ============================================================================
VERSION_3_MINIMAL = """
import os
import sys

# Add project path
project_path = r"C:\\Users\\mark\\Desktop\\Quillbot_api-main"
sys.path.insert(0, project_path)

from quillbot.bot import Quillbot

# Get text from items or file
text = items[0]['json'].get('text', '')
if not text:
    # Fallback: read from file
    input_file = os.path.join(project_path, 'input', 'paraphrase.txt')
    if os.path.exists(input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()

if not text:
    items[0]['json']['error'] = 'No text provided'
    return items

bot = Quillbot(headless=True)
try:
    result = bot.paraphrase(text)
    items[0]['json']['result'] = result
    items[0]['json']['success'] = True
except Exception as e:
    items[0]['json']['error'] = str(e)
    items[0]['json']['success'] = False
finally:
    bot.close()

return items
"""


if __name__ == "__main__":
    print("=" * 80)
    print("VERSION 1: Read from input file (input/paraphrase.txt)")
    print("=" * 80)
    print(VERSION_1_FILE_INPUT)
    
    print("\n" + "=" * 80)
    print("VERSION 2: Read from n8n items (from previous node)")
    print("=" * 80)
    print(VERSION_2_ITEMS_INPUT)
    
    print("\n" + "=" * 80)
    print("VERSION 3: Minimal version")
    print("=" * 80)
    print(VERSION_3_MINIMAL)

# Quillbot API (Python)

A Python wrapper for automating interactions with Quillbot's Paraphrasing and AI Humanizer tools using Selenium. This tool allows you to programmatically paraphrase text and use the AI Humanizer (including Advanced mode for premium users) via a headless browser.

> **Disclaimer**: This project is for **educational and experimental purposes only**. It uses browser automation to interact with Quillbot. Please respect Quillbot's Terms of Service and use this tool responsibly.

## Features

-   **Paraphrasing**: Automate text paraphrasing using Quillbot's standard tool.
-   **AI Humanizer**: Access the AI Humanizer tool.
    -   **Basic Mode**: Free mode.
    -   **Advanced Mode**: Supports Premium accounts via session reuse.
-   **Long Text Support**: Automatically splits long text into chunks to respect the word limit (default 125 words).
-   **Headless Automation**: Runs in the background without opening a visible browser window.
-   **Session Reuse**: Can use your existing Chrome profile to access Premium features without logging in manually.
-   **Robustness**: Handles dynamic elements, React-based inputs, and varying load times.

## Usage

### Basic Usage

```python
from quillbot.bot import Quillbot

# Initialize (headless by default)
bot = Quillbot()

try:
    # Paraphrase text
    text = "This is a test sentence."
    result = bot.paraphrase(text)
    print(f"Paraphrased: {result}")

    # Humanize text (Basic mode)
    humanized = bot.humanize(text, mode="Basic")
    print(f"Humanized: {humanized}")

finally:
    bot.close()
```

### Advanced Usage (Signed-in Session)

To use **Advanced Mode** (or other features requiring a logged-in account), you need to point the script to your existing Chrome profile where you are already signed in.

**Note**: The script includes a `copy_profile` option (enabled by default in examples) that copies your profile to a temporary directory. This allows you to run the automation **even if your main Chrome browser is open**, avoiding "Chrome instance exited" errors.

> **Known Issues with Advanced Mode**:
> - **Popups**: Promotional popups or "Sign up" modals may occasionally block the automation.
> - **Profile Verification**: Chrome may sometimes ask for profile verification (password re-entry) when launching from a copied profile, which can prevent the session from being fully active.
> - **Stability**: Due to these factors, Advanced Mode is currently experimental and may require manual intervention or a more robust login implementation.

```python
from quillbot.bot import Quillbot

# Path to your Chrome User Data directory
# macOS: "/Users/<username>/Library/Application Support/Google/Chrome"
# Windows: "C:\\Users\\<username>\\AppData\\Local\\Google\\Chrome\\User Data"
user_data_dir = "/Users/yourname/Library/Application Support/Google/Chrome"

bot = Quillbot(
    headless=True,
    user_data_dir=user_data_dir,
    profile_directory="Default",
    copy_profile=True  # Recommended: Copies profile to temp dir to avoid locking
)

try:
    text = "AI is a branch of computer science."
    # Now you can use Advanced mode
    result = bot.humanize(text, mode="Advanced")
    print(result)
finally:
    bot.close()
```

## Configuration

You can also configure the example script using environment variables:

-   `HEADLESS`: `True` or `False` (default: `True`)
-   `CHROME_USER_DATA_DIR`: Path to your Chrome User Data directory.
-   `CHROME_PROFILE_DIR`: Profile directory name (default: `Default`).
-   `COPY_PROFILE`: `True` or `False` (default: `True`).

## Contributing

Contributions are welcome! This project is open source.

**Areas for Improvement:**
-   **Advanced Mode Stability**: Better handling of login sessions, profile verification checks, and promotional popups.
-   **Word Limit Bypass**: Better logic to split text or bypass the 125-word limit more efficiently.
-   **Efficiency**: Optimizing wait times and selectors.

Please feel free to submit a Pull Request.

## License

MIT License
 
 3.Rules
 Browser Must  have signed in Quillbot
 Browser must be closed
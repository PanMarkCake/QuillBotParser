# n8n Code Node - Quick Start Guide

## Copy & Paste Code for n8n Code (Python) Node

### Which Version Should I Use?

- **Version 1**: Use if you want to read text from `input/paraphrase.txt` file (like `paraphrase.py` does)
- **Version 2**: Use if you want to read text from previous n8n node (from `items[0]['json']['text']`)
- **Version 3**: Minimal version - tries both file and items, no file saving

### Step 1: Open the Code File

Open `examples/n8n_code_snippet.py` and copy the version you need.

### Step 2: Adjust the Path

Before pasting, adjust this line to match your project location:

```python
project_path = r"C:\\Users\\mark\\Desktop\\Quillbot_api-main"
```

Change it to your actual path.

### Step 3: Paste into n8n

1. In n8n, add a **Code** node
2. Select **Python** as the language
3. Paste the code
4. Adjust the path if needed
5. Execute

### Step 4: Get Results

After execution, the result will be in:
- `items[0]['json']['result']` - The paraphrased text
- `items[0]['json']['success']` - `true` if successful, `false` if error
- `items[0]['json']['error']` - Error message if failed

### Input Format (Version 2)

If using Version 2, make sure your previous node outputs text in one of these formats:

```json
{
  "text": "Text to paraphrase"
}
```

Or:

```json
{
  "body": {
    "text": "Text to paraphrase"
  }
}
```

Or:

```json
{
  "body": "Text to paraphrase"
}
```

### Troubleshooting

**Error: ModuleNotFoundError**
- Check that `project_path` is correct
- Verify the `quillbot` folder exists in that path

**Error: File not found**
- For Version 1: Check that `input/paraphrase.txt` exists
- Adjust the path in the code if needed

**Error: No text provided**
- For Version 2: Check that previous node outputs text in expected format
- Adjust the field name in the code: `items[0]['json'].get('text')`

**Error: Chrome failed to start**
- Close Chrome browser before running
- Check Chrome/ChromeDriver installation

### Example Workflow

1. **Manual Trigger** or **Webhook**
2. **Set Node** (optional) - Format input: `{"text": "Your text here"}`
3. **Code (Python) Node** - Paste Version 2 code
4. **Continue workflow** - Use `items[0]['json']['result']`

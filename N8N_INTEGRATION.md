# n8n Integration Guide for Quillbot Bot

This guide explains how to integrate the Quillbot bot with n8n workflows using the Execute Command node.

## Overview

The integration uses a Python wrapper script (`examples/n8n_wrapper.py`) that:
- Accepts JSON input from n8n
- Executes Quillbot operations (paraphrase or humanize)
- Returns JSON output for n8n to consume
- Handles errors gracefully

## Prerequisites

1. **Python Environment**: Ensure Python 3.x is installed and accessible from n8n
2. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. **Chrome/ChromeDriver**: Ensure Chrome browser and ChromeDriver are installed
4. **Chrome Profile** (Optional): For Advanced Mode, ensure you're logged into Quillbot in your Chrome profile

## Wrapper Script

The wrapper script (`examples/n8n_wrapper.py`) accepts JSON input via stdin or command-line argument.

### Input Format

```json
{
  "text": "Text to paraphrase or humanize",
  "operation": "paraphrase" or "humanize",
  "mode": "Basic" or "Advanced" (only required for humanize, defaults to "Basic")
}
```

### Output Format

**Success:**
```json
{
  "success": true,
  "result": "Paraphrased or humanized text",
  "error": null
}
```

**Error:**
```json
{
  "success": false,
  "result": null,
  "error": "Error message describing what went wrong"
}
```

## n8n Workflow Setup

### Step 1: Basic Workflow Structure

1. **Trigger Node** (Webhook/Manual/Schedule)
   - Receives or generates the text to process

2. **Set Node** (Optional - Format Input)
   - Formats the input data as JSON string
   - Example expression:
     ```javascript
     JSON.stringify({
       text: $json.text || $json.body,
       operation: "paraphrase",
       mode: $json.mode || "Basic"
     })
     ```

3. **Execute Command Node**
   - Executes the wrapper script
   - Configuration below

4. **Parse JSON Node**
   - Parses the JSON output from the wrapper

5. **IF Node** (Error Handling)
   - Checks if `success` is `true`

6. **Continue Workflow**
   - Use the `result` field in subsequent nodes

### Step 2: Execute Command Node Configuration

**Node Settings:**
- **Command**: `python` (or full path: `C:\Python\python.exe` on Windows)
- **Arguments**: 
  ```
  ["C:\\Users\\mark\\Desktop\\Quillbot_api-main\\examples\\n8n_wrapper.py"]
  ```
  (Adjust path based on your installation)

**Input:**
- **Input Data**: Select "Using Input Data"
- **Input Field**: The JSON string from previous node
- **Input Type**: `stdin` (default)

**Advanced Settings:**
- **Timeout**: Set to `60000` (60 seconds) or higher
  - Chrome initialization and Quillbot processing can take time
- **Working Directory**: Optional, set to project root if needed

### Step 3: Parse JSON Node

After Execute Command, add a **Parse JSON** node:
- **Input Field**: `stdout` (or the field containing JSON output)
- **Output**: Parsed JSON object with `success`, `result`, and `error` fields

### Step 4: Error Handling

Add an **IF Node** to check for errors:

**Condition:**
```javascript
{{ $json.success === true }}
```

**True Path (Success):**
- Continue with workflow using `{{ $json.result }}`

**False Path (Error):**
- Log error: `{{ $json.error }}`
- Send notification or handle error appropriately
- Optionally retry or stop workflow

## Example Workflows

### Example 1: Simple Paraphrasing

```
Manual Trigger
  → Set Node (format input)
  → Execute Command (run wrapper)
  → Parse JSON
  → IF (check success)
    → True: Use result
    → False: Log error
```

**Set Node Expression:**
```javascript
JSON.stringify({
  text: "This is the text to paraphrase.",
  operation: "paraphrase"
})
```

### Example 2: Webhook with Humanize

```
Webhook Trigger
  → Set Node (format input from webhook)
  → Execute Command (run wrapper)
  → Parse JSON
  → IF (check success)
    → True: Return result via HTTP Response
    → False: Return error via HTTP Response
```

**Set Node Expression:**
```javascript
JSON.stringify({
  text: $json.body.text,
  operation: $json.body.operation || "paraphrase",
  mode: $json.body.mode || "Basic"
})
```

### Example 3: Batch Processing

```
Schedule Trigger
  → Read from Database/File
  → Split In Batches
  → For Each Item:
    → Set Node (format input)
    → Execute Command
    → Parse JSON
    → IF (check success)
      → Save result
      → Continue
```

## Configuration via Environment Variables

The wrapper script reads configuration from environment variables. Set these in n8n or your system:

- `HEADLESS`: `"True"` or `"False"` (default: `"True"`)
- `CHROME_USER_DATA_DIR`: Path to Chrome User Data directory (optional)
- `CHROME_PROFILE_DIR`: Profile directory name (default: `"Default"`)
- `COPY_PROFILE`: `"True"` or `"False"` (default: `"True"`)

### Setting Environment Variables in n8n

**Option 1: System Environment Variables**
- Set in your operating system
- n8n will inherit them

**Option 2: n8n Environment Variables**
- In n8n settings, configure environment variables
- Access in Execute Command node if supported

**Option 3: Modify Wrapper Script**
- Hardcode values in `n8n_wrapper.py` if needed

## Error Handling

### Common Errors

1. **Chrome Not Available**
   - Error: "Chrome failed to start"
   - Solution: Ensure Chrome is installed and ChromeDriver is accessible

2. **Chrome Profile Locked**
   - Error: "The process cannot access the file because it is being used"
   - Solution: Close Chrome browser or set `COPY_PROFILE=True`

3. **Invalid Input**
   - Error: "Missing required field" or "Invalid operation"
   - Solution: Check input JSON format

4. **Timeout**
   - Error: Command timeout
   - Solution: Increase timeout in Execute Command node settings

### Error Handling in n8n

```javascript
// In IF Node (False path)
{
  "error": "{{ $json.error }}",
  "timestamp": "{{ $now }}",
  "input": "{{ $('Set Node').item.json }}"
}
```

## Performance Considerations

1. **Execution Time**: Each operation takes 10-30 seconds
   - Chrome initialization: ~5-10 seconds
   - Quillbot processing: ~5-20 seconds depending on text length

2. **Concurrency**: 
   - Multiple simultaneous executions may conflict
   - Chrome profile locking can cause issues
   - Consider queueing or limiting concurrent executions

3. **Timeout Settings**:
   - Set Execute Command timeout to at least 60 seconds
   - For long texts, consider 90-120 seconds

4. **Resource Usage**:
   - Each execution starts a new Chrome instance
   - Monitor system resources (CPU, memory)

## Testing

### Test the Wrapper Script Manually

```bash
# Test with stdin
echo '{"text": "Hello world", "operation": "paraphrase"}' | python examples/n8n_wrapper.py

# Test with command-line argument (PowerShell)
python examples/n8n_wrapper.py '{\"text\": \"Hello world\", \"operation\": \"paraphrase\"}'
```

### Test in n8n

1. Create a simple workflow with Manual Trigger
2. Use Set Node with test JSON
3. Execute and verify output
4. Check error handling with invalid input

## Troubleshooting

### Issue: Script not found
- **Solution**: Use absolute path in Execute Command arguments
- Verify Python path is correct

### Issue: JSON parsing errors
- **Solution**: Ensure input is valid JSON string
- Use Set Node to format input properly

### Issue: Chrome crashes
- **Solution**: Ensure Chrome is closed before execution
- Check ChromeDriver version compatibility

### Issue: Timeout errors
- **Solution**: Increase timeout in Execute Command node
- Check system resources

## Advanced: HTTP API Alternative

For better performance and concurrency handling, consider creating an HTTP API wrapper using Flask or FastAPI. This would:
- Run as a persistent service
- Handle multiple requests concurrently
- Provide better error handling
- Allow connection pooling

See the plan document for details on this approach.

## Support

For issues or questions:
1. Check error messages in n8n workflow execution logs
2. Test wrapper script manually to isolate issues
3. Verify Chrome and ChromeDriver installation
4. Review Quillbot bot documentation

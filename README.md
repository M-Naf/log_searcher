# README: Log Search Scripts

This repository contains two Python scripts designed to search for keywords in log files within a specific directory. Each script has unique features: one is a **command-line script** for flexible usage, while the other provides a **graphical user interface (GUI)** for user-friendly interaction.

---

## Script 1: **Command-Line Log Searcher**

### **Overview**
This script (`log_searcher.py`) is designed for searching log files in a specified directory using the command line. It supports filters for specific log types and highlights matching keywords in the console output.

### **Features**
- Search within `audit.log`, `mailbox.log`, and `zimbra.log` files.
- Highlight matches in **green**.
- Provides error messages for invalid filters or missing directories.
- Supports case-insensitive search.

### **Usage**
```bash
python log_searcher.py <file_filter> <keyword1> [<keyword2> ...]
```
### **Examples**
#### 1. Search all logs for a specific email and time:
```bash
python log_searcher.py -all test@test.com 13:00
```
#### 2. Search only audit.log files:
```bash
python log_searcher.py -audit error
```
### File Filters
- `-all`: Search in all relevant log files.
- `-address`: Search in address files.
- `-audit`: Search in audit.log.
- `-bruteforce`: Search in Bruteforce files.
- `-ip`: Search in ip_block.log.
- `-mailbox`: Search in mailbox.log.
- `-zimbra`: Search in zimbra.log.
### Output
- Matching Lines: Displays file name, line number, and highlighted matches.
- Errors: Highlighted in red (e.g., missing directory or invalid filter).
- Completion Message: Notifies whether matches were found.
---
# Script 2: Log Searcher App
### **Overview**
This script provides a graphical user interface for searching log files, making it ideal for users who prefer a visual approach. It features a progress bar, result highlighting, and dropdown menus for easy file selection.

### Features
- GUI with a text entry for keywords and a dropdown to select log files.
- Progress bar for search progress.
- Highlights results in the output window.
- Error messages in a user-friendly message box.
### **Usage**
1. Run the script:
```bash
python log_searcher_app.py
```
2. Enter Keywords: Type the keywords you want to search for (separated by spaces).
3. Select Log File: Choose from `All`, `audit.log`, `mailbox.log`, or `zimbra.log`.
4. Click Search or Return: View results in the scrolling text box, with matches highlighted in green and errors in red.
### **Components**
- Keyword Input: Type search terms, separated by spaces.
- Log File Selection: Select from the dropdown menu.
- Search Button: Initiates the search process.
- Result Display: Scrollable text box showing matches and errors.
- Progress Bar: Tracks search progress.
---
### **Requirements**
#### Common Dependencies
- Python 3.6 or later
- re (Regular Expressions)
- os (File System Interaction)
- sys (Command-line Interaction)
#### GUI-Specific Dependencies
- tkinter (Standard Python library for GUI development)
### **Directory Configuration**
Both scripts use a fixed log directory:
```bash
d:\test\log\
```
##### Ensure this directory exists and contains the relevant log files. If the directory is missing or inaccessible, the scripts will provide appropriate error messages.

---
### Compile to .exe
- Install PyInstaller
```bash
pip install pyinstaller
```
- Then run
```bash
pyinstaller --onefile --icon=D:\icon\logS.ico --noconsole log_searcher_app.py 
```
The `--onefile` option tells PyInstaller to bundle everything into a single executable file.

`--noconsole` is to hide the console window
### **Highlights**
- Command-Line Script: Suitable for automation or advanced users.
- GUI Script: Intuitive and ideal for manual searches.
- Customizability: Modify the `LOG_DIRECTORY` variable to adapt the scripts for your environment.
### **Known Issues**
- Large Files: Searching in very large files may take time. Use specific keywords to narrow results.
- Permissions: Ensure you have read permissions for the log directory.
### **Examples of Use Cases**
- System administrators searching for specific events in log files.
- Debugging email delivery or server issues using keywords like email addresses or timestamps.
- Monitoring audit logs for suspicious activities.
# **Author**
### Feel free to reach out for suggestions, improvements, or bug reports! 😊

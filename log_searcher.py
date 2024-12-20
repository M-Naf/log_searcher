import os
import re
import sys

LOG_DIRECTORY = r"d:\dir\log"

def search_logs(file_filter, keywords, directory):
    """Search for keywords in log files filtered by the specified file filter."""
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"\033[91mError: Directory '{directory}' does not exist.\033[0m")
        return
    log_files = []  # List to hold the paths of log files
    prefix_map = {
        "-all": ["address", "audit.log", "Bruteforce", "ip_block", "mailbox.log", "zimbra.log"],
        "-address": ["address"],
        "-audit": ["audit.log"],
        "-bruteforce": ["Bruteforce"],
        "-ip": ["ip_block"],
        "-mailbox": ["mailbox.log"],
        "-zimbra": ["zimbra.log"]
    }
    # Validate the file filter
    if file_filter not in prefix_map:
        print(f"\033[91mError: Invalid file filter '{file_filter}'. Use -all, -address, -audit, -bruteforce, -ip, -mailbox, or -zimbra.\033[0m")
        return
    # Traverse the directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.startswith(prefix) and not file.endswith(".gz") for prefix in prefix_map[file_filter]):
                log_files.append(os.path.join(root, file))  # Add matched log file to the list
    # Check if any log files were found
    if not log_files:
        print(f"No log files found matching the filter '{file_filter}' in the directory or its subdirectories.")
        return
    print(f"Searching for keywords: {', '.join(keywords)} in '{file_filter}' log files...\n")
    found = False

    # Define a function for highlighting keywords in the text
    def highlight_text(text, keywords):
        """Highlight keywords in the given text."""
        for keyword in keywords:
            text = re.sub(
                f"({re.escape(keyword)})",  # Escape special characters in the keyword
                r"\033[92m\1\033[0m",  # Highlight with green text
                text,
                flags=re.IGNORECASE,
            )
        return text

    # Search for the keywords in each selected log file
    total_files = len(log_files)  # Total number of log files
    for index, log_file in enumerate(log_files):
        try:
            with open(log_file, 'r') as file:
                for line_number, line in enumerate(file, 1):
                    # Check if all keywords are present in the line (case-insensitive)
                    if all(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                        highlighted_line = highlight_text(line.strip(), keywords)
                        print(f"[{log_file} - Line {line_number}] {highlighted_line}")
                        found = True
        except Exception as e:
            print(f"\033[91mError reading file '{log_file}': {e}\033[0m")

        # Update the progress bar after processing each file
        display_progress_bar(index + 1, total_files)

    # Print results based on whether any matches were found
    if not found:
        print(f"No matches found for keywords: {', '.join(keywords)}.")
    else:
        print("\nSearch completed.")

def display_progress_bar(iteration, total, bar_length=50):
    progress = (iteration / total)
    arrow = '=' * int(round(progress * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stderr.write(f'\rProgress: [{arrow + spaces}] {int(progress * 100)}%')
    sys.stderr.flush()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\033[94m\nUsage: \033[93mpython \033[0mlog_searcher.py \033[96m<file_filter> \033[0m<keyword1> [<keyword2> ...]")
        print("\033[92mUse: -all, -address, -audit, -bruteforce, -ip, -mailbox, or -zimbra.\n")
        print("\033[94mExample: \033[93mpython \033[0mlog_searcher.py \033[96m-all \033[0mtest@test.com 13:00 to=test2@test.com")
        sys.exit(1)

    # Get the file filter 
    file_filter = sys.argv[1]
    # Get the keywords for the search
    search_terms = sys.argv[2:]  # Remaining arguments after the file filter
    # Call the search function
    search_logs(file_filter, search_terms, LOG_DIRECTORY)

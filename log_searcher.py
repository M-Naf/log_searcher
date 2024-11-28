import os
import re
import sys

LOG_DIRECTORY = r"\\sh2\mail$\log"

def search_logs(file_filter, keywords, directory):

    if not os.path.exists(directory):
        print(f"\033[91mError: Directory '{directory}' does not exist.\033[0m")
        return

    # Select files based on the file filter
    if file_filter == "-all":
        log_files = [
            f for f in os.listdir(directory)
            if (f.startswith("audit.log") or f.startswith("mailbox.log") or f.startswith("zimbra.log"))
            and not f.endswith(".gz")
            and os.path.isfile(os.path.join(directory, f))
        ]
    else:
        prefix_map = {
            "-audit": "audit.log",
            "-mailbox": "mailbox.log",
            "-zimbra": "zimbra.log"
        }
        if file_filter not in prefix_map:
            print(f"\033[91mError: Invalid file filter '{file_filter}'. Use -all, -audit, -mailbox, or -zimbra.\033[0m")
            return
        log_files = [
            f for f in os.listdir(directory)
            if f.startswith(prefix_map[file_filter]) and not f.endswith(".gz") and os.path.isfile(os.path.join(directory, f))
        ]

    if not log_files:
        print(f"No log files found matching the filter '{file_filter}' in the directory.")
        return

    print(f"Searching for keywords: {', '.join(keywords)} in log files filtered by '{file_filter}'...\n")
    found = False

    # Define ANSI color for highlighting
    def highlight_text(text, keywords):
        for keyword in keywords:
            text = re.sub(
                f"({re.escape(keyword)})",  # Escape special characters in the keyword
                r"\033[92m\1\033[0m",  # Highlight with red text
                text,
                flags=re.IGNORECASE,
            )
        return text

    # Search for the keywords in each selected log file
    for log_file in log_files:
        log_path = os.path.join(directory, log_file)
        try:
            with open(log_path, 'r') as file:
                for line_number, line in enumerate(file, 1):
                    # Check if all keywords are present in the line (case-insensitive)
                    if all(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                        highlighted_line = highlight_text(line.strip(), keywords)
                        print(f"[{log_file} - Line {line_number}] {highlighted_line}")
                        found = True
        except Exception as e:
            print(f"\033[91mError reading file '{log_file}': {e}\033[0m")

    if not found:
        print(f"No matches found for keywords: {', '.join(keywords)}.")
    else:
        print("\nSearch completed.")

if __name__ == "__main__":
    # Ensure correct usage
    if len(sys.argv) < 3:
        print("\033[94m\nUsage: \033[93mpython \033[0mlog_searcher.py \033[96m<file_filter> \033[0m<keyword1> [<keyword2> ...]")
        print("\033[94mExample: \033[93mpython \033[0mlog_searcher.py \033[96m-all \033[0mtest@test.com 13:00 to=test2@test.com")
        print("or")
        print("\033[94mUsage: \033[93mpython \033[0m.\log_searcher.py \033[96m<file_filter> \033[0m<keyword1> [<keyword2> ...]")
        print("\033[94mExample: \033[93mpython \033[0m.\log_searcher.py \033[96m-all \033[0mtest@test.com 13:00 to=test2@test.com")
        sys.exit(1)

    # Get the file filter (e.g., -all, -audit, -mailbox, -zimbra)
    file_filter = sys.argv[1]

    # Get the keywords for the search
    search_terms = sys.argv[2:]  # Remaining arguments after the file filter

    # Call the search function
    search_logs(file_filter, search_terms, LOG_DIRECTORY)

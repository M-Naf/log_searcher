import os
import re
import sys

# Define the directory where log files are stored
LOG_DIRECTORY = r"d:\log\"

def search_logs(file_filter, keywords, directory):
    """Search for keywords in log files filtered by the specified file filter."""
    
    # Check if the log directory exists
    if not os.path.exists(directory):
        print(f"\033[91mError: Directory '{directory}' does not exist.\033[0m")
        return
    
    log_files = []
    
    # Map file filters to specific log file name patterns
    prefix_map = {
        "-all": ["address", "audit.log", "Bruteforce", "ip_block", "fail2ban.log", "mailbox.log", "zimbra.log"],
        "-address": ["address"],
        "-audit": ["audit.log"],
        "-bruteforce": ["Bruteforce"],
        "-ip": ["ip_block"],
        "-fail2ban": ["fail2ban.log"],
        "-mailbox": ["mailbox.log"],
        "-zimbra": ["zimbra.log"]
    }

    # Validate if the user-provided file filter exists in the prefix_map
    if file_filter not in prefix_map:
        print(f"\033[91mError: Invalid file filter '{file_filter}'. Use -all, -address, -audit, -bruteforce, -ip, -fail2ban, -mailbox, or -zimbra.\033[0m")
        return

    # Search for matching log files in the directory
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.startswith(prefix) and not file.endswith(".gz") for prefix in prefix_map[file_filter]):
                log_files.append(os.path.join(root, file))
    
    # If no log files match the filter, print a message and exit
    if not log_files:
        print(f"No log files found matching the filter '{file_filter}' in the directory or its subdirectories.")
        return

    print(f"Searching for keywords: {' '.join(keywords)} in '{file_filter}' log files...\n")
    found = False

    def highlight_text(text, keywords):
        """Highlight matching keywords in the text output."""
        for keyword in keywords:
            text = re.sub(
                f"({re.escape(keyword)})",
                r"\033[92m\1\033[0m",
                text,
                flags=re.IGNORECASE,
            )
        return text

    # Process search terms: separate them based on "or" and group by "and"
    or_groups = []  # Stores groups of AND conditions
    temp_and_group = []  # Temporary storage for AND conditions
    
    for term in keywords:
        if term.lower() == "or":
            if temp_and_group:
                or_groups.append(temp_and_group)  # Save the AND group
                temp_and_group = []  # Reset for the next OR group
        elif term.lower() != "and":
            temp_and_group.append(term)  # Add keyword to AND group

    if temp_and_group:
        or_groups.append(temp_and_group)  # Append last AND group

    total_files = len(log_files)
    for index, log_file in enumerate(log_files):
        try:
            with open(log_file, 'r') as file:
                for line_number, line in enumerate(file, 1):
                    match_found = False
                    
                    # Check if the line matches any of the OR groups
                    for and_conditions in or_groups:
                        if all(re.search(keyword.strip(), line, re.IGNORECASE) for keyword in and_conditions):
                            match_found = True
                            break  # Stop checking if one OR group matches

                    if match_found:
                        # Highlight all matched keywords
                        all_keywords = [kw for group in or_groups for kw in group]  # Flatten keyword list
                        highlighted_line = highlight_text(line.strip(), all_keywords)
                        print(f"[{log_file} - Line {line_number}] {highlighted_line}")
                        found = True
        except Exception as e:
            print(f"\033[91mError reading file '{log_file}': {e}\033[0m")

        # Show progress bar while processing
        display_progress_bar(index + 1, total_files)
    
    # Print result summary
    if not found:
        print(f"No matches found for keywords: {', '.join(keywords)}.")
    else:
        print("\nSearch completed.")


def display_progress_bar(iteration, total, bar_length=50):
    """Display a progress bar while processing files."""
    progress = (iteration / total)
    arrow = '=' * int(round(progress * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    sys.stderr.write(f'\rProgress: [{arrow + spaces}] {int(progress * 100)}%')
    sys.stderr.flush()


if __name__ == "__main__":
    # Ensure at least 2 arguments (file filter + at least 1 keyword)
    if len(sys.argv) < 3:
        print("\033[94m\nUsage: \033[93mpython \033[0mlog_searcher.py \033[96m<file_filter> \033[0m<\"keyword1\"> and <\"keyword2\"> [or <\"keyword3\"> ...]")
        print("\033[92mUse: -all, -address, -audit, -bruteforce, -ip, -fail2ban, -mailbox, or -zimbra.\n")
        print("\033[94mExample: \033[93mpython \033[0mlog_searcher.py \033[96m-all \033[0m\"keyword1\" and \"keyword2\" or \"keyword3\"")
        sys.exit(1)

    # Get the file filter (e.g., -zimbra, -mailbox) and search terms
    file_filter = sys.argv[1]
    search_terms = sys.argv[2:]
    
    # Execute the log search function
    search_logs(file_filter, search_terms, LOG_DIRECTORY)

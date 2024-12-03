import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

LOG_DIRECTORY = r"\\sh2\mail$"  # Fixed directory for logs

def search_logs(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button):
    """
    Search for multiple keywords in the selected log files within the fixed directory.
    Displays results immediately and updates the progress bar based on the number of files processed.
    """
    # Check if the log directory exists
    if not os.path.exists(LOG_DIRECTORY):
        messagebox.showerror("Error", f"Directory '{LOG_DIRECTORY}' does not exist.")
        search_button.config(state=tk.NORMAL)
        return

    log_files = []  # List to hold paths of log files matching the selected prefix
    prefix_map = {
        "All": ["address", "audit.log", "Bruteforce", "ip_block", "mailbox.log", "zimbra.log"],
        "Address":["address"],
        "Audit.log": ["audit.log"],
        "Bruteforce":["Bruteforce"],
        "IP_block": ["ip_block"],
        "Mailbox.log": ["mailbox.log"],
        "Zimbra.log": ["zimbra.log"]
    }
    
    # Validate the selected file
    if selected_file not in prefix_map:
        messagebox.showerror("Error", f"Invalid selection '{selected_file}'.")
        search_button.config(state=tk.NORMAL)
        return

    # Traverse the directory and collect log files based on the selected prefix
    for root_dir, _, files in os.walk(LOG_DIRECTORY):
        for file in files:
            # Check if the file matches the selected prefix and is not a gzipped file
            if any(file.startswith(prefix) and not file.endswith(".gz") for prefix in prefix_map[selected_file]):
                log_files.append(os.path.join(root_dir, file))  # Add the matching file to the list

    # If no log files are found, display an error message
    if not log_files:
        result_box.insert(tk.END, f"No log files found for '{selected_file}'.\n", "error")
        search_button.config(state=tk.NORMAL)
        return

    # Inform the user that the search is starting
    result_box.insert(tk.END, f"Searching for keywords: {', '.join(keywords)} in {selected_file}...\n\n")
    found = False  # Flag to track if any matches are found
    total_files = len(log_files)  # Total number of files to process
    keyword_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]
    # Search for keywords in each log file
    for index, log_file in enumerate(log_files):
        try:
            with open(log_file, 'r', buffering=8192) as file:
                # Read each line in the current log file
                for line_number, line in enumerate(file, 1):
                    # Check if all of the keywords are present in the line
                    if all(pattern.search(line) for pattern in keyword_patterns): #case-insensitively
                        # If a match is found, insert it into the result box
                        result_box.insert(tk.END, f"[{log_file} - Line {line_number}] {line.strip()}\n")
                        found = True
        except Exception as e:
            # Handle any errors that occur while reading the file
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n", "error")

        # Update the progress bar after processing each file
        progress_bar["value"] = ((index + 1) / total_files) * 100  # Calculate percentage of files processed
        root.update_idletasks()  # Update the GUI to reflect the new progress

    # Set the progress bar to complete
    progress_bar["value"] = 100
    progress_bar_label.config(text="Complete")  # Update label to indicate completion
    if not found:
        result_box.insert(tk.END, f"No matches found for keywords: {', '.join(keywords)}.\n", "error")
    else:
        result_box.insert(tk.END, "\nSearch completed.\n", "success")

    highlight_all_results(result_box, keywords)  # Highlight all found keywords in the results
    search_button.config(state=tk.NORMAL)  # Re-enable the search button

def highlight_all_results(result_box, keywords):
    """
    Highlight all occurrences of keywords in the result box after the search completes.
    """
    for keyword in keywords:
        start_pos = "1.0"  # Start searching from the beginning of the text
        while True:
            # Search for the keyword in the result box
            start_pos = result_box.search(keyword, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:  # If no more occurrences are found, exit the loop
                break
            end_pos = f"{start_pos}+{len(keyword)}c"  # Calculate the end position of the found keyword
            result_box.tag_add("highlight", start_pos, end_pos)  # Add a highlight tag to the found keyword
            result_box.tag_config("highlight", foreground="green", font=("Calibri", 9, "bold"))  # Configure the highlight style
            start_pos = end_pos  # Move past the last match to continue searching

def start_search(entry, selected_file, result_box, progress_bar, progress_bar_label, search_button):
    """
    Trigger the search with user input, handle button disable/enable, and progress updates.
    """
    input_text = entry.get().strip()  # Get the input keywords from the entry
    if not input_text:
        messagebox.showwarning("Warning", "Please enter keywords to search.")
        return
    keywords = input_text.split()  # Split input into multiple keywords
    result_box.delete(1.0, tk.END)  # Clear previous results
    progress_bar["value"] = 0  # Reset the progress bar
    progress_bar_label.config(text="In Progress ...")  # Set initial progress label text
    search_button.config(state=tk.DISABLED)  # Disable the search button to prevent multiple requests

    # Run the search in a separate thread to avoid freezing the GUI
    threading.Thread(target=search_logs, args=(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button)).start()

def create_gui():
    """
    Create the GUI application for searching log files.
    """
    global root  # To access the root window in other functions
    root = tk.Tk()
    root.title("Log Searcher")
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
    ttk.Label(frame, text="Enter keywords (separated by spaces):").grid(row=0, column=0, sticky=tk.W)
    keyword_entry = ttk.Entry(frame, width=50)  # Entry field for keywords
    keyword_entry.grid(row=0, column=1, padx=5)
    log_file_label = ttk.Label(frame, text="Select log file:")
    log_file_label.grid(row=1, column=0, sticky=tk.W)
    log_file_combobox = ttk.Combobox(frame, values=["All", "Address", "Audit.log", "Bruteforce", "IP_block", "Mailbox.log", "Zimbra.log"], state="readonly")
    log_file_combobox.set("All")  # Default selection
    log_file_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)
    progress_bar_label = ttk.Label(frame, text="In Progress ...")
    progress_bar_label.grid(row=1, column=2, padx=5, sticky=tk.W)
    progress_bar = ttk.Progressbar(frame, length=200, mode="determinate")  # Progress bar for search progress
    progress_bar.grid(row=1, column=3, padx=0, sticky=tk.W)
    search_button = ttk.Button(frame, text="Search", command=lambda: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))
    search_button.grid(row=0, column=2, padx=5)
    # Bind the "Return" key to trigger search
    keyword_entry.bind("<Return>", lambda event: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))
    result_box = scrolledtext.ScrolledText(root, width=250, height=50, wrap=tk.WORD)  # Scrolled text box for results
    result_box.grid(row=1, column=0, padx=10, pady=10)
    result_box.config(font=("Calibri", 9))  # Set font for the result box
    result_box.tag_config("success", foreground="green", font=("Calibri", 9, "bold"))  # Tag for success messages
    result_box.tag_config("error", foreground="red", font=("Calibri", 9, "bold"))  # Tag for error messages
    root.mainloop()  # Start the GUI event loop

if __name__ == "__main__":
    create_gui()  # Run the GUI application

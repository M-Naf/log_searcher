import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

# Define the directory where log files are stored
LOG_DIRECTORY = r"d:\dir\log"

# Event to allow cancellation of the search operation
cancel_event = threading.Event()

def search_logs(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button):
    """
    Search for multiple keywords in the selected log files within the fixed directory.
    Displays results immediately and updates the progress bar based on the number of files processed.
    """
    global cancel_event  # Use the global cancel_event to check for cancellation
    # Check if the specified log directory exists
    if not os.path.exists(LOG_DIRECTORY):
        messagebox.showerror("Error", f"Directory '{LOG_DIRECTORY}' does not exist.")
        search_button.config(state=tk.NORMAL)
        return

    log_files = []  # List to hold paths of log files to be searched
    # Define a mapping of file categories to their prefixes
    prefix_map = {
        "All": ["address", "audit.log", "Bruteforce", "ip_block", "mailbox.log", "zimbra.log"],
        "Address": ["address"],
        "Audit.log": ["audit.log"],
        "Bruteforce": ["Bruteforce"],
        "IP_block": ["ip_block"],
        "Mailbox.log": ["mailbox.log"],
        "Zimbra.log": ["zimbra.log"]
    }

    # Validate that the selected file type exists in the prefix map
    if selected_file not in prefix_map:
        messagebox.showerror("Error", f"Invalid selection '{selected_file}'.")
        search_button.config(state=tk.NORMAL)
        return

    # Traverse the directory to find files matching the selected type
    for root_dir, _, files in os.walk(LOG_DIRECTORY):
        for file in files:
            if any(file.startswith(prefix) and not file.endswith(".gz") for prefix in prefix_map[selected_file]):
                log_files.append(os.path.join(root_dir, file))

    # If no files match the selection, notify the user
    if not log_files:
        result_box.insert(tk.END, f"No log files found for '{selected_file}'.\n", "error")
        search_button.config(state=tk.NORMAL)
        return

    # Notify the user that the search has started
    result_box.insert(tk.END, f"Searching for keywords: {', '.join(keywords)} in {selected_file}...\n\n")
    found = False  # Flag to indicate if any matches are found
    total_files = len(log_files)  # Total number of files to process

    # Compile the keyword patterns with case-insensitive matching
    keyword_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]

    # Process each log file
    for index, log_file in enumerate(log_files):
        if cancel_event.is_set():  # Stop if the cancel event is set
            result_box.insert(tk.END, "Search cancelled by user.\n", "error")
            search_button.config(state=tk.NORMAL)
            return

        try:
            with open(log_file, 'r', buffering=8192) as file:
                # Read and search each line in the log file
                for line_number, line in enumerate(file, 1):
                    if all(pattern.search(line) for pattern in keyword_patterns):
                        result_box.insert(tk.END, f"[{log_file} - Line {line_number}] {line.strip()}\n")
                        found = True
        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n", "error")

        # Update the progress bar
        progress_bar["value"] = ((index + 1) / total_files) * 100
        root.update_idletasks()

    # Finalize the progress bar
    progress_bar["value"] = 100
    progress_bar_label.config(text="Complete")
    if not found:
        result_box.insert(tk.END, f"No matches found for keywords: {', '.join(keywords)}.\n", "error")
    else:
        result_box.insert(tk.END, "\nSearch completed.\n", "success")

    # Highlight the results
    highlight_all_results(result_box, keywords)
    search_button.config(state=tk.NORMAL)

def highlight_all_results(result_box, keywords):
    """
    Highlight all occurrences of keywords in the result box after the search completes.
    """
    for keyword in keywords:
        start_pos = "1.0"  # Start at the beginning of the text box
        while True:
            # Search for the keyword, case-insensitively
            start_pos = result_box.search(keyword, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break  # Stop if no more matches are found
            end_pos = f"{start_pos}+{len(keyword)}c"  # Calculate the end position
            result_box.tag_add("highlight", start_pos, end_pos)  # Highlight the found text
            result_box.tag_config("highlight", foreground="green", font=("Calibri", 9, "bold"))
            start_pos = end_pos  # Move to the end of the last match

def start_search(entry, selected_file, result_box, progress_bar, progress_bar_label, search_button):
    """
    Start the search operation, taking user input and managing the progress bar and cancel events.
    """
    input_text = entry.get().strip()
    if not input_text:
        messagebox.showwarning("Warning", "Please enter keywords to search.")
        return

    # Extract quoted and unquoted keywords using regex
    keywords = re.findall(r'"(.*?)"|(\S+)', input_text)
    keywords = [k[0] or k[1] for k in keywords]  # Flatten the list and filter None values

    result_box.delete(1.0, tk.END)  # Clear the results box
    progress_bar["value"] = 0  # Reset the progress bar
    progress_bar_label.config(text="In Progress ...")
    search_button.config(state=tk.DISABLED)  # Disable the search button
    cancel_event.clear()  # Reset the cancel event

    # Start the search in a separate thread
    threading.Thread(target=search_logs, args=(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button)).start()

def cancel_search(search_button):
    """
    Cancel the ongoing search operation.
    """
    global cancel_event
    cancel_event.set()  # Signal the cancellation
    search_button.config(state=tk.NORMAL)

def create_gui():
    """
    Create and initialize the GUI for the log search application.
    """
    global root
    root = tk.Tk()
    root.title("Log Searcher")
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    # Input for keywords
    ttk.Label(frame, text="Enter keywords (separated by spaces):").grid(row=0, column=0, sticky=tk.W)
    keyword_entry = ttk.Entry(frame, width=50)
    keyword_entry.grid(row=0, column=1, padx=5)

    # Dropdown for selecting log file type
    log_file_label = ttk.Label(frame, text="Select log file:")
    log_file_label.grid(row=1, column=0, sticky=tk.W)
    log_file_combobox = ttk.Combobox(frame, values=["All", "Address", "Audit.log", "Bruteforce", "IP_block", "Mailbox.log", "Zimbra.log"], state="readonly")
    log_file_combobox.set("All")
    log_file_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

    # Progress bar and labels
    progress_bar_label = ttk.Label(frame, text="In Progress ...")
    progress_bar_label.grid(row=1, column=2, padx=5, sticky=tk.W)
    progress_bar = ttk.Progressbar(frame, length=200, mode="determinate")
    progress_bar.grid(row=1, column=3, padx=0, sticky=tk.W)

    # Buttons for search and cancel
    search_button = ttk.Button(frame, text="Search", command=lambda: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))
    search_button.grid(row=0, column=2, padx=5)
    cancel_button = ttk.Button(frame, text="Cancel", command=lambda: cancel_search(search_button))
    cancel_button.grid(row=0, column=3, padx=5)

    # Bind Enter key to start the search
    keyword_entry.bind("<Return>", lambda event: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))

    # Text box for displaying results
    result_box = scrolledtext.ScrolledText(root, width=250, height=50, wrap=tk.WORD)
    result_box.grid(row=1, column=0, padx=10, pady=10)
    result_box.config(font=("Calibri", 9))
    result_box.tag_config("success", foreground="green", font=("Calibri", 9, "bold"))
    result_box.tag_config("error", foreground="red", font=("Calibri", 9, "bold"))

    root.mainloop()  # Start the GUI event loop

if __name__ == "__main__":
    create_gui()  # Initialize the GUI application

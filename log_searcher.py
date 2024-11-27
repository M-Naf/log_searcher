import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

# Fixed directory for logs
LOG_DIRECTORY = r"\\sh2\mail$\log"

def highlight_keywords(result_box, line, keywords, log_file, line_number):
    """
    :param result_box: The scrolled text widget for displaying results.
    :param line: The line of text to search through.
    :param keywords: List of keywords to search for.
    :param log_file: The log file name (for display in results).
    :param line_number: The line number in the log file.
    """
    result_box.insert(tk.END, f"\n[{log_file} - Line {line_number}] ")
    
    start_index = result_box.index(tk.END)  # Store where the text insertion ends before adding any tags
    result_box.insert(tk.END, line.strip())  # Insert the line into the result box
    
    # Now, go through the line and highlight keywords
    for keyword in keywords:
        start_pos = '1.0'  # Start from the beginning of the line
        while True:
            start_pos = result_box.search(keyword, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(keyword)}c"
            # Apply a tag to highlight the keyword
            result_box.tag_add("highlight", start_pos, end_pos)
            result_box.tag_config("highlight", foreground="red", font=("Arial", 10, "bold"))  # Highlight style
            start_pos = end_pos  # Move past the last match

def search_logs(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button):
    """
    Search for multiple keywords in the selected log file within the fixed directory.
    
    1. Improved error handling when reading files.
    2. Optimized file reading with buffering and progress bar updates.
    3. Handled large file efficiently using buffered reading.
    """
    # Ensure directory exists only once
    if not os.path.exists(LOG_DIRECTORY):
        messagebox.showerror("Error", f"Directory '{LOG_DIRECTORY}' does not exist.")
        search_button.config(state=tk.NORMAL)
        return

    log_files = []
    if selected_file == "All":
        log_files = [
            f for f in os.listdir(LOG_DIRECTORY)
            if (f.startswith("audit.log") or f.startswith("mailbox.log") or f.startswith("zimbra.log"))
            and not f.endswith(".gz") and os.path.isfile(os.path.join(LOG_DIRECTORY, f))
        ]
    else:
        log_files = [
            f for f in os.listdir(LOG_DIRECTORY)
            if f.startswith(selected_file) and not f.endswith(".gz") and os.path.isfile(os.path.join(LOG_DIRECTORY, f))
        ]
    
    if not log_files:
        result_box.insert(tk.END, f"No log files found for '{selected_file}'.\n")
        search_button.config(state=tk.NORMAL)
        return

    result_box.insert(tk.END, f"Searching for keywords: {', '.join(keywords)} in {selected_file}...\n\n")
    found = False
    total_lines = 0
    current_line = 0

    # Count total lines for progress bar
    for log_file in log_files:
        log_path = os.path.join(LOG_DIRECTORY, log_file)
        try:
            with open(log_path, 'r', buffering=8192) as file:  # Open file with buffered read
                total_lines += sum(1 for line in file)  # Count number of lines
        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n")

    # Search for keywords with optimized handling of large files
    for log_file in log_files:
        log_path = os.path.join(LOG_DIRECTORY, log_file)
        try:
            with open(log_path, 'r', buffering=8192) as file:
                for line_number, line in enumerate(file, 1):
                    current_line += 1
                    progress_bar["value"] = (current_line / total_lines) * 100
                    root.update_idletasks()  # Update progress bar

                    # Check if the line contains all keywords
                    if all(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                        highlight_keywords(result_box, line, keywords, log_file, line_number)
                        found = True
        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n")

    # Final update of progress bar
    progress_bar["value"] = 100
    progress_bar_label.config(text="Complete")

    if not found:
        result_box.insert(tk.END, f"No matches found for keywords: {', '.join(keywords)}.\n")
    else:
        result_box.insert(tk.END, "\n\nSearch completed.\n")

    search_button.config(state=tk.NORMAL)

def start_search(entry, selected_file, result_box, progress_bar, progress_bar_label, search_button):
    """Trigger the search with user input, handle button disable/enable and progress updates."""
    input_text = entry.get().strip()
    if not input_text:
        messagebox.showwarning("Warning", "Please enter keywords to search.")
        return

    keywords = input_text.split()  # Split input into multiple keywords
    result_box.delete(1.0, tk.END)  # Clear previous results
    progress_bar["value"] = 0  # Reset the progress bar
    progress_bar_label.config(text="In Progress ...")  # Set initial progress label text

    # Disable the search button to prevent multiple search requests during the search
    search_button.config(state=tk.DISABLED)

    # Run the search in a separate thread to avoid freezing the GUI
    threading.Thread(target=search_logs, args=(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button)).start()

def create_gui():
    """Create the GUI application."""
    global root  # To access the root window in other functions

    root = tk.Tk()
    root.title("Log Searcher")

    # Frame for keyword input
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    ttk.Label(frame, text="Enter keywords (separated by spaces):").grid(row=0, column=0, sticky=tk.W)
    keyword_entry = ttk.Entry(frame, width=50)
    keyword_entry.grid(row=0, column=1, padx=5)

    # Create Combobox for selecting log file
    log_file_label = ttk.Label(frame, text="Select log file:")
    log_file_label.grid(row=1, column=0, sticky=tk.W)
    log_file_combobox = ttk.Combobox(frame, values=["All", "audit.log", "mailbox.log", "zimbra.log"], state="readonly")
    log_file_combobox.set("All")  # Default selection
    log_file_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

    # Create progress bar for search progress
    progress_bar_label = ttk.Label(frame, text="In Progress ...")
    progress_bar_label.grid(row=1, column=2, padx=5, sticky=tk.W)
    progress_bar = ttk.Progressbar(frame, length=200, mode="determinate")
    progress_bar.grid(row=1, column=3, padx=0, sticky=tk.W)

    # Create Search button
    search_button = ttk.Button(frame, text="Search", command=lambda: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))
    search_button.grid(row=0, column=2, padx=5)

    # Bind the "Return" key to trigger search
    keyword_entry.bind("<Return>", lambda event: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))

    # Scrolled text box for results
    result_box = scrolledtext.ScrolledText(root, width=230, height=50, wrap=tk.WORD)  # Enable word wrap
    result_box.grid(row=1, column=0, padx=10, pady=10)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    create_gui()

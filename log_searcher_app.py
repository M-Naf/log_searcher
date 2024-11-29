import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

# Fixed directory for logs
LOG_DIRECTORY = r"\\directory\log"

def search_logs(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button):
    """
    Search for multiple keywords in the selected log file within the fixed directory, recursively.
    Displays results immediately and highlights them after the search is complete.
    """
    if not os.path.exists(LOG_DIRECTORY):
        messagebox.showerror("Error", f"Directory '{LOG_DIRECTORY}' does not exist.")
        search_button.config(state=tk.NORMAL)
        return

    log_files = []
    prefix_map = {
        "All": ["audit.log", "mailbox.log", "zimbra.log", "ip_block"],
        "audit.log": ["audit.log"],
        "ip_block": ["ip_block"],
        "mailbox.log": ["mailbox.log"],
        "zimbra.log": ["zimbra.log"]
    }

    if selected_file not in prefix_map:
        messagebox.showerror("Error", f"Invalid selection '{selected_file}'.")
        search_button.config(state=tk.NORMAL)
        return

    # Traverse the directory recursively
    for root_dir, _, files in os.walk(LOG_DIRECTORY):
        for file in files:
            if any(file.startswith(prefix) and not file.endswith(".gz") for prefix in prefix_map[selected_file]):
                log_files.append(os.path.join(root_dir, file))

    if not log_files:
        result_box.insert(tk.END, f"No log files found for '{selected_file}'.\n", "error")
        search_button.config(state=tk.NORMAL)
        return

    result_box.insert(tk.END, f"Searching for keywords: {', '.join(keywords)} in {selected_file}...\n\n")
    found = False
    total_lines = 0
    current_line = 0

    # Count total lines for progress bar
    for log_file in log_files:
        try:
            with open(log_file, 'r', buffering=8192) as file:
                total_lines += sum(1 for line in file)
        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n", "error")

    # Search and display results
    for log_file in log_files:
        try:
            with open(log_file, 'r', buffering=8192) as file:
                for line_number, line in enumerate(file, 1):
                    current_line += 1
                    progress_bar["value"] = (current_line / total_lines) * 100
                    root.update_idletasks()

                    # Check if the line contains all keywords
                    if all(re.search(keyword, line, re.IGNORECASE) for keyword in keywords):
                        result_box.insert(tk.END, f"[{log_file} - Line {line_number}] {line.strip()}\n")
                        found = True
        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n", "error")

    # Final update of progress bar
    progress_bar["value"] = 100
    progress_bar_label.config(text="Complete")

    if not found:
        result_box.insert(tk.END, f"No matches found for keywords: {', '.join(keywords)}.\n", "error")
    else:
        result_box.insert(tk.END, "\nSearch completed.\n", "success")

    # Highlight keywords after search
    highlight_all_results(result_box, keywords)

    search_button.config(state=tk.NORMAL)


def highlight_all_results(result_box, keywords):
    """
    Highlight all occurrences of keywords in the result box after search completes.
    """
    for keyword in keywords:
        start_pos = "1.0"  # Start at the beginning of the text
        while True:
            start_pos = result_box.search(keyword, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(keyword)}c"
            result_box.tag_add("highlight", start_pos, end_pos)
            result_box.tag_config("highlight", foreground="green", font=("Calibri", 9, "bold"))
            start_pos = end_pos  # Move past the last match


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
    log_file_combobox = ttk.Combobox(frame, values=["All", "audit.log", "ip_block", "mailbox.log", "zimbra.log"], state="readonly")
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
    result_box = scrolledtext.ScrolledText(root, width=250, height=50, wrap=tk.WORD)  # Enable word wrap
    result_box.grid(row=1, column=0, padx=10, pady=10)
    result_box.config(font=("Calibri", 9))
    result_box.tag_config("success", foreground="green", font=("Calibri", 9, "bold"))
    result_box.tag_config("error", foreground="red", font=("Calibri", 9, "bold"))

    # Run the application
    root.mainloop()


if __name__ == "__main__":
    create_gui()

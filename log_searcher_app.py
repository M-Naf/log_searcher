import os
import re
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading

LOG_DIRECTORY = r"d:\dir\log"  #directory for logs
cancel_event = threading.Event()  # Event to control cancellation of the search

def search_logs(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button):
    """
    Search for multiple keywords in the selected log files within the fixed directory.
    Displays results immediately and updates the progress bar based on the number of files processed.
    """
    global cancel_event  # Use the global cancel_event to check for cancellation
    if not os.path.exists(LOG_DIRECTORY):
        messagebox.showerror("Error", f"Directory '{LOG_DIRECTORY}' does not exist.")
        search_button.config(state=tk.NORMAL)
        return

    log_files = []
    prefix_map = {
        "All": ["address", "audit.log", "Bruteforce", "ip_block", "mailbox.log", "zimbra.log"],
        "Address": ["address"],
        "Audit.log": ["audit.log"],
        "Bruteforce": ["Bruteforce"],
        "IP_block": ["ip_block"],
        "Mailbox.log": ["mailbox.log"],
        "Zimbra.log": ["zimbra.log"]
    }

    if selected_file not in prefix_map:
        messagebox.showerror("Error", f"Invalid selection '{selected_file}'.")
        search_button.config(state=tk.NORMAL)
        return

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
    total_files = len(log_files)
    keyword_patterns = [re.compile(re.escape(keyword), re.IGNORECASE) for keyword in keywords]

    for index, log_file in enumerate(log_files):
        if cancel_event.is_set():  # Check if the search has been cancelled
            result_box.insert(tk.END, "Search cancelled by user.\n", "error")
            search_button.config(state=tk.NORMAL)
            return

        try:
            with open(log_file, 'r', buffering=8192) as file:
                for line_number, line in enumerate(file, 1):
                    if all(pattern.search(line) for pattern in keyword_patterns):
                        result_box.insert(tk.END, f"[{log_file} - Line {line_number}] {line.strip()}\n")
                        found = True
        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n", "error")

        progress_bar["value"] = ((index + 1) / total_files) * 100
        root.update_idletasks()

    progress_bar["value"] = 100
    progress_bar_label.config(text="Complete")
    if not found:
        result_box.insert(tk.END, f"No matches found for keywords: {', '.join(keywords)}.\n", "error")
    else:
        result_box.insert(tk.END, "\nSearch completed.\n", "success")
    highlight_all_results(result_box, keywords)
    search_button.config(state=tk.NORMAL)

def highlight_all_results(result_box, keywords):
    for keyword in keywords:
        start_pos = "1.0"
        while True:
            start_pos = result_box.search(keyword, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(keyword)}c"
            result_box.tag_add("highlight", start_pos, end_pos)
            result_box.tag_config("highlight", foreground="green", font=("Calibri", 9, "bold"))
            start_pos = end_pos

def start_search(entry, selected_file, result_box, progress_bar, progress_bar_label, search_button):
    input_text = entry.get().strip()
    if not input_text:
        messagebox.showwarning("Warning", "Please enter keywords to search.")
        return
    
    # Use regex to find quoted keywords and separate them from unquoted ones
    keywords = re.findall(r'"(.*?)"|(\S+)', input_text)
    keywords = [k[0] or k[1] for k in keywords]  # Flatten the list and filter None values

    result_box.delete(1.0, tk.END)
    progress_bar["value"] = 0
    progress_bar_label.config(text="In Progress ...")
    search_button.config(state=tk.DISABLED)
    cancel_event.clear()  # Clear the cancel event
    threading.Thread(target=search_logs, args=(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button)).start()


def cancel_search(search_button):
    global cancel_event
    cancel_event.set()  # Set the cancel event to stop the search
    search_button.config(state=tk.NORMAL)  # Re-enable the search button

def save_results(result_box):
    """Save the content of the result box to a text file."""
    # Open a file dialog to choose the save location
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:  # Ensure a file path was selected
        try:
            with open(file_path, 'w') as file:
                file.write(result_box.get(1.0, tk.END))  # Get all text from the result box
            messagebox.showinfo("Saved", f"Results saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

def create_gui():
    global root
    root = tk.Tk()
    root.title("Log Searcher (By M.Naf)")
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E))

    # Existing GUI elements
    ttk.Label(frame, text="Enter keywords (separated by spaces):").grid(row=0, column=0, sticky=tk.W)
    keyword_entry = ttk.Entry(frame, width=50)
    keyword_entry.grid(row=0, column=1, padx=5)

    log_file_label = ttk.Label(frame, text="Select log file:")
    log_file_label.grid(row=1, column=0, sticky=tk.W)
    log_file_combobox = ttk.Combobox(frame, values=["All", "Address", "Audit.log", "Bruteforce", "IP_block", "Mailbox.log", "Zimbra.log"], state="readonly")
    log_file_combobox.set("All")
    log_file_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)

    progress_bar_label = ttk.Label(frame, text="In Progress ...")
    progress_bar_label.grid(row=1, column=2, padx=5, sticky=tk.W)
    progress_bar = ttk.Progressbar(frame, length=200, mode="determinate")
    progress_bar.grid(row=1, column=3, padx=0, sticky=tk.W)

    search_button = ttk.Button(frame, text="Search", command=lambda: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))
    search_button.grid(row=0, column=2, padx=5)

    cancel_button = ttk.Button(frame, text="Cancel", command=lambda: cancel_search(search_button))
    cancel_button.grid(row=0, column=4, padx=5)

    save_button = ttk.Button(frame, text="Save", command=lambda: save_results(result_box))
    save_button.grid(row=0, column=5, padx=5)
    

    keyword_entry.bind("<Return>", lambda event: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))

    result_box = scrolledtext.ScrolledText(root, width=250, height=50, wrap=tk.WORD)
    result_box.grid(row=1, column=0, padx=5, pady=10)
    
    result_box.config(font=("Calibri", 9))
    result_box.tag_config("success", foreground="green", font=("Calibri", 9, "bold"))
    result_box.tag_config("error", foreground="red", font=("Calibri", 9, "bold"))
    #footer label
    footer_label = ttk.Label(root, text="Copyright M.Naf 2024", foreground="green",font=("Calibri", 9, "bold"))
    footer_label.grid(row=2, column=0, pady=10,padx=30, sticky=tk.E)
    #default icon
    try:
        root.iconbitmap(r"E:\icon\logS.ico")  
    except Exception as e:
        print(f"Error setting icon: {e}")
    root.mainloop()

if __name__ == "__main__":
    create_gui()

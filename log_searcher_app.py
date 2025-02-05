import os  # Module for interacting with the operating system
import re  # Module for regular expressions
import tkinter as tk  # Tkinter module for GUI creation
from tkinter import ttk, scrolledtext, messagebox, filedialog  # Additional Tkinter components
import threading  # Module for creating and managing threads

# Directory where log files are stored
LOG_DIRECTORY = r"d:\dir\log"  
# Event to control the cancellation of the search operation
cancel_event = threading.Event()  

def search_logs(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button):
    """
    Search for multiple keywords in the selected log files within the fixed directory.
    Displays results immediately and updates the progress bar based on the number of files processed.
    """
    global cancel_event  # Use the global cancel_event to check for cancellation
    
    # Check if the log directory exists
    if not os.path.exists(LOG_DIRECTORY):
        messagebox.showerror("Error", f"Directory '{LOG_DIRECTORY}' does not exist.")  # Show error message
        search_button.config(state=tk.NORMAL)  # Re-enable the search button
        return

    log_files = []  # List to hold found log files
    # Map of prefixes to log files based on user selection
    prefix_map = {
        "- all": ["address", "audit.log", "Bruteforce", "ip_block", "fail2ban.log", "mailbox.log", "zimbra.log"],
        "- address": ["address"],
        "- audit": ["audit.log"],
        "- bruteforce": ["Bruteforce"],
        "- ip": ["ip_block"],
        "- fail2ban": ["fail2ban.log"],
        "- mailbox": ["mailbox.log"],
        "- zimbra": ["zimbra.log"]
    }

    # Validate the selected file from the combobox
    if selected_file not in prefix_map:
        messagebox.showerror("Error", f"Invalid selection '{selected_file}'.")  # Show error for invalid selection
        search_button.config(state=tk.NORMAL)  # Re-enable the search button
        return

    # Walk through the log directory to find relevant log files
    for root_dir, _, files in os.walk(LOG_DIRECTORY):
        for file in files:
            # Check if the file matches any of the prefixes and is not a compressed file (.gz)
            if any(file.startswith(prefix) and not file.endswith(".gz") for prefix in prefix_map[selected_file]):
                log_files.append(os.path.join(root_dir, file))  # Add the file to the list

    # If no log files are found, notify the user and exit
    if not log_files:
        result_box.insert(tk.END, f"No log files found for '{selected_file}'.\n", "error")  # Show message in result box
        search_button.config(state=tk.NORMAL)  # Re-enable the search button
        return

    # Notify user of the search initiation
    result_box.insert(tk.END, f"Searching for keywords: {' '.join(keywords)} in {selected_file}...\n\n")
    found = False  # Flag to check if any matches were found
    total_files = len(log_files)  # Total number of files to process

    # Process search terms: separate them based on "or" and group by "and"
    or_groups = []  # Stores groups of AND conditions
    temp_and_group = []  # Temporary storage for AND conditions

    # Organize keywords into groups for searching
    for term in keywords:
        if term.lower() == "or":
            if temp_and_group:
                or_groups.append(temp_and_group)  # Save the current AND group
                temp_and_group = []  # Reset for the next OR group
        elif term.lower() != "and":
            temp_and_group.append(term)  # Add keyword to the current AND group
    if temp_and_group:
        or_groups.append(temp_and_group)  # Append the last AND group

    # Iterate through each log file and search for keywords
    for index, log_file in enumerate(log_files):
        if cancel_event.is_set():  # Check if the search has been cancelled
            result_box.insert(tk.END, "Search cancelled by user.\n", "error")  # Notify cancellation
            search_button.config(state=tk.NORMAL)  # Re-enable the search button
            return

        try:
            with open(log_file, 'r', buffering=8192) as file:  # Open log file for reading
                for line_number, line in enumerate(file, 1):  # Read each line with line numbers
                    match_found = False  # Flag for finding a match
                    # Check if the line matches any of the OR groups
                    for and_conditions in or_groups:
                        if all(re.search(re.escape(keyword.strip()), line, re.IGNORECASE) for keyword in and_conditions):
                            match_found = True  # A match was found
                            break  # Stop checking if one OR group matches
                    if match_found:
                        result_box.insert(tk.END, f"[{log_file} - Line {line_number}] {line.strip()}\n")  # Output the match
                        found = True  # Set found flag to true

        except Exception as e:
            result_box.insert(tk.END, f"Error reading file '{log_file}': {e}\n", "error")  # Handle file read errors

        # Update progress bar based on the number of files processed
        progress_bar["value"] = ((index + 1) / total_files) * 100
        root.update_idletasks()  # Update the GUI with the current state

    progress_bar["value"] = 100  # Set progress bar to complete
    progress_bar_label.config(text="Complete")  # Update label to show completion

    # Notify if no matches were found
    if not found:
        result_box.insert(tk.END, f"No matches found for keywords: {' '.join(keywords)}.\n", "error")
    else:
        result_box.insert(tk.END, "\nSearch completed.\n", "success")  # Notify successful completion

    highlight_all_results(result_box, keywords)  # Highlight results after search is complete
    search_button.config(state=tk.NORMAL)  # Re-enable the search button

def highlight_all_results(result_box, keywords):
    """
    Highlight all occurrences of the keywords in the result box.
    """
    for keyword in keywords:
        if keyword.lower() in ["and", "or"]:  # Skip highlighting "and" and "or"
            continue  
        start_pos = "1.0"  # Start position for search
        while True:
            # Search for the keyword in the result box
            start_pos = result_box.search(keyword, start_pos, stopindex=tk.END, nocase=True)
            if not start_pos:  # If no more occurrences are found, break
                break
            end_pos = f"{start_pos}+{len(keyword)}c"  # Calculate end position of the found keyword
            result_box.tag_add("highlight", start_pos, end_pos)  # Add highlight tag
            result_box.tag_config("highlight", foreground="green", font=("Calibri", 9, "bold"))  # Configure highlight style
            start_pos = end_pos  # Move start position for next search

def start_search(entry, selected_file, result_box, progress_bar, progress_bar_label, search_button):
    """
    Initiate the search process based on user input.
    """
    input_text = entry.get().strip()  # Get the input text from the entry field
    if not input_text:  # Check if input is empty
        messagebox.showwarning("Warning", "Please enter keywords to search.")  # Show warning
        return

    # Use regex to find quoted keywords and separate them from unquoted ones
    keywords = re.findall(r'"(.*?)"|(\S+)', input_text)  # Find quoted and unquoted keywords
    keywords = [k[0] or k[1] for k in keywords]  # Flatten the list and filter None values

    # Clear previous results and reset UI elements
    result_box.delete(1.0, tk.END)  # Clear the result box
    progress_bar["value"] = 0  # Reset progress bar
    progress_bar_label.config(text="In Progress ...")  # Update label
    search_button.config(state=tk.DISABLED)  # Disable search button
    cancel_event.clear()  # Clear the cancel event to allow for a new search

    # Start the search in a new thread to avoid freezing the GUI
    threading.Thread(target=search_logs, args=(selected_file, keywords, result_box, progress_bar, progress_bar_label, search_button)).start()

def cancel_search(search_button):
    """
    Cancel the ongoing search operation.
    """
    global cancel_event
    cancel_event.set()  # Set the cancel event to stop the search
    search_button.config(state=tk.NORMAL)  # Re-enable the search button

def save_results(result_box):
    """Save the content of the result box to a text file."""
    # Open a file dialog to choose where to save the results
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:  # Ensure a file path was selected
        try:
            with open(file_path, 'w') as file:
                file.write(result_box.get(1.0, tk.END))  # Get all text from the result box
            messagebox.showinfo("Saved", f"Results saved to {file_path}")  # Notify user of successful save
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")  # Show error if save fails

def create_gui():
    """
    Create and configure the main GUI window.
    """
    global root
    root = tk.Tk()  # Create the main window
    root.title("Log Searcher (By M.Naf)")  # Set the window title
    frame = ttk.Frame(root, padding="10")  # Create a frame for layout
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E))  # Place the frame in the window

    # GUI elements for keyword input
    ttk.Label(frame, text="keywords (Use 'and/or'):").grid(row=0, column=0, sticky=tk.W)  # Label for keywords
    keyword_entry = ttk.Entry(frame, width=100)  # Entry field for keywords
    keyword_entry.grid(row=0, column=1, padx=5)  # Place the entry field

    # GUI elements for log file selection
    log_file_label = ttk.Label(frame, text="Select log file:")  # Label for log file selection
    log_file_label.grid(row=1, column=0, sticky=tk.W)  # Place the label
    # Combobox for selecting log file type
    log_file_combobox = ttk.Combobox(frame, values=["- all", "- address", "- audit", "- bruteforce", "- ip", "- fail2ban", "- mailbox", "- zimbra"], state="readonly")
    log_file_combobox.set("- all")  # Set default selection
    log_file_combobox.grid(row=1, column=1, padx=5, sticky=tk.W)  # Place the combobox

    # GUI elements for progress indication
    progress_bar_label = ttk.Label(frame, text="In Progress ...")  # Label for progress
    progress_bar_label.grid(row=1, column=2, padx=5, sticky=tk.W)  # Place the label
    progress_bar = ttk.Progressbar(frame, length=200, mode="determinate")  # Create a progress bar
    progress_bar.grid(row=1, column=3, padx=0, sticky=tk.W)  # Place the progress bar

    # Search button to initiate the search
    search_button = ttk.Button(frame, text="Search", command=lambda: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))
    search_button.grid(row=0, column=2, padx=5)  # Place the search button

    # Cancel button to stop the search
    cancel_button = ttk.Button(frame, text="Cancel", command=lambda: cancel_search(search_button))
    cancel_button.grid(row=0, column=4, padx=5)  # Place the cancel button

    # Save button to save results to a file
    save_button = ttk.Button(frame, text="Save", command=lambda: save_results(result_box))
    save_button.grid(row=0, column=5, padx=5)  # Place the save button

    # Bind the Enter key to trigger the search
    keyword_entry.bind("<Return>", lambda event: start_search(keyword_entry, log_file_combobox.get(), result_box, progress_bar, progress_bar_label, search_button))

    # Text area for displaying search results
    result_box = scrolledtext.ScrolledText(root, width=250, height=50, wrap=tk.WORD)  # Create a scrollable text area
    result_box.grid(row=1, column=0, padx=5, pady=10)  # Place the text area
    result_box.config(font=("Calibri", 9))  # Set font for the text area
    # Configure text tags for success and error messages
    result_box.tag_config("success", foreground="green", font=("Calibri", 9, "bold"))
    result_box.tag_config("error", foreground="red", font=("Calibri", 9, "bold"))

    # Footer label with copyright information
    footer_label = ttk.Label(root, text="Copyright M.Naf 2024", foreground="green", font=("Calibri", 9, "bold"))
    footer_label.grid(row=2, column=0, pady=10, padx=30, sticky=tk.E)  # Place the footer label

    # Default icon for the application window
    try:
        root.iconbitmap(r"E:\Documents\formation\log.ico")  # Set application icon
    except Exception as e:
        print(f"Error setting icon: {e}")  # Print error if icon setting fails

    root.mainloop()  # Start the Tkinter main loop

if __name__ == "__main__":
    create_gui()  # Call the function to create and display the GUI

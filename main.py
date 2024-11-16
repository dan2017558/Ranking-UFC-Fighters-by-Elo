import tkinter as tk
from tkinter import messagebox
import pandas as pd
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox


def update_suggestions(event):
    """Update the suggestions based on the user input."""
    search_term = entry.get().strip().lower()
    
    if not search_term:
        suggestions_frame.place_forget()  # Hide the suggestions frame when there's no input
        return

    # Get fighter names and filter based on the search term
    fighter_names = [name for name in all_fighter_names if search_term in name.lower()]
    
    # Clear the listbox and insert the filtered names
    listbox.delete(0, tk.END)
    for name in fighter_names[:5]:  # Show only the top 5 suggestions
        listbox.insert(tk.END, name)
    
    # Show the listbox if there are suggestions
    if fighter_names:
        suggestions_frame.place(x=entry.winfo_x(), y=entry.winfo_y() + entry.winfo_height() + 5)
    else:
        suggestions_frame.place_forget()  # Hide the listbox if no suggestions


def on_select_fighter(event):
    """Auto-fill the selected fighter name into the entry field."""
    selected_fighter = listbox.get(listbox.curselection())
    entry.delete(0, tk.END)
    entry.insert(tk.END, selected_fighter)
    suggestions_frame.place_forget()  # Hide the suggestions once a name is selected


def show_fighter_data():
    fighter_name = entry.get().strip()
    if fighter_name == "":
        Messagebox.show_error("Error", "Please enter a fighter's name.")
        return

    try:
        # Load data from the CSV file
        df = pd.read_csv("records.csv")
    except FileNotFoundError:
        Messagebox.show_error("Error", "The file 'records.csv' was not found.")
        return
    except Exception as e:
        Messagebox.show_error("Error", f"An error occurred while reading the file: {e}")
        return

    # Validate that the required columns exist in the CSV
    required_columns = {"Fighter", "Elo", "Opponent", "Change"}
    if not required_columns.issubset(df.columns):
        Messagebox.show_error(
            "Error", f"The file must contain the following columns: {', '.join(required_columns)}"
        )
        return

    # Standardize fighter names (remove extra spaces and make case-insensitive)
    df["Fighter"] = df["Fighter"].str.strip().str.lower()
    fighter_name = fighter_name.lower()

    # Filter the data for the given fighter
    fighter_data = df[df["Fighter"] == fighter_name]

    # Clear previous results if any
    for widget in results_frame.winfo_children():
        widget.destroy()

    if fighter_data.empty:
        Messagebox.show_info("No Data", f"No data found for fighter: {fighter_name.title()}")
    else:
        # Display the fighter's data in the same window
        result_label = ttk.Label(results_frame, text=f"Results for {fighter_name.title()}:")
        result_label.pack(pady=10)

        # Create a Treeview to display the data
        tree = ttk.Treeview(results_frame, columns=list(fighter_data.columns), show="headings")
        tree.pack(fill=tk.BOTH, expand=True)

        # Set up the column headers
        for col in fighter_data.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)

        # Insert the data into the Treeview
        for _, row in fighter_data.iterrows():
            tree.insert("", tk.END, values=list(row))


# Create the main application window with ttkbootstrap style
root = ttk.Window(themename="darkly")
root.title("Fighter Data Viewer")
root.geometry("800x600")  # Set a larger window size to fit all elements
root.minsize(800, 600)  # Set minimum size to ensure it is large enough for the widgets

# Create the input field and button with modern styling
frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

label = ttk.Label(frame, text="Enter Fighter Name:", font=("Helvetica", 12))
label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

entry = ttk.Entry(frame, font=("Helvetica", 12), bootstyle="info")
entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

button = ttk.Button(frame, text="Search", bootstyle="success", command=show_fighter_data)
button.grid(row=0, column=2, padx=10, pady=5)

# Make the entry widget expand horizontally
frame.grid_columnconfigure(1, weight=1)  # Make column 1 (entry) expand with window size

# Create a frame for suggestions below the entry field
suggestions_frame = ttk.Frame(root)
suggestions_frame.place_forget()  # Hide it initially

# Create the listbox for the suggestions
listbox = tk.Listbox(suggestions_frame, height=5, width=40, selectmode=tk.SINGLE, font=("Helvetica", 12))
listbox.bind("<ButtonRelease-1>", on_select_fighter)
listbox.pack()

# Load fighter names into the listbox
try:
    df = pd.read_csv("records.csv")
    all_fighter_names = df["Fighter"].str.strip().str.title().drop_duplicates().tolist()
except FileNotFoundError:
    Messagebox.show_error("Error", "The file 'records.csv' was not found.")
    all_fighter_names = []
except Exception as e:
    Messagebox.show_error("Error", f"An error occurred while reading the file: {e}")
    all_fighter_names = []

# Create a frame for the search results
results_frame = ttk.Frame(root, padding="20")
results_frame.pack(fill=tk.BOTH, expand=True)

# Attach the event handler for updating suggestions
entry.bind("<KeyRelease>", update_suggestions)

# Start the Tkinter event loop
root.mainloop()

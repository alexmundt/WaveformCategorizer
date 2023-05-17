from GUI import MainFrame
import tkinter as tk
from tkinter import ttk

# Declare general options here:
# mseed files to read are in the folder
folder_name = "example data"
# the maximum frequency to be displayed in the Fourier domain
max_freq = 0.9


root = tk.Tk()
root.title("DataCategorizer")
mainframe = MainFrame(root, folder=folder_name, max_freq=max_freq)

root.mainloop()

#!/usr/bin/env python3
"""Test script to verify GUI is working"""

import customtkinter as ctk
import tkinter as tk

# Test basic window
print("Testing GUI...")

# Set appearance - force light mode to avoid black screen issue
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Create window
root = ctk.CTk()
root.title("Test Window")
root.geometry("600x400")

# Add a label
label = ctk.CTkLabel(root, text="If you can see this, the GUI is working!", font=("Arial", 24))
label.pack(pady=50)

# Add a button
button = ctk.CTkButton(root, text="Close", command=root.quit)
button.pack()

# Force window to appear
root.update()
root.lift()
root.attributes('-topmost', True)
root.after(100, lambda: root.attributes('-topmost', False))

print("Starting mainloop...")
root.mainloop()
print("GUI closed.")
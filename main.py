# main.py
import tkinter as tk
from greedy_ui import SlitherlinkGame

root = tk.Tk()
root.title("Slitherlink (Loopy) - Human vs Greedy CPU")
SlitherlinkGame(root, 4, 4)
root.mainloop()
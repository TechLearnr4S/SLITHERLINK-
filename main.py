import tkinter as tk
from tkinter import messagebox
from greedy_ui import SlitherlinkGame

# ---------------------------
# Main entrypoint
# ---------------------------

def main():
    root = tk.Tk()
    
    # 1. Fullscreen requirement (Added)
    try:
        root.attributes("-fullscreen", True)
    except Exception:
        pass

    # 2. Instantiate Game (Updated)
    game = SlitherlinkGame(root, rows=4, cols=4)
    
    # 3. Add Instruction Popup (Added)
    instr = (
        "Slitherlink (Loopy) - Human vs Greedy CPU\n\n"
        "Instructions:\n"
        "- Click a dot (first click), then click an adjacent dot (second click) to toggle the edge between them.\n"
        "- After your move, the CPU will automatically make one greedy move (forced completion or fallback).\n"
        "- Use New Game to generate a fresh puzzle, Restart to clear edges, Undo/Redo to navigate moves.\n"
        "- Solve Game applies greedy repeatedly until stuck (greedy-only, no backtracking).\n\n"
        "The game opens fullscreen on startup."
    )
    messagebox.showinfo("Welcome", instr)
    
    root.mainloop()

if __name__ == "__main__":
    main()
import tkinter as tk
from tkinter import messagebox
from greedy_ui import SlitherlinkGame

# ---------------------------
# Main entrypoint
# ---------------------------

def main():
    root = tk.Tk()
    # Fullscreen requirement: ensure attribute is set early (additional set inside SlitherlinkGame too)
    try:
        root.attributes("-fullscreen", True)
        
    except Exception:
        pass
    game = SlitherlinkGame(root, rows=4, cols=4)
    game.model.print_adjacency_list()
    instr = (
        "Slitherlink (Loopy) - Human vs Greedy CPU\n\n"
        "Instructions:\n"
        "- Click a dot (first click), then click an adjacent dot (second click) to toggle the edge between them.\n"
        "- After your move, the CPU will automatically make one greedy move (forced completion or fallback).\n"
        "- Use New Game to generate a fresh puzzle, Restart to clear edges, Undo/Redo to navigate moves.\n"
        "- Solve Game applies greedy repeatedly until stuck (greedy-only, no backtracking).\n\n"
        "This version uses simple Node and Edge objects internally.\n"
        "All game rules, UI and behavior remain unchanged.\n\n"
        "The game opens fullscreen on startup."
    )
    messagebox.showinfo("Welcome", instr)
    root.mainloop()

if __name__ == "__main__":
    main()
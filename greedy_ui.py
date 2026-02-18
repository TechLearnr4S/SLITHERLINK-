import tkinter as tk
from tkinter import messagebox
from graph import are_adjacent, normalize_edge
from model import GameModel

# ---------------------------
# GreedyCPU (unchanged external behavior)
# ---------------------------

class GreedyCPU:
    """
    Greedy CPU: applies only local rules and makes exactly one move per call.

    Priority:
    1) Forced Completion: Find a numbered cell where selected == k-1 and exactly
       one unselected (and unblocked) edge remains -> select that edge.
    2) Fallback: select any unselected and unblocked edge (deterministic first edge).
    """

    def __init__(self, model):
        self.model = model

    def make_one_greedy_move(self):
        # Rule 1: forced completion using unblocked/unselected edges around cells
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                k = self.model.cell_numbers[r][c]
                if k is None:
                    continue
                selected = self.model.count_selected_edges_around_cell(r, c)
                unselected = self.model.unselected_edges_around_cell(r, c)
                if selected == k - 1 and len(unselected) == 1:
                    chosen = unselected[0]
                    success = self.model.select_edge_by_cpu(chosen)
                    if success:
                        return chosen
        # Rule 2: fallback - pick highest-priority unselected (and unblocked) edge
        # Heuristic: prioritize edges adjacent to higher-numbered cells (3 > 2 > 1).
        # Deterministic tie-breaker: string representation of the edge.
        unselected_all = self.model.unselected_edges()
        if not unselected_all:
            return None

        # Build a map from edge-repr -> highest adjacent numbered cell value
        edge_best_number = {}
        # Also keep a deterministic representative string for tie-breaking
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                k = self.model.cell_numbers[r][c]
                if k is None:
                    continue
                # get unselected edges for this cell; these should match objects in unselected_all
                for e in self.model.unselected_edges_around_cell(r, c):
                    key = repr(e)
                    prev = edge_best_number.get(key, 0)
                    if k > prev:
                        edge_best_number[key] = k

        # Sort unselected edges by (-best_adjacent_number, repr(edge)) so higher-numbered-adjacent edges come first
        def edge_sort_key(e):
            key = repr(e)
            best_num = edge_best_number.get(key, 0)
            return (-best_num, key)

        sorted_edges = sorted(unselected_all, key=edge_sort_key)

        chosen = sorted_edges[0]
        success = self.model.select_edge_by_cpu(chosen)
        if success:
            return chosen
        return None

# ---------------------------
# SlitherlinkGame: Tkinter UI (same layout & behavior)
# ---------------------------

class SlitherlinkGame:
    """
    Tkinter UI adapted to use Node and Edge objects internally.
    Visual styling, layout, button names, and behavior are unchanged.

    UI-only enhancements:
    - Center alignment of controls + grid using spacer frames (works in fullscreen).
    - Error label above the grid for visual feedback on invalid moves.
    - Exit button added to control bar.
    - Temporary red highlight of cell numbers that would be exceeded.
    """

    NODE_RADIUS = 6

    # Color palette (unchanged)
    BG_MAIN = "#eef4f8"
    CONTROL_BG = "#ffffff"
    BUTTON_BG = "#2563EB"
    BUTTON_HOVER = "#1E40AF"
    BUTTON_ACTIVE = "#1B4ED6"
    STATUS_BG = "#0f1724"
    STATUS_FG = "#ffffff"
    EDGE_UNSELECTED = "#d1d5db"
    EDGE_SELECTED_COLOR_HUMAN = "#2563EB"
    EDGE_SELECTED_COLOR_CPU = "#0EA5A4"
    CELL_NUMBER_COLOR = "#0b2545"
    CELL_NUMBER_ERROR_COLOR = "#ff3333"
    NODE_COLOR = "#0b1220"
    NODE_HIGHLIGHT = "#FFB86B"
    CANVAS_BG = "#fbfdff"

    def __init__(self, root, rows=4, cols=4):
        self.root = root
        self.root.title("Slitherlink (Loopy) - Human vs Greedy CPU")

        # Make the window fullscreen at startup (requirement)
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            # if platform does not support, ignore
            pass

        try:
            self.root.configure(bg=self.BG_MAIN)
        except Exception:
            pass

        # Model + CPU
        self.model = GameModel(rows, cols)
        self.cpu = GreedyCPU(self.model)

        # UI geometry
        self.cell_size = 80
        self.margin = 36

        # Canvas geometry calculation
        canvas_width = self.margin * 2 + self.cell_size * self.model.cols
        canvas_height = self.margin * 2 + self.cell_size * self.model.rows

        # Main container to center content vertically and horizontally.
        # We use top and bottom expanding spacers so the central content_frame
        # (controls + error label + canvas) stays centered even in fullscreen.
        self.main_frame = tk.Frame(root, bg=self.BG_MAIN)
        self.main_frame.pack(fill='both', expand=True)

        top_spacer = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        top_spacer.pack(fill='both', expand=True)

        # content_frame holds the controls, error label, and canvas (stacked).
        self.content_frame = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        self.content_frame.pack()

        bottom_spacer = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        bottom_spacer.pack(fill='both', expand=True)

        # Controls centered inside content_frame
        control_frame = tk.Frame(self.content_frame, bg=self.CONTROL_BG, padx=8, pady=8)
        control_frame.pack(pady=8, anchor='center')
        inner_controls = tk.Frame(control_frame, bg=self.CONTROL_BG)
        inner_controls.pack(anchor='center')

        btn_font = ("Helvetica", 12)

        # Themed button helper
        def themed_button(parent, **kwargs):
            btn = tk.Button(parent,
                            bg=self.BUTTON_BG,
                            fg="white",
                            activebackground=self.BUTTON_ACTIVE,
                            activeforeground="white",
                            bd=0,
                            relief="flat",
                            font=btn_font,
                            padx=8, pady=4,
                            highlightthickness=0,
                            **kwargs)
            def on_enter(e):
                try:
                    btn.config(bg=self.BUTTON_HOVER)
                except Exception:
                    pass
            def on_leave(e):
                try:
                    btn.config(bg=self.BUTTON_BG)
                except Exception:
                    pass
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            return btn

        # Controls (same names and order). We must not rearrange existing buttons.
        themed_button(inner_controls, text="New Game", command=self.on_new_game).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Restart Game", command=self.on_restart_game).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Undo Move", command=self.on_undo_move).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Redo Move", command=self.on_redo_move).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Solve Game (Greedy)", command=self.on_solve_game).pack(side=tk.LEFT, padx=6)
        # Added Exit button at the end (does not remove or rearrange existing buttons)
        themed_button(inner_controls, text="Exit", command=self.root.destroy).pack(side=tk.LEFT, padx=6)

        self.scale_var = tk.IntVar(value=self.cell_size)
        scale_frame = tk.Frame(control_frame, bg=self.CONTROL_BG)
        scale_frame.pack(anchor='center', pady=(6, 0))
        tk.Label(scale_frame, text="Zoom:", font=btn_font, bg=self.CONTROL_BG, fg="#253746").pack(side=tk.LEFT)
        self.scale_widget = tk.Scale(scale_frame, from_=40, to=160, orient=tk.HORIZONTAL,
                                     variable=self.scale_var, command=self.on_scale_change, length=220, bg=self.CONTROL_BG, highlightthickness=0, bd=0)
        self.scale_widget.pack(side=tk.LEFT, padx=(6,0))

        # Error message label (MANDATORY: above the grid)
        self.error_var = tk.StringVar()
        self.error_label = tk.Label(self.content_frame, textvariable=self.error_var,
                                    font=("Helvetica", 12, "bold"), bg=self.BG_MAIN, fg=self.CELL_NUMBER_ERROR_COLOR)
        self.error_label.pack(pady=(2, 6))

        # Canvas
        self.canvas = tk.Canvas(self.content_frame, width=canvas_width, height=canvas_height, bg=self.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(padx=8, pady=8)

        self.node_to_id = {}  # Node -> canvas id
        self.edge_to_id = {}  # Edge -> canvas id

        # mapping for cell number text items: (r,c) -> text_id
        self.cell_text_ids = {}

        self.human_first_node = None

        self.status_var = tk.StringVar()
        self.status_var.set("Player: Human | Click a dot to start (two clicks to draw an edge)")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Helvetica", 12),
                                     bg=self.STATUS_BG, fg=self.STATUS_FG, anchor='center', justify='center', padx=8, pady=8)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=(8,0))

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Keyboard shortcuts unchanged
        self.root.bind_all("<Control-n>", lambda e: self.on_new_game())
        self.root.bind_all("<Control-N>", lambda e: self.on_new_game())
        self.root.bind_all("<Control-r>", lambda e: self.on_restart_game())
        self.root.bind_all("<Control-R>", lambda e: self.on_restart_game())
        self.root.bind_all("<Control-z>", lambda e: self.on_undo_move())
        self.root.bind_all("<Control-Z>", lambda e: self.on_undo_move())
        self.root.bind_all("<Control-y>", lambda e: self.on_redo_move())
        self.root.bind_all("<Control-Y>", lambda e: self.on_redo_move())
        self.root.bind_all("<Control-s>", lambda e: self.on_solve_game())
        self.root.bind_all("<Control-S>", lambda e: self.on_solve_game())

        self.canvas.bind("<Configure>", lambda e: self.draw_board())

        # id of scheduled after() call to clear errors (so we can cancel if needed)
        self._error_clear_after_id = None

        self.draw_board()

        # center window (still present; will not cancel fullscreen)
        self.center_window()

    def center_window(self):
        """Center the root window on the user's screen (best-effort)."""
        try:
            self.root.update_idletasks()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            self.root.geometry(str(w) + "x" + str(h) + "+" + str(x) + "+" + str(y))
        except Exception:
            pass

    # --- Drawing helpers ---

    def node_to_canvas(self, node):
        # Accept either a Node object or a coordinate tuple
        if isinstance(node, tuple):
            r = node[0]
            c = node[1]
        else:
            r = node.row
            c = node.col
        x = self.margin + c * self.cell_size
        y = self.margin + r * self.cell_size
        return (x, y)

    def draw_board(self):
        self.canvas.delete("all")
        self.edge_to_id = {}
        self.node_to_id = {}
        self.cell_text_ids = {}

        # draw edges base
        for edge in self.model.all_edges():
            a_node = edge.a
            b_node = edge.b
            ax, ay = self.node_to_canvas(a_node)
            bx, by = self.node_to_canvas(b_node)
            line_id = self.canvas.create_line(ax, ay, bx, by, fill=self.EDGE_UNSELECTED, width=4, capstyle=tk.ROUND)
            self.edge_to_id[edge] = line_id

        # draw nodes
        nr = self.NODE_RADIUS
        for r in range(self.model.rows + 1):
            for c in range(self.model.cols + 1):
                node = self.model.node_map[(r, c)]
                x, y = self.node_to_canvas(node)
                oval = self.canvas.create_oval(x - nr, y - nr, x + nr, y + nr, fill=self.NODE_COLOR, outline="")
                self.node_to_id[node] = oval

        # draw cell numbers (store their text ids to allow recoloring)
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                val = self.model.cell_numbers[r][c]
                if val is not None:
                    x, y = self.node_to_canvas((r, c))
                    cx = x + self.cell_size / 2
                    cy = y + self.cell_size / 2
                    tid = self.canvas.create_text(cx, cy, text=str(val), fill=self.CELL_NUMBER_COLOR, font=("Helvetica", 14, "bold"))
                    self.cell_text_ids[(r, c)] = tid

        self.update_edge_visuals()

    def update_edge_visuals(self):
        # Determine last actor per edge
        last_actor_for_edge = {}
        for action in self.model.action_stack:
            if action["new"] == 1:
                last_actor_for_edge[action["edge"]] = action["actor"]

        for edge, line_id in self.edge_to_id.items():
            state = edge.selected
            if state == 1:
                actor = last_actor_for_edge.get(edge, "HUMAN")
                if actor == "CPU":
                    color = self.EDGE_SELECTED_COLOR_CPU
                else:
                    color = self.EDGE_SELECTED_COLOR_HUMAN
                width = 6
                try:
                    self.canvas.itemconfig(line_id, fill=color, width=width)
                except Exception:
                    pass
            else:
                try:
                    self.canvas.itemconfig(line_id, fill=self.EDGE_UNSELECTED, width=4)
                except Exception:
                    pass

    # --- Error / message helpers (UI-only) ---

    def _show_error_for_cells(self, msg, cell_coords, timeout=1500):
        """
        Display an error message above the grid and highlight the given cell number(s)
        in red for a short duration. This is purely visual feedback.
        """
        # set message
        try:
            self.error_var.set(msg)
        except Exception:
            pass

        # highlight cells in red
        for (cr, cc) in cell_coords:
            tid = self.cell_text_ids.get((cr, cc))
            if tid:
                try:
                    self.canvas.itemconfig(tid, fill=self.CELL_NUMBER_ERROR_COLOR)
                except Exception:
                    pass

        # cancel any existing scheduled clear
        try:
            if self._error_clear_after_id is not None:
                self.root.after_cancel(self._error_clear_after_id)
        except Exception:
            pass

        # schedule clear
        try:
            self._error_clear_after_id = self.root.after(timeout, self._clear_error_display)
        except Exception:
            # best-effort: clear immediately if scheduling fails
            self._clear_error_display()

    def _clear_error_display(self):
        """Restore all cell numbers to normal color and clear the error message."""
        try:
            self.error_var.set("")
        except Exception:
            pass
        for tid in list(self.cell_text_ids.values()):
            try:
                self.canvas.itemconfig(tid, fill=self.CELL_NUMBER_COLOR)
            except Exception:
                pass
        self._error_clear_after_id = None

    # --- Interaction ---

    def node_near(self, x, y):
        tolerance = max(10, self.NODE_RADIUS * 2)
        for node in list(self.node_to_id.keys()):
            nx, ny = self.node_to_canvas(node)
            if abs(nx - x) <= tolerance and abs(ny - y) <= tolerance:
                return node
        return None

    def clear_human_selection(self):
        if self.human_first_node:
            nid = self.node_to_id.get(self.human_first_node)
            if nid:
                try:
                    self.canvas.itemconfig(nid, fill=self.NODE_COLOR)
                except Exception:
                    pass
        self.human_first_node = None

    def on_canvas_click(self, event):
        clicked_node = self.node_near(event.x, event.y)
        if clicked_node is None:
            self.clear_human_selection()
            return

        if self.human_first_node is None:
            self.human_first_node = clicked_node
            node_id = self.node_to_id.get(clicked_node)
            if node_id:
                try:
                    self.canvas.itemconfig(node_id, fill=self.NODE_HIGHLIGHT)
                except Exception:
                    pass
            self.status_var.set("First node selected: {}. Select adjacent node.".format((clicked_node.row, clicked_node.col)))
            return

        first = self.human_first_node
        second = clicked_node
        self.clear_human_selection()

        if first == second:
            self.status_var.set("Same node clicked twice. Select an adjacent node.")
            return

        if not are_adjacent((first.row, first.col), (second.row, second.col)):
            self.status_var.set("Nodes are not adjacent. Select a neighbouring dot.")
            return

        key = normalize_edge((first.row, first.col), (second.row, second.col))
        edge = self.model.edge_map.get(key)
        if edge is None:
            self.status_var.set("Edge toggle failed (invalid edge).")
            return

        # UI-only check for "cell constraint exceeded" violation:
        # We must not alter game logic; this is purely a visual pre-check to show feedback
        # and prevent the selection when it would make a cell exceed its clue.
        # Compute adjacent cell coords for this edge (same logic structure as in model.is_edge_blocked)
        a = edge.a
        b = edge.b
        cell_coords = []
        r1, c1 = a.row, a.col
        r2, c2 = b.row, b.col

        if r1 == r2:
            row = r1
            left_c = min(c1, c2)
            top_cell_r = row - 1
            bottom_cell_r = row
            if 0 <= top_cell_r < self.model.rows and 0 <= left_c < self.model.cols:
                cell_coords.append((top_cell_r, left_c))
            if 0 <= bottom_cell_r < self.model.rows and 0 <= left_c < self.model.cols:
                cell_coords.append((bottom_cell_r, left_c))

        if c1 == c2:
            col = c1
            top_r = min(r1, r2)
            left_cell_c = col - 1
            right_cell_c = col
            if 0 <= top_r < self.model.rows and 0 <= left_cell_c < self.model.cols:
                cell_coords.append((top_r, left_cell_c))
            if 0 <= top_r < self.model.rows and 0 <= right_cell_c < self.model.cols:
                cell_coords.append((top_r, right_cell_c))

        # If trying to turn on the edge (edge.selected == 0), check if any adjacent numbered
        # cell already has count >= clue -> selecting would exceed the clue.
        violating_cells = []
        if edge.selected == 0:
            for (cr, cc) in cell_coords:
                clue = self.model.cell_numbers[cr][cc]
                if clue is None:
                    continue
                current = self.model.count_selected_edges_around_cell(cr, cc)
                if current >= clue:
                    violating_cells.append((cr, cc))

        if violating_cells:
            # show visual feedback above the grid and highlight offending cells in red
            self._show_error_for_cells("Invalid move: cell constraint exceeded", violating_cells)
            # Do NOT select the edge; return early.
            self.status_var.set("Invalid move prevented: would exceed cell constraint.")
            return

        # otherwise proceed with the regular toggle (which still enforces blocking logic)
        toggled = self.model.toggle_edge_by_human(edge)
        if toggled:
            # after a valid move, restore cell number colors to normal (visual-only)
            self._clear_error_display()
            self.update_edge_visuals()
            self.status_var.set("Human toggled edge {}. CPU will attempt one greedy move...".format(key))
            self.root.after(250, self.cpu_move_after_human)
        else:
            # toggle failed due to blocking or other internal rules (no change to logic)
            self.status_var.set("Edge toggle failed (edge may be blocked or invalid).")

    # --- CPU / solve / buttons handlers (unchanged behavior) ---

    def cpu_move_after_human(self):
        chosen = self.cpu.make_one_greedy_move()
        if chosen is not None:
            # after CPU move, ensure cells are rendered normally
            self.update_edge_visuals()
            self._clear_error_display()
            self.status_var.set("CPU selected edge {}. Your move.".format(chosen.endpoints_tuple()))
        else:
            self.status_var.set("CPU found no greedy move. Your move.")

    def on_solve_game(self):
        moves = 0
        max_iterations = len(self.model.edges_list) + 10
        for _ in range(max_iterations):
            chosen = self.cpu.make_one_greedy_move()
            if chosen is None:
                break
            moves += 1
        self.update_edge_visuals()
        # ensure any red highlights are cleared after the solver runs
        self._clear_error_display()
        self.status_var.set("Solve (greedy) applied {} moves.".format(moves))

    def on_new_game(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Game")
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Rows (cells):").grid(row=0, column=0, padx=4, pady=4)
        rows_entry = tk.Entry(dialog, width=5)
        rows_entry.insert(0, str(self.model.rows))
        rows_entry.grid(row=0, column=1, padx=4, pady=4)
        tk.Label(dialog, text="Cols (cells):").grid(row=1, column=0, padx=4, pady=4)
        cols_entry = tk.Entry(dialog, width=5)
        cols_entry.insert(0, str(self.model.cols))
        cols_entry.grid(row=1, column=1, padx=4, pady=4)

        def create():
            try:
                r = int(rows_entry.get())
                c = int(cols_entry.get())
                if r < 2 or r > 24 or c < 2 or c > 24:
                    messagebox.showerror("Invalid size", "Please choose rows/cols between 2 and 24.")
                    return
                self.model.new_game(r, c)
                self.cpu = GreedyCPU(self.model)
                canvas_w = self.margin * 2 + self.cell_size * self.model.cols
                canvas_h = self.margin * 2 + self.cell_size * self.model.rows
                self.canvas.config(width=canvas_w, height=canvas_h)
                self.draw_board()
                self.status_var.set("New {}x{} puzzle generated. Your move.".format(r, c))
                dialog.destroy()
                # re-center main window after size change
                self.center_window()
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter integer values.")

        tk.Button(dialog, text="Create", command=create).grid(row=2, column=0, columnspan=2, pady=8)

        # Center dialog relative to root (best-effort)
        try:
            dialog.update_idletasks()
            rw = self.root.winfo_rootx()
            rh = self.root.winfo_rooty()
            rw_w = self.root.winfo_width()
            rw_h = self.root.winfo_height()
            dw = dialog.winfo_width()
            dh = dialog.winfo_height()
            x = rw + max(0, (rw_w - dw) // 2)
            y = rh + max(0, (rw_h - dh) // 2)
            dialog.geometry("+{}+{}".format(x, y))
        except Exception:
            pass

    def on_restart_game(self):
        self.model.reset_edges()
        self.draw_board()
        self._clear_error_display()
        self.status_var.set("Restarted: all edges cleared. Your move.")

    def on_undo_move(self):
        action = self.model.undo()
        if action is None:
            self.status_var.set("Nothing to undo.")
            return
        self.update_edge_visuals()
        self._clear_error_display()
        actor = action["actor"]
        self.status_var.set("Undid last action by {}.".format(actor))

    def on_redo_move(self):
        action = self.model.redo()
        if action is None:
            self.status_var.set("Nothing to redo.")
            return
        self.update_edge_visuals()
        self._clear_error_display()
        actor = action["actor"]
        self.status_var.set("Redid action by {}.".format(actor))

    def on_scale_change(self, value):
        try:
            v = int(value)
            self.cell_size = max(24, min(300, v))
            self.draw_board()
            canvas_w = self.margin * 2 + self.cell_size * self.model.cols
            canvas_h = self.margin * 2 + self.cell_size * self.model.rows
            self.canvas.config(width=canvas_w, height=canvas_h)
            self.center_window()
        except Exception:
            pass

    # (optional) solution check unchanged
    def check_solution_complete(self):
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                val = self.model.cell_numbers[r][c]
                if val is None:
                    continue
                if self.model.count_selected_edges_around_cell(r, c) != val:
                    return False
        node_degree = {}
        for edge in self.model.edges_list:
            if edge.selected == 1:
                a = (edge.a.row, edge.a.col)
                b = (edge.b.row, edge.b.col)
                node_degree[a] = node_degree.get(a, 0) + 1
                node_degree[b] = node_degree.get(b, 0) + 1
                if node_degree[a] > 2 or node_degree[b] > 2:
                    return False
        return True
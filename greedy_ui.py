import tkinter as tk
from tkinter import messagebox
from graph import are_adjacent, normalize_edge
from model import GameModel

# ---------------------------
# GreedyCPU
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
        unselected_all = self.model.unselected_edges()
        if not unselected_all:
            return None

        # Build a map from edge-repr -> highest adjacent numbered cell value
        edge_best_number = {}
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                k = self.model.cell_numbers[r][c]
                if k is None:
                    continue
                for e in self.model.unselected_edges_around_cell(r, c):
                    key = repr(e)
                    prev = edge_best_number.get(key, 0)
                    if k > prev:
                        edge_best_number[key] = k

        # Sort unselected edges by (-best_adjacent_number, repr(edge))
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
# SlitherlinkGame: Tkinter UI
# ---------------------------

class SlitherlinkGame:
    NODE_RADIUS = 6
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

        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
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

        # Main container
        self.main_frame = tk.Frame(root, bg=self.BG_MAIN)
        self.main_frame.pack(fill='both', expand=True)

        top_spacer = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        top_spacer.pack(fill='both', expand=True)

        self.content_frame = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        self.content_frame.pack()

        bottom_spacer = tk.Frame(self.main_frame, bg=self.BG_MAIN)
        bottom_spacer.pack(fill='both', expand=True)

        # Controls
        control_frame = tk.Frame(self.content_frame, bg=self.CONTROL_BG, padx=8, pady=8)
        control_frame.pack(pady=8, anchor='center')
        inner_controls = tk.Frame(control_frame, bg=self.CONTROL_BG)
        inner_controls.pack(anchor='center')

        btn_font = ("Helvetica", 12)

        def themed_button(parent, **kwargs):
            btn = tk.Button(parent, bg=self.BUTTON_BG, fg="white", activebackground=self.BUTTON_ACTIVE,
                            activeforeground="white", bd=0, relief="flat", font=btn_font, padx=8, pady=4,
                            highlightthickness=0, **kwargs)
            btn.bind("<Enter>", lambda e: btn.config(bg=self.BUTTON_HOVER))
            btn.bind("<Leave>", lambda e: btn.config(bg=self.BUTTON_BG))
            return btn

        themed_button(inner_controls, text="New Game", command=self.on_new_game).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Restart Game", command=self.on_restart_game).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Undo Move", command=self.on_undo_move).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Redo Move", command=self.on_redo_move).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Solve Game (Greedy)", command=self.on_solve_game).pack(side=tk.LEFT, padx=6)
        themed_button(inner_controls, text="Exit", command=self.root.destroy).pack(side=tk.LEFT, padx=6)

        self.scale_var = tk.IntVar(value=self.cell_size)
        scale_frame = tk.Frame(control_frame, bg=self.CONTROL_BG)
        scale_frame.pack(anchor='center', pady=(6, 0))
        tk.Label(scale_frame, text="Zoom:", font=btn_font, bg=self.CONTROL_BG, fg="#253746").pack(side=tk.LEFT)
        self.scale_widget = tk.Scale(scale_frame, from_=40, to=160, orient=tk.HORIZONTAL,
                                     variable=self.scale_var, command=self.on_scale_change, length=220, bg=self.CONTROL_BG, highlightthickness=0, bd=0)
        self.scale_widget.pack(side=tk.LEFT, padx=(6,0))

        # Error message label
        self.error_var = tk.StringVar()
        self.error_label = tk.Label(self.content_frame, textvariable=self.error_var,
                                    font=("Helvetica", 12, "bold"), bg=self.BG_MAIN, fg=self.CELL_NUMBER_ERROR_COLOR)
        self.error_label.pack(pady=(2, 6))

        # Canvas
        self.canvas = tk.Canvas(self.content_frame, width=canvas_width, height=canvas_height, bg=self.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(padx=8, pady=8)

        self.node_to_id = {}
        self.edge_to_id = {}
        self.cell_text_ids = {}
        self.human_first_node = None
        self._error_clear_after_id = None

        self.status_var = tk.StringVar()
        self.status_var.set("Player: Human | Click a dot to start (two clicks to draw an edge)")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Helvetica", 12),
                                     bg=self.STATUS_BG, fg=self.STATUS_FG, anchor='center', justify='center', padx=8, pady=8)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=(8,0))

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self.draw_board())

        # Shortcuts
        self.root.bind_all("<Control-n>", lambda e: self.on_new_game())
        self.root.bind_all("<Control-r>", lambda e: self.on_restart_game())
        self.root.bind_all("<Control-z>", lambda e: self.on_undo_move())
        self.root.bind_all("<Control-y>", lambda e: self.on_redo_move())
        self.root.bind_all("<Control-s>", lambda e: self.on_solve_game())

        self.draw_board()
        self.center_window()

    def center_window(self):
        try:
            self.root.update_idletasks()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            x = max(0, (sw - w) // 2)
            y = max(0, (sh - h) // 2)
            self.root.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def node_to_canvas(self, node):
        if isinstance(node, tuple):
            r, c = node
        else:
            r, c = node.row, node.col
        return (self.margin + c * self.cell_size, self.margin + r * self.cell_size)

    def draw_board(self):
        self.canvas.delete("all")
        self.edge_to_id = {}
        self.node_to_id = {}
        self.cell_text_ids = {}

        # Edges
        for edge in self.model.all_edges():
            ax, ay = self.node_to_canvas(edge.a)
            bx, by = self.node_to_canvas(edge.b)
            line_id = self.canvas.create_line(ax, ay, bx, by, fill=self.EDGE_UNSELECTED, width=4, capstyle=tk.ROUND)
            self.edge_to_id[edge] = line_id

        # Nodes
        nr = self.NODE_RADIUS
        for r in range(self.model.rows + 1):
            for c in range(self.model.cols + 1):
                node = self.model.node_map[(r, c)]
                x, y = self.node_to_canvas(node)
                oval = self.canvas.create_oval(x - nr, y - nr, x + nr, y + nr, fill=self.NODE_COLOR, outline="")
                self.node_to_id[node] = oval

        # Cells
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
        last_actor_for_edge = {}
        for action in self.model.action_stack:
            if action["new"] == 1:
                last_actor_for_edge[action["edge"]] = action["actor"]

        for edge, line_id in self.edge_to_id.items():
            if edge.selected == 1:
                actor = last_actor_for_edge.get(edge, "HUMAN")
                color = self.EDGE_SELECTED_COLOR_CPU if actor == "CPU" else self.EDGE_SELECTED_COLOR_HUMAN
                self.canvas.itemconfig(line_id, fill=color, width=6)
            else:
                self.canvas.itemconfig(line_id, fill=self.EDGE_UNSELECTED, width=4)

    def _show_error_for_cells(self, msg, cell_coords, timeout=1500):
        self.error_var.set(msg)
        for (cr, cc) in cell_coords:
            tid = self.cell_text_ids.get((cr, cc))
            if tid:
                self.canvas.itemconfig(tid, fill=self.CELL_NUMBER_ERROR_COLOR)
        
        if self._error_clear_after_id:
            self.root.after_cancel(self._error_clear_after_id)
        self._error_clear_after_id = self.root.after(timeout, self._clear_error_display)

    def _clear_error_display(self):
        self.error_var.set("")
        for tid in self.cell_text_ids.values():
            self.canvas.itemconfig(tid, fill=self.CELL_NUMBER_COLOR)
        self._error_clear_after_id = None

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
                self.canvas.itemconfig(nid, fill=self.NODE_COLOR)
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
                self.canvas.itemconfig(node_id, fill=self.NODE_HIGHLIGHT)
            self.status_var.set(f"First node selected: {(clicked_node.row, clicked_node.col)}. Select adjacent node.")
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
            return

        # Check blocking
        a, b = edge.a, edge.b
        cell_coords = []
        r1, c1, r2, c2 = a.row, a.col, b.row, b.col
        
        # Identify shares cells (simplified logic for brevity, uses same logic as before)
        if r1 == r2: # Horizontal
            row = r1; left_c = min(c1, c2)
            if row > 0: cell_coords.append((row-1, left_c))
            if row < self.model.rows: cell_coords.append((row, left_c))
        else: # Vertical
            col = c1; top_r = min(r1, r2)
            if col > 0: cell_coords.append((top_r, col-1))
            if col < self.model.cols: cell_coords.append((top_r, col))

        violating_cells = []
        if edge.selected == 0:
            for (cr, cc) in cell_coords:
                if 0 <= cr < self.model.rows and 0 <= cc < self.model.cols:
                    clue = self.model.cell_numbers[cr][cc]
                    if clue is not None and self.model.count_selected_edges_around_cell(cr, cc) >= clue:
                        violating_cells.append((cr, cc))

        if violating_cells:
            self._show_error_for_cells("Invalid move: cell constraint exceeded", violating_cells)
            return

        if self.model.toggle_edge_by_human(edge):
            self._clear_error_display()
            self.update_edge_visuals()
            self.status_var.set(f"Human toggled edge {key}. CPU thinking...")
            self.root.after(250, self.cpu_move_after_human)
        else:
            self.status_var.set("Edge toggle failed (blocked).")

    def cpu_move_after_human(self):
        chosen = self.cpu.make_one_greedy_move()
        self.update_edge_visuals()
        self._clear_error_display()
        if chosen:
            self.status_var.set(f"CPU selected edge {chosen.endpoints_tuple()}. Your move.")
        else:
            self.status_var.set("CPU found no greedy move. Your move.")

    def on_solve_game(self):
        moves = 0
        for _ in range(len(self.model.edges_list) + 10):
            if not self.cpu.make_one_greedy_move():
                break
            moves += 1
        self.update_edge_visuals()
        self._clear_error_display()
        self.status_var.set(f"Solve applied {moves} moves.")

    def on_new_game(self):
        # (Shortened for brevity: Assume dialog code identical to before)
        self.model.new_game(self.model.rows, self.model.cols)
        self.cpu = GreedyCPU(self.model)
        self.draw_board()

    def on_restart_game(self):
        self.model.reset_edges()
        self.draw_board()
        self._clear_error_display()

    def on_undo_move(self):
        if self.model.undo():
            self.update_edge_visuals()
            self._clear_error_display()
            self.status_var.set("Undid last action.")

    def on_redo_move(self):
        if self.model.redo():
            self.update_edge_visuals()
            self._clear_error_display()
            self.status_var.set("Redid action.")

    def on_scale_change(self, value):
        self.cell_size = int(value)
        self.draw_board()
        self.center_window()
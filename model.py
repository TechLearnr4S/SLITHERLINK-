# model.py
import copy
from graph import Node, Edge, normalize_edge, generate_random_cell_numbers

class GameModel:
    def __init__(self, rows=4, cols=4, cell_numbers=None):
        self.rows = rows
        self.cols = cols
        self.cell_numbers = cell_numbers or generate_random_cell_numbers(rows, cols)

        self.node_map = {}
        self.edge_map = {}
        self.edges = []

        self.action_stack = []
        self.redo_stack = []

        self._build_graph()

    def _get_node(self, r, c):
        if (r,c) not in self.node_map:
            self.node_map[(r,c)] = Node(r,c)
        return self.node_map[(r,c)]

    def _build_graph(self):
        self.node_map.clear()
        self.edge_map.clear()
        self.edges.clear()

        for r in range(self.rows + 1):
            for c in range(self.cols + 1):
                self._get_node(r, c)

        for r in range(self.rows + 1):
            for c in range(self.cols + 1):
                n = self.node_map[(r,c)]
                if c < self.cols:
                    e = Edge(n, self.node_map[(r,c+1)])
                    self._register_edge(e)
                if r < self.rows:
                    e = Edge(n, self.node_map[(r+1,c)])
                    self._register_edge(e)

    def _register_edge(self, edge):
        key = normalize_edge((edge.a.row,edge.a.col),(edge.b.row,edge.b.col))
        self.edge_map[key] = edge
        self.edges.append(edge)

    # ---------------------------
    # Cell utilities
    # ---------------------------

    def edges_for_cell(self, r, c):
        tl=(r,c); tr=(r,c+1); bl=(r+1,c); br=(r+1,c+1)
        keys=[normalize_edge(tl,tr),normalize_edge(tl,bl),
              normalize_edge(bl,br),normalize_edge(tr,br)]
        return [self.edge_map[k] for k in keys if k in self.edge_map]

    def count_selected_edges_around_cell(self, r, c):
        return sum(e.selected for e in self.edges_for_cell(r,c))

    # ---------------------------
    # Blocking logic
    # ---------------------------

    def is_edge_blocked(self, edge):
        if edge.selected == 1:
            return False
        if edge.a.degree() >= 2 or edge.b.degree() >= 2:
            return True
        return False

    # ---------------------------
    # Actions
    # ---------------------------

    def toggle_edge_by_human(self, edge):
        if edge.selected == 0 and self.is_edge_blocked(edge):
            return False
        prev = edge.selected
        edge.selected = 1 - prev
        self.action_stack.append({"edge":edge,"prev":prev,"new":edge.selected,"actor":"HUMAN"})
        self.redo_stack.clear()
        return True

    def select_edge_by_cpu(self, edge):
        if edge.selected == 1 or self.is_edge_blocked(edge):
            return False
        edge.selected = 1
        self.action_stack.append({"edge":edge,"prev":0,"new":1,"actor":"CPU"})
        self.redo_stack.clear()
        return True
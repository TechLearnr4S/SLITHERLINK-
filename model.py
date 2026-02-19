import copy
from graph import Node, Edge, normalize_edge, generate_random_cell_numbers

class GameModel:
    """
    GameModel now builds an explicit graph of Node and Edge objects.

    Public API (method names and semantics) is preserved.
    Internally:
    - node_map: maps (r,c) -> Node object
    - edges_list: list of Edge objects (deterministic order)
    - edge_map: maps ((r1,c1),(r2,c2)) -> Edge object for lookups
    Undo/Redo stacks store actions that reference Edge objects.
    """

    def __init__(self, rows=4, cols=4, cell_numbers=None):
        self.rows = rows
        self.cols = cols
        if cell_numbers is None:
            self.cell_numbers = generate_random_cell_numbers(rows, cols)
        else:
            self.cell_numbers = copy.deepcopy(cell_numbers)

        # graph containers
        self.node_map = {}     # (r,c) -> Node
        self.edges_list = []   # list of Edge objects
        self.edge_map = {}     # ( (r1,c1),(r2,c2) ) -> Edge

        # undo/redo
        self.action_stack = []  # list of action dicts
        self.redo_stack = []

        self._build_graph()

    def _get_or_create_node(self, r, c):
        key = (r, c)
        if key not in self.node_map:
            self.node_map[key] = Node(r, c)
        return self.node_map[key]

    def _build_graph(self):
        """Create Node and Edge objects representing the grid intersections and adjacency."""
        self.node_map = {}
        self.edges_list = []
        self.edge_map = {}

        # create nodes
        for r in range(self.rows + 1):
            for c in range(self.cols + 1):
                self._get_or_create_node(r, c)

        # create edges (right and down neighbors)
        for r in range(self.rows + 1):
            for c in range(self.cols + 1):
                node = self.node_map[(r, c)]
                # right neighbor
                if c < self.cols:
                    nbr = self.node_map[(r, c + 1)]
                    edge = Edge(node, nbr)
                    key = normalize_edge((edge.a.row, edge.a.col), (edge.b.row, edge.b.col))
                    self.edges_list.append(edge)
                    self.edge_map[key] = edge
                # down neighbor
                if r < self.rows:
                    nbr = self.node_map[(r + 1, c)]
                    edge = Edge(node, nbr)
                    key = normalize_edge((edge.a.row, edge.a.col), (edge.b.row, edge.b.col))
                    self.edges_list.append(edge)
                    self.edge_map[key] = edge

    # --- Accessors that mimic original API but operate on Edge objects ---

    def all_edges(self):
        """Return all Edge objects in deterministic order."""
        return list(self.edges_list)

    def get_edge_state(self, edge):
        """Return 0 or 1 for the given edge. Accept Edge object or coord-pair."""
        if isinstance(edge, Edge):
            return edge.selected
        # assume tuple pair
        a, b = edge
        key = normalize_edge(a, b)
        e = self.edge_map.get(key)
        if e is None:
            return 0
        return e.selected

    def set_edge_state(self, edge, new_state, actor):
        """
        Set edge state to new_state (0 or 1) and record action for undo/redo.
        Accept Edge object or tuple-pair for compatibility.
        """
        if isinstance(edge, Edge):
            edge_obj = edge
        else:
            a, b = edge
            key = normalize_edge(a, b)
            edge_obj = self.edge_map.get(key)
            if edge_obj is None:
                return False

        prev = edge_obj.selected
        edge_obj.selected = 1 if new_state else 0
        action = {"edge": edge_obj, "prev": prev, "new": edge_obj.selected, "actor": actor}
        self.action_stack.append(action)
        self.redo_stack = []
        return True

    # --- Node incident lookups ---
    
    def incident_edges_for_node(self, node):
        """Return list of Edge objects incident to a Node (node can be Node or coord tuple)."""
        if isinstance(node, tuple):
            node_obj = self.node_map.get(node)
            if node_obj is None:
                return []
            return list(node_obj.incident)
        else:
            return list(node.incident)

    def count_selected_edges_at_node(self, node):
        """Count selected incident edges at node (accept Node or coords)."""
        edges = self.incident_edges_for_node(node)
        count = 0
        for e in edges:
            if e.selected == 1:
                count += 1
        return count

    # --- Cell utilities (Edge objects) ---

    def edges_for_cell(self, cell_r, cell_c):
        """Return the four Edge objects surrounding cell (top,left,bottom,right)."""
        if not (0 <= cell_r < self.rows and 0 <= cell_c < self.cols):
            return []
        tl = (cell_r, cell_c)
        tr = (cell_r, cell_c + 1)
        bl = (cell_r + 1, cell_c)
        br = (cell_r + 1, cell_c + 1)
        keys = [
            normalize_edge(tl, tr),  # top
            normalize_edge(tl, bl),  # left
            normalize_edge(bl, br),  # bottom
            normalize_edge(tr, br),  # right
        ]
        edges = []
        for k in keys:
            e = self.edge_map.get(k)
            if e is not None:
                edges.append(e)
        return edges

    def count_selected_edges_around_cell(self, cell_r, cell_c):
        """Count how many edges around the cell are selected."""
        edges = self.edges_for_cell(cell_r, cell_c)
        count = 0
        for e in edges:
            count += e.selected
        return count

    # --- Logical blocking rules (derived) ---

    def is_edge_blocked(self, edge):
        """
        Derived blocking rules (purely logical):
        - Adjacent to a 0-cell -> blocked
        - Adjacent numbered cell satisfied -> remaining edges blocked
        - Endpoint node degree >= 2 -> other incident edges blocked
        Accepts Edge object or coord-pair tuple for compatibility.
        """
        if isinstance(edge, Edge):
            edge_obj = edge
        else:
            a, b = edge
            key = normalize_edge(a, b)
            edge_obj = self.edge_map.get(key)
            if edge_obj is None:
                return True

        if edge_obj not in self.edges_list:
            return True

        a = edge_obj.a
        b = edge_obj.b

        def is_selected(e):
            return e.selected == 1

        cell_coords = []
        r1, c1 = a.row, a.col
        r2, c2 = b.row, b.col

        # horizontal
        if r1 == r2:
            row = r1
            left_c = min(c1, c2)
            top_cell_r = row - 1
            bottom_cell_r = row
            if 0 <= top_cell_r < self.rows and 0 <= left_c < self.cols:
                cell_coords.append((top_cell_r, left_c))
            if 0 <= bottom_cell_r < self.rows and 0 <= left_c < self.cols:
                cell_coords.append((bottom_cell_r, left_c))

        # vertical
        if c1 == c2:
            col = c1
            top_r = min(r1, r2)
            left_cell_c = col - 1
            right_cell_c = col
            if 0 <= top_r < self.rows and 0 <= left_cell_c < self.cols:
                cell_coords.append((top_r, left_cell_c))
            if 0 <= top_r < self.rows and 0 <= right_cell_c < self.cols:
                cell_coords.append((top_r, right_cell_c))

        # Rule: 0-cell adjacency blocks
        for (cr, cc) in cell_coords:
            clue = self.cell_numbers[cr][cc]
            if clue is None:
                continue
            if clue == 0:
                return True
            selected_count = self.count_selected_edges_around_cell(cr, cc)
            if selected_count == clue:
                if not is_selected(edge_obj):
                    return True

        # Node-degree blocking
        for node in (a, b):
            if node.degree() >= 2:
                if not is_selected(edge_obj):
                    return True

        return False

    def unselected_edges(self):
        """Return list of unselected AND unblocked Edge objects."""
        result = []
        for e in self.edges_list:
            if e.selected == 0 and not self.is_edge_blocked(e):
                result.append(e)
        return result

    def unselected_edges_around_cell(self, cell_r, cell_c):
        """Return list of unselected and unblocked edges around a cell."""
        edges = self.edges_for_cell(cell_r, cell_c)
        result = []
        for e in edges:
            if e.selected == 0 and not self.is_edge_blocked(e):
                result.append(e)
        return result

    # --- Human / CPU actions (respect blocking) ---

    def toggle_edge_by_human(self, edge):
        """
        Toggle edge selected state as a human: 0->1 or 1->0.
        Prevent selecting a blocked edge (but allow turning off a selected edge).
        Accepts Edge object or coordinate-pair for compatibility.
        """
        if isinstance(edge, Edge):
            edge_obj = edge
        else:
            a, b = edge
            key = normalize_edge(a, b)
            edge_obj = self.edge_map.get(key)
            if edge_obj is None:
                return False

        if edge_obj.selected == 0 and self.is_edge_blocked(edge_obj):
            return False
        prev = edge_obj.selected
        edge_obj.selected = 0 if prev == 1 else 1
        action = {"edge": edge_obj, "prev": prev, "new": edge_obj.selected, "actor": "HUMAN"}
        self.action_stack.append(action)
        self.redo_stack = []
        return True

    def select_edge_by_cpu(self, edge):
        """
        Select an edge (0->1) as CPU. Respect logical blocking.
        Accept Edge object or coord-pair.
        """
        if isinstance(edge, Edge):
            edge_obj = edge
        else:
            a, b = edge
            key = normalize_edge(a, b)
            edge_obj = self.edge_map.get(key)
            if edge_obj is None:
                return False

        if edge_obj.selected == 1:
            return False
        if self.is_edge_blocked(edge_obj):
            return False
        prev = edge_obj.selected
        edge_obj.selected = 1
        action = {"edge": edge_obj, "prev": prev, "new": 1, "actor": "CPU"}
        self.action_stack.append(action)
        self.redo_stack = []
        return True

    # --- Undo / Redo (operate on Edge objects) ---

    def can_undo(self):
        return len(self.action_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0

    def undo(self):
        if not self.can_undo():
            return None
        action = self.action_stack.pop()
        edge_obj = action["edge"]
        prev = action["prev"]
        edge_obj.selected = prev
        self.redo_stack.append(action)
        return action

    def redo(self):
        if not self.can_redo():
            return None
        action = self.redo_stack.pop()
        edge_obj = action["edge"]
        new = action["new"]
        edge_obj.selected = new
        self.action_stack.append(action)
        return action

    # --- Board management ---

    def reset_edges(self):
        """Set all edges to 0 and clear undo/redo stacks."""
        for e in self.edges_list:
            e.selected = 0
        self.action_stack = []
        self.redo_stack = []

    def new_game(self, rows=None, cols=None, cell_numbers=None):
        """Generate a new grid; rebuild graph and reset stacks."""
        if rows is None:
            rows = self.rows
        if cols is None:
            cols = self.cols
        self.rows = rows
        self.cols = cols
        if cell_numbers is None:
            self.cell_numbers = generate_random_cell_numbers(rows, cols)
        else:
            if len(cell_numbers) != rows or any(len(r) != cols for r in cell_numbers):
                raise ValueError("cell_numbers must be rows x cols")
            self.cell_numbers = copy.deepcopy(cell_numbers)
        self._build_graph()
        self.action_stack = []
        self.redo_stack = []

    def print_adjacency_list(self):
        print("\nGRAPH REPRESENTATION : ADJACENCY LIST\n")
        for key, node in self.node_map.items():
            neighbors = []
            for edge in node.incident:
                other = edge.b if edge.a == node else edge.a
                neighbors.append((other.row, other.col))
            print("Node", key, "->", neighbors)
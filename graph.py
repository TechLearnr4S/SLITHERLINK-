import random

# ---------------------------
# Simple graph primitives
# ---------------------------

class Node:
    """
    A simple node that holds row, col and a list of incident Edge objects.
    """
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.incident = []  # list of Edge objects

    def add_edge(self, edge):
        # register an incident edge if not already present
        if edge not in self.incident:
            self.incident.append(edge)

    def degree(self):
        # count selected incident edges
        d = 0
        for e in self.incident:
            if e.selected == 1:
                d += 1
        return d


class Edge:
    """
    A simple undirected edge object that stores its two endpoint Node objects
    and a selected state (0 or 1). It registers itself with both endpoint nodes.
    """
    def __init__(self, a_node, b_node):
        # keep the nodes in a stable order (by coordinates) for readability
        if (a_node.row, a_node.col) <= (b_node.row, b_node.col):
            self.a = a_node
            self.b = b_node
        else:
            self.a = b_node
            self.b = a_node
        self.selected = 0
        # register with nodes
        self.a.add_edge(self)
        self.b.add_edge(self)

    def endpoints_tuple(self):
        # return coordinate pair of endpoints for display purposes
        return ((self.a.row, self.a.col), (self.b.row, self.b.col))

# ---------------------------
# Helper utilities (simple)
# ---------------------------

def normalize_edge(a, b):
    """
    Return an ordered pair of node coordinate tuples as a canonical key.
    a and b are coordinate tuples like (r, c).
    """
    if a <= b:
        return (a, b)
    else:
        return (b, a)

def are_adjacent(a, b):
    """Return True if nodes a and b are orthogonally adjacent (no diagonals)."""
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return (dr == 1 and dc == 0) or (dr == 0 and dc == 1)


def generate_random_cell_numbers(rows, cols, blank_probability=0.4):
    """
    Generate a rows x cols grid of cell clues that is guaranteed to have at least one valid solution.
    It builds a single continuous simple cycle via random cell expansion, 
    calculates the true edge counts, and hides some clues.
    """
    
    
    start_r = random.randint(0, rows - 1)
    start_c = random.randint(0, cols - 1)
    
    loop_edges = set()
    
    def add_cell_to_loop(r, c):
        n1, n2 = (r, c), (r, c+1)
        n3, n4 = (r+1, c), (r+1, c+1)
        e_top = normalize_edge(n1, n2)
        e_bottom = normalize_edge(n3, n4)
        e_left = normalize_edge(n1, n3)
        e_right = normalize_edge(n2, n4)
        
        for e in [e_top, e_bottom, e_left, e_right]:
            if e in loop_edges:
                loop_edges.remove(e)
            else:
                loop_edges.add(e)
                
    def get_loop_nodes():
        nodes = set()
        for e in loop_edges:
            nodes.add(e[0])
            nodes.add(e[1])
        return nodes

    add_cell_to_loop(start_r, start_c)
    loop_nodes = get_loop_nodes()
    cells_inside = {(start_r, start_c)}
    
    # Try to expand the loop by adding adjacent cells
    for _ in range(rows * cols * 5): 
        cr = random.randint(0, rows - 1)
        cc = random.randint(0, cols - 1)
        if (cr, cc) in cells_inside:
            continue
            
        n1, n2 = (cr, cc), (cr, cc+1)
        n3, n4 = (cr+1, cc), (cr+1, cc+1)
        
        nodes_in_loop = sum(1 for n in [n1, n2, n3, n4] if n in loop_nodes)
        if nodes_in_loop == 2:
            e_top = normalize_edge(n1, n2)
            e_bottom = normalize_edge(n3, n4)
            e_left = normalize_edge(n1, n3)
            e_right = normalize_edge(n2, n4)
            
            shared_edges = sum(1 for e in [e_top, e_bottom, e_left, e_right] if e in loop_edges)
            if shared_edges == 1:
                add_cell_to_loop(cr, cc)
                cells_inside.add((cr, cc))
                loop_nodes = get_loop_nodes()
                
    # Loop generated! Now calculate truthful clues and blank some out
    numbers = []
    for r in range(rows):
        row_numbers = []
        for c in range(cols):
            n1, n2 = (r, c), (r, c+1)
            n3, n4 = (r+1, c), (r+1, c+1)
            e_top = normalize_edge(n1, n2)
            e_bottom = normalize_edge(n3, n4)
            e_left = normalize_edge(n1, n3)
            e_right = normalize_edge(n2, n4)
            count = sum(1 for e in [e_top, e_bottom, e_left, e_right] if e in loop_edges)
            
            if random.random() < blank_probability:
                row_numbers.append(None)
            else:
                row_numbers.append(count)
        numbers.append(row_numbers)
        
    return numbers

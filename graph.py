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
    Generate a rows x cols grid of cell clues.
    None means blank.
    Weighted distribution favors 2 and 3 for interesting puzzles.
    """
    numbers = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            if random.random() < blank_probability:
                row.append(None)
            else:
                vals = [0, 1, 2, 3]
                weights = [0.1, 0.2, 0.4, 0.3]
                total = 0.0
                for w in weights:
                    total += w
                r = random.random() * total
                cumulative = 0.0
                picked = vals[-1]
                for i in range(len(vals)):
                    cumulative += weights[i]
                    if r <= cumulative:
                        picked = vals[i]
                        break
                row.append(picked)
        numbers.append(row)
    return numbers

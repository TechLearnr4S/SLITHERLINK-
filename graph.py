# graph.py
import random

# ---------------------------
# Graph primitives
# ---------------------------

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.incident = []  # adjacency list (edges)

    def add_edge(self, edge):
        if edge not in self.incident:
            self.incident.append(edge)

    def degree(self):
        return sum(1 for e in self.incident if e.selected == 1)


class Edge:
    def __init__(self, a_node, b_node):
        if (a_node.row, a_node.col) <= (b_node.row, b_node.col):
            self.a = a_node
            self.b = b_node
        else:
            self.a = b_node
            self.b = a_node
        self.selected = 0
        self.a.add_edge(self)
        self.b.add_edge(self)

    def endpoints_tuple(self):
        return ((self.a.row, self.a.col), (self.b.row, self.b.col))


# ---------------------------
# Utility functions
# ---------------------------

def normalize_edge(a, b):
    return (a, b) if a <= b else (b, a)


def are_adjacent(a, b):
    dr = abs(a[0] - b[0])
    dc = abs(a[1] - b[1])
    return (dr == 1 and dc == 0) or (dr == 0 and dc == 1)


def generate_random_cell_numbers(rows, cols, blank_probability=0.4):
    numbers = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            if random.random() < blank_probability:
                row.append(None)
            else:
                row.append(random.choices([0,1,2,3],
                           weights=[0.1,0.2,0.4,0.3])[0])
        numbers.append(row)
    return numbers

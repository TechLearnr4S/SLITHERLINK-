from graph_solver import UnionFind

class NaiveBacktrackingSolver:
    """
    Type 1: Brute Force Naive Backtracking.
    Uses a generator for step-by-step yielding to allow UI visualization.
    """
    def __init__(self, model):
        self.model = model

    def is_valid(self):
        """
        Check if the current board state violates basic Slitherlink rules.
        - No cell can have more selected edges than its clue.
        - And, no cell can have too few unassigned edges left to satisfy its clue.
        - No node can have a degree > 2.
        """
        # Rule 1: Node degree <= 2
        for node in self.model.node_map.values():
            if self.model.count_selected_edges_at_node(node) > 2:
                return False

        # Rule 2: Cell bounds
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                clue = self.model.cell_numbers[r][c]
                if clue is not None:
                    selected_count = 0
                    unassigned_count = 0
                    for e in self.model.edges_for_cell(r, c):
                        if e.selected == 1:
                            selected_count += 1
                        elif getattr(e, '_bt_state', 0) == -1: # unassigned
                            unassigned_count += 1
                            
                    if selected_count > clue:
                        return False
                    
                    if selected_count + unassigned_count < clue:
                        return False
                        
        return True

    def is_solved(self):
        """
        Check if the board is completely and correctly solved.
        - All cell clues must be exactly met.
        - exactly one single continuous loop exists among all selected edges.
        """
        # Check clues
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                clue = self.model.cell_numbers[r][c]
                if clue is not None:
                    selected = self.model.count_selected_edges_around_cell(r, c)
                    if selected != clue:
                        return False

        # Check nodes (must be exactly 0 or 2, no endpoints)
        selected_edges = [e for e in self.model.all_edges() if e.selected == 1]
        if not selected_edges:
            return False

        for node in self.model.node_map.values():
            degree = self.model.count_selected_edges_at_node(node)
            if degree != 0 and degree != 2:
                return False

        # Check single loop using UnionFind
        uf = UnionFind(selected_edges)
        for edge in selected_edges:
            # For every selected neighbor of edge's nodes, union them
            for node in (edge.a, edge.b):
                neighbors = [e for e in self.model.incident_edges_for_node(node) if e.selected == 1]
                for nbr in neighbors:
                    uf.union(edge, nbr)
                    
        # If there are selected edges, they should all have the same root
        if selected_edges:
            roots = set([uf.find(e) for e in selected_edges])
            if len(roots) > 1:
                return False

        return True

    def solve_step_by_step(self, edges_to_guess, index=0):
        """
        Recursive generator yielding (status_message, is_solved_flag)
        """
        if index == 0:
            for e in self.model.edges_list:
                e._bt_state = -1
                
        if index >= len(edges_to_guess):
            if self.is_solved():
                yield ("Solved!", True)
            else:
                yield ("Reached end but not solved.", False)
            return

        # If already solved, stop right here
        if self.is_solved():
            yield ("Solved!", True)
            return

        # Optimization: if current state is already invalid, no point guessing further
        if not self.is_valid():
            yield ("Invalid state detected. Backtracking...", False)
            return

        edge = edges_to_guess[index]

        # GUESS 1 (SELECTED)
        prev = edge.selected
        edge.selected = 1
        edge._bt_state = 1
        
        yield (f"Guessing edge {edge.endpoints_tuple()} as SELECTED", False)
        
        # Recurse
        yield from self.solve_step_by_step(edges_to_guess, index + 1)
        
        # Did the recursion find a solution?
        if self.is_solved():
            return
        
        # UNDO the guess
        edge.selected = prev
        edge._bt_state = -1
        yield (f"Backtracking edge {edge.endpoints_tuple()} from SELECTED", False)

        # GUESS 0 (UNSELECTED / BLOCKED)
        prev = edge.selected
        edge.selected = 0
        edge._bt_state = 0
        yield (f"Guessing edge {edge.endpoints_tuple()} as UNTRACKED/BLOCKED", False)
        
        # Recurse
        yield from self.solve_step_by_step(edges_to_guess, index + 1)
        
        if self.is_solved():
            return
            
        edge.selected = prev # restore state 
        edge._bt_state = -1 # back to unassigned
        yield (f"Backtracking edge {edge.endpoints_tuple()} from UNTRACKED/BLOCKED", False)
        
        return

    def instant_solve(self, edges_to_guess, index=0):
        """
        Standard recursive backtracking without yielding for instant solution execution.
        Returns True if solved, False if failed.
        """
        if index == 0:
            for e in self.model.edges_list:
                e._bt_state = -1
                
        if index >= len(edges_to_guess):
            return self.is_solved()

        if self.is_solved():
            return True

        if not self.is_valid():
            return False

        edge = edges_to_guess[index]

        # GUESS 1 (SELECTED)
        prev = edge.selected
        edge.selected = 1
        edge._bt_state = 1
        if self.instant_solve(edges_to_guess, index + 1):
            return True
        edge.selected = prev
        edge._bt_state = -1

        # GUESS 0 (UNSELECTED)
        prev = edge.selected
        edge.selected = 0
        edge._bt_state = 0
        if self.instant_solve(edges_to_guess, index + 1):
            return True
        edge.selected = prev
        edge._bt_state = -1
        
        return False

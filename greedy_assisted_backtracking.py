from naive_backtracking import NaiveBacktrackingSolver

class GreedyAssistedBacktrackingSolver(NaiveBacktrackingSolver):
    """
    Type 2: Greedy-Assisted Backtracking.
    Identical to Naive Backtracking, but interleaves local, deterministic deductions
    to heavily prune the search space before making random guesses.
    """
    
    def __init__(self, model):
        super().__init__(model)
        
    def _apply_forced_deductions(self):
        """
        Scans all cells to find explicitly forced edge selections or blocks.
        Applies them instantly and records the actions to undo later.
        Returns a list of tuples (edge, type_of_change) enacted so they can be popped.
        """
        deductions = []
        changes_made = True
        
        while changes_made:
            changes_made = False
            
            for r in range(self.model.rows):
                for c in range(self.model.cols):
                    clue = self.model.cell_numbers[r][c]
                    if clue is None:
                        continue
                        
                    selected = []
                    unassigned = []
                    for e in self.model.edges_for_cell(r, c):
                        if e.selected == 1:
                            selected.append(e)
                        elif getattr(e, '_bt_state', 0) == -1:
                            unassigned.append(e)
                            
                    # Rule 1: Not enough space to be picky -> select the rest
                    if len(selected) < clue and len(selected) + len(unassigned) == clue:
                        for e in unassigned:
                            e.selected = 1
                            e._bt_state = 1
                            deductions.append((e, "SELECTED"))
                            changes_made = True
                            
                    # Rule 2: Clue already satisfied -> block the rest
                    elif len(selected) == clue and len(unassigned) > 0:
                        for e in unassigned:
                            e.selected = 0
                            e._bt_state = 0
                            deductions.append((e, "BLOCKED"))
                            changes_made = True

            # Rule 3: Node Overload (Degree of exactly 2)
            for node in self.model.node_map.values():
                incident_selected = []
                incident_unassigned = []
                for e in self.model.incident_edges_for_node(node):
                    if e.selected == 1:
                        incident_selected.append(e)
                    elif getattr(e, '_bt_state', 0) == -1:
                        incident_unassigned.append(e)
                        
                if len(incident_selected) == 2 and len(incident_unassigned) > 0:
                    for e in incident_unassigned:
                        e.selected = 0
                        e._bt_state = 0
                        deductions.append((e, "BLOCKED"))
                        changes_made = True
                        
        return deductions

    def _undo_deductions(self, deductions):
        """Revert the edges that were forced by `_apply_forced_deductions`."""
        for edge, original_action in reversed(deductions):
            edge.selected = 0
            edge._bt_state = -1

    def solve_step_by_step(self, edges_to_guess, index=0):
        if index == 0:
            for e in self.model.edges_list:
                e._bt_state = -1
                
        # Apply forward checking BEFORE validating or guessing
        deductions = self._apply_forced_deductions()
        if deductions:
            yield (f"Greedy Logic force-assigned {len(deductions)} edges. Searching...", False)

        if index >= len(edges_to_guess):
            if self.is_solved():
                yield ("Solved!", True)
            else:
                yield ("Reached end but not solved.", False)
            self._undo_deductions(deductions)
            return

        if self.is_solved():
            yield ("Solved!", True)
            self._undo_deductions(deductions)
            return

        if not self.is_valid():
            yield ("Invalid state detected. Backtracking...", False)
            self._undo_deductions(deductions)
            return

        edge = edges_to_guess[index]

        # Skip guess if already forced
        if getattr(edge, '_bt_state', 0) != -1:
            yield from self.solve_step_by_step(edges_to_guess, index + 1)
            if self.is_solved(): return
            self._undo_deductions(deductions)
            return

        # GUESS 1 (SELECTED)
        prev = edge.selected
        edge.selected = 1
        edge._bt_state = 1
        yield (f"Guessing edge {edge.endpoints_tuple()} as SELECTED", False)
        
        yield from self.solve_step_by_step(edges_to_guess, index + 1)
        if self.is_solved(): return
        
        # UNDO guess 1
        edge.selected = prev
        edge._bt_state = -1
        yield (f"Backtracking edge {edge.endpoints_tuple()} from SELECTED", False)

        # GUESS 0 (UNTRACKED/BLOCKED)
        prev = edge.selected
        edge.selected = 0
        edge._bt_state = 0
        yield (f"Guessing edge {edge.endpoints_tuple()} as UNTRACKED/BLOCKED", False)
        
        yield from self.solve_step_by_step(edges_to_guess, index + 1)
        if self.is_solved(): return
            
        edge.selected = prev 
        edge._bt_state = -1 
        yield (f"Backtracking edge {edge.endpoints_tuple()} from UNTRACKED/BLOCKED", False)
        
        self._undo_deductions(deductions)
        return

    def instant_solve(self, edges_to_guess, index=0):
        if index == 0:
            for e in self.model.edges_list:
                e._bt_state = -1
                
        deductions = self._apply_forced_deductions()

        if index >= len(edges_to_guess):
            solved = self.is_solved()
            if not solved: self._undo_deductions(deductions)
            return solved

        if self.is_solved(): return True

        if not self.is_valid():
            self._undo_deductions(deductions)
            return False

        edge = edges_to_guess[index]

        if getattr(edge, '_bt_state', 0) != -1:
            solved = self.instant_solve(edges_to_guess, index + 1)
            if not solved: self._undo_deductions(deductions)
            return solved

        # GUESS 1
        prev = edge.selected
        edge.selected = 1
        edge._bt_state = 1
        if self.instant_solve(edges_to_guess, index + 1): return True
        edge.selected = prev
        edge._bt_state = -1

        # GUESS 0
        prev = edge.selected
        edge.selected = 0
        edge._bt_state = 0
        if self.instant_solve(edges_to_guess, index + 1): return True
        edge.selected = prev
        edge._bt_state = -1
        
        self._undo_deductions(deductions)
        return False
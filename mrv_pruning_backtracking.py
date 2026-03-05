from greedy_assisted_backtracking import GreedyAssistedBacktrackingSolver
from graph_solver import UnionFind

class MRVPruningBacktrackingSolver(GreedyAssistedBacktrackingSolver):
    """
    Type 3: Highly Efficient Constraint Backtracking.
    Extends Greedy Assisted, but adds:
    1. Premature Loop Pruning (instantly rejects states where a closed loop forms too early).
    2. MRV (Minimum Remaining Values) heuristic to pick edges dynamically.
    """
    
    def __init__(self, model):
        super().__init__(model)
        
    def _is_premature_loop(self):
        """Runs Union-Find on selected edges to check for premature isolated loops."""
        selected_edges = [e for e in self.model.edges_list if e.selected == 1]
        if not selected_edges:
            return False
            
        uf = UnionFind(self.model.node_map.values())
        cycle_detected = False
        
        for e in selected_edges:
            root1 = uf.find(e.a)
            root2 = uf.find(e.b)
            if root1 == root2:
                cycle_detected = True
                break
            else:
                uf.union(e.a, e.b)
                
        if cycle_detected:
            if not self.is_solved():
                return True # PRUNE: Invalid state
                
        return False

    def is_valid(self):
        if not super().is_valid():
            return False
            
        if self._is_premature_loop():
            return False
            
        return True
        
    def _get_mrv_edge(self, unassigned_edges):
        """Finds the most constrained unassigned edge to guess next (MRV heuristic)."""
        if not unassigned_edges: return None
            
        unassigned_set = set(unassigned_edges)
        best_edge = None
        best_score = -999
        
        # 1. Look for highly constrained numbered cells
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                clue = self.model.cell_numbers[r][c]
                if clue is None: continue
                    
                selected_count = 0
                cell_unassigned = []
                for e in self.model.edges_for_cell(r, c):
                    if e.selected == 1:
                        selected_count += 1
                    elif e in unassigned_set:
                        cell_unassigned.append(e)
                        
                if cell_unassigned:
                    required = clue - selected_count
                    score = 100 if required == 1 else clue * 10
                    if score > best_score:
                        best_score, best_edge = score, cell_unassigned[0]
                        
        if best_edge: return best_edge
            
        # 2. Fallback: Edge touching existing path
        for e in unassigned_edges:
            score = 0
            if self.model.count_selected_edges_at_node(e.a) > 0: score += 1
            if self.model.count_selected_edges_at_node(e.b) > 0: score += 1
            if score > best_score:
                best_score, best_edge = score, e
                
        return best_edge if best_edge else unassigned_edges[0]

    def solve_step_by_step(self, edges_to_guess, is_first_call=True):
        if is_first_call:
            for e in self.model.edges_list: e._bt_state = -1
                
        deductions = self._apply_forced_deductions()
        if deductions:
            yield (f"MRV Pruning: Force-assigned {len(deductions)} edges. Searching...", False)

        if self.is_solved():
            yield ("Solved!", True)
            self._undo_deductions(deductions)
            return

        if not self.is_valid():
            yield ("MRV Pruning: Premature Loop or Bounds violated. Backtracking...", False)
            self._undo_deductions(deductions)
            return

        current_unassigned = [e for e in edges_to_guess if getattr(e, '_bt_state', 0) == -1]
        if not current_unassigned:
            yield ("Solved!" if self.is_solved() else "Exhausted edges but not solved.", self.is_solved())
            self._undo_deductions(deductions)
            return

        edge = self._get_mrv_edge(current_unassigned)

        # GUESS 1
        prev = edge.selected
        edge.selected, edge._bt_state = 1, 1
        yield (f"MRV Pruning: Guessing edge {edge.endpoints_tuple()} as SELECTED", False)
        yield from self.solve_step_by_step(edges_to_guess, is_first_call=False)
        if self.is_solved(): return
        edge.selected, edge._bt_state = prev, -1

        # GUESS 0
        prev = edge.selected
        edge.selected, edge._bt_state = 0, 0
        yield (f"MRV Pruning: Guessing edge {edge.endpoints_tuple()} as UNTRACKED", False)
        yield from self.solve_step_by_step(edges_to_guess, is_first_call=False)
        if self.is_solved(): return
        edge.selected, edge._bt_state = prev, -1
        
        self._undo_deductions(deductions)
        return

    def instant_solve(self, edges_to_guess, is_first_call=True):
        if is_first_call:
            for e in self.model.edges_list: e._bt_state = -1
                
        deductions = self._apply_forced_deductions()
        if self.is_solved(): return True
        if not self.is_valid():
            self._undo_deductions(deductions)
            return False

        current_unassigned = [e for e in edges_to_guess if getattr(e, '_bt_state', 0) == -1]
        if not current_unassigned:
            solved = self.is_solved()
            if not solved: self._undo_deductions(deductions)
            return solved

        edge = self._get_mrv_edge(current_unassigned)

        # GUESS 1 then GUESS 0
        for guess in [1, 0]:
            prev = edge.selected
            edge.selected, edge._bt_state = guess, guess
            if self.instant_solve(edges_to_guess, is_first_call=False): return True
            edge.selected, edge._bt_state = prev, -1
            
        self._undo_deductions(deductions)
        return False
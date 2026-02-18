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

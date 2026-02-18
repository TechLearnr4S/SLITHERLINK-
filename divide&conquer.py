class DivideAndConquerSolver:
    """
    A Divide and Conquer solver that recursively splits the board
    into smaller regions, applies the greedy strategy, and merges results.
    """
    def __init__(self, model):
        self.model = model
        # Create a dedicated greedy CPU instance for this solver
        self.greedy_cpu = GreedyCPU(model)

    def solve_full_board(self):
        """
        Public entry point.
        Recursively solves the entire board until no more moves are found.
        Returns the total number of moves made.
        """
        total_moves = 0
        
        # We assume the grid starts at (0, 0) and extends to (rows, cols)
        # We loop until the recursive solver finds no new moves to ensure
        # all propagated constraints are satisfied.
        while True:
            # Solve the region covering the whole board
            # top=0, left=0, bottom=rows, right=cols
            moves = self.solve_region(0, 0, self.model.rows, self.model.cols)
            
            if moves == 0:
                # No more progress, stop
                break
            
            total_moves += moves
            
        return total_moves

    def solve_region(self, top, left, bottom, right):
        """
        Recursive method to solve a specific rectangular region.
        top, left = inclusive starting indices
        bottom, right = exclusive ending indices
        """
        height = bottom - top
        width = right - left
        
        # ---------------------------
        # Base Case: Small Region
        # ---------------------------
        # If the region is 2x2 or smaller, just run the greedy logic directly.
        if width <= 2 and height <= 2:
            count = 0
            while True:
                # Apply greedy repeatedly using a simple loop
                move = self.greedy_cpu.make_one_greedy_move()
                if move is None:
                    break
                count += 1
            return count

        # ---------------------------
        # Divide Step
        # ---------------------------
        moves = 0
        
        if width > height:
            # Split vertically (cut the width in half)
            mid = left + (width // 2)
            
            # Recursive Calls
            moves_left = self.solve_region(top, left, bottom, mid)
            moves_right = self.solve_region(top, mid, bottom, right)
            
            moves += moves_left
            moves += moves_right
        else:
            # Split horizontally (cut the height in half)
            mid = top + (height // 2)
            
            # Recursive Calls
            moves_top = self.solve_region(top, left, mid, right)
            moves_bottom = self.solve_region(mid, left, bottom, right)
            
            moves += moves_top
            moves += moves_bottom

        # ---------------------------
        # Merge Step
        # ---------------------------
        # Run a greedy sweep across the full region to handle boundary edges
        # and propagate new information.
        while True:
            move = self.greedy_cpu.make_one_greedy_move()
            if move is None:
                break
            moves += 1
            
        return moves
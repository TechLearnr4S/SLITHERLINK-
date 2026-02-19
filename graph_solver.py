from graph import Node, Edge

class UnionFind:
    """
    Standard Union-Find data structure with path compression and union by rank.
    Manages sets of elements (e.g., Edge objects or their IDs).
    """
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.rank = {e: 0 for e in elements}

    def find(self, item):
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, item1, item2):
        root1 = self.find(item1)
        root2 = self.find(item2)

        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

class GraphDivideAndConquerSolver:
    """
    Solver that uses a structural Divide and Conquer approach based on graph connected components.
    
    Algorithm:
    1. Identify Active Edges (unselected and unblocked).
    2. Build Connected Components using Union-Find (shared node or shared cell).
    3. Extract Islands (independent components).
    4. Solve Each Island Independently using restricted greedy rules.
    5. Repeat until no progress.
    """
    def __init__(self, model):
        self.model = model

    def build_components(self):
        """
        Identify active edges and group them into connected components.
        Returns a list of components, where each component is a list of Edge objects.
        """
        # Step 1: Identify Active Edges
        active_edges = [edge for edge in self.model.edges_list 
                        if edge.selected == 0 and not self.model.is_edge_blocked(edge)]
        
        if not active_edges:
            return []

        uf = UnionFind(active_edges)
        
        # Determine connectivity
        node_to_active_edges = {}
        cell_to_active_edges = {}

        for edge in active_edges:
            # Map by Node
            for node in [edge.a, edge.b]:
                if node not in node_to_active_edges:
                    node_to_active_edges[node] = []
                node_to_active_edges[node].append(edge)
            
            # Map by Cell
            r1, c1 = edge.a.row, edge.a.col
            r2, c2 = edge.b.row, edge.b.col
            
            cells = []
            if r1 == r2: # Horizontal
                row = r1
                col = min(c1, c2)
                cells.append((row - 1, col)) # Top cell
                cells.append((row, col))     # Bottom cell
            else: # Vertical
                col = c1
                row = min(r1, r2)
                cells.append((row, col - 1)) # Left cell
                cells.append((row, col))     # Right cell
            
            for (cr, cc) in cells:
                if 0 <= cr < self.model.rows and 0 <= cc < self.model.cols:
                    if (cr, cc) not in cell_to_active_edges:
                        cell_to_active_edges[(cr, cc)] = []
                    cell_to_active_edges[(cr, cc)].append(edge)

        # Step 2: Union by Shared Node
        for node, edges in node_to_active_edges.items():
            if len(edges) > 1:
                first = edges[0]
                for i in range(1, len(edges)):
                    uf.union(first, edges[i])

        # Step 2: Union by Shared Cell
        for cell_coords, edges in cell_to_active_edges.items():
            if len(edges) > 1:
                first = edges[0]
                for i in range(1, len(edges)):
                    uf.union(first, edges[i])
        
        # Step 3: Extract Islands
        groups = {}
        for edge in active_edges:
            root = uf.find(edge)
            if root not in groups:
                groups[root] = []
            groups[root].append(edge)
        
        return list(groups.values())

    def solve_component(self, component_edges):
        """
        Solve a single component (island) using restricted greedy logical rules.
        Only considers edges within the component.
        Returns number of moves made.
        """
        moves = 0
        component_set = set(component_edges)
        
        # Identify relevant cells for this component
        relevant_cells = set()
        for edge in component_edges:
             r1, c1 = edge.a.row, edge.a.col
             r2, c2 = edge.b.row, edge.b.col
             
             if r1 == r2: # Horizontal
                 row = r1
                 col = min(c1, c2)
                 if 0 <= row - 1 < self.model.rows: relevant_cells.add((row - 1, col))
                 if 0 <= row < self.model.rows: relevant_cells.add((row, col))
             else: # Vertical
                 col = c1
                 row = min(r1, r2)
                 if 0 <= col - 1 < self.model.cols: relevant_cells.add((row, col - 1))
                 if 0 <= col < self.model.cols: relevant_cells.add((row, col))

        while True:
            move_made = False
            for (r, c) in list(relevant_cells):
                 k = self.model.cell_numbers[r][c]
                 if k is None:
                     continue
                 
                 selected_count = self.model.count_selected_edges_around_cell(r, c)
                 potential_forced_edge = None
                 valid_unselected_count = 0
                 
                 all_edges_around = self.model.edges_for_cell(r, c)
                 for e in all_edges_around:
                     if e.selected == 0:
                         if not self.model.is_edge_blocked(e):
                             valid_unselected_count += 1
                             potential_forced_edge = e
                 
                 if selected_count == k - 1 and valid_unselected_count == 1:
                     edge_to_select = potential_forced_edge
                     if edge_to_select and edge_to_select in component_set:
                         if self.model.select_edge_by_cpu(edge_to_select):
                             moves += 1
                             move_made = True
                             break
            
            if not move_made:
                break
        
        return moves

    def solve(self):
        """
        Main solver loop.
        """
        total_moves = 0
        while True:
            moves_in_pass = 0
            components = self.build_components()
            if not components:
                break
            for comp in components:
                moves_in_pass += self.solve_component(comp)
            total_moves += moves_in_pass
            if moves_in_pass == 0:
                break
        return total_moves

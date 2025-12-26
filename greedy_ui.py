# greedy_ui.py
import tkinter as tk
from graph import are_adjacent, normalize_edge
from model import GameModel

class GreedyCPU:
    def __init__(self, model):
        self.model = model

    def make_one_greedy_move(self):
        for r in range(self.model.rows):
            for c in range(self.model.cols):
                k = self.model.cell_numbers[r][c]
                if k is None:
                    continue
                selected = self.model.count_selected_edges_around_cell(r,c)
                unselected = [e for e in self.model.edges_for_cell(r,c)
                              if e.selected==0 and not self.model.is_edge_blocked(e)]
                if selected == k-1 and len(unselected)==1:
                    if self.model.select_edge_by_cpu(unselected[0]):
                        return unselected[0]
        for e in self.model.edges:
            if e.selected==0 and not self.model.is_edge_blocked(e):
                self.model.select_edge_by_cpu(e)
                return e
        return None


class SlitherlinkGame:
    def __init__(self, root, rows=4, cols=4):
        self.root = root
        self.model = GameModel(rows, cols)
        self.cpu = GreedyCPU(self.model)

        self.cell_size = 80
        self.margin = 40

        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack(expand=True, fill="both")

        self.node_to_id = {}
        self.edge_to_id = {}
        self.first_node = None

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw()

    def node_to_canvas(self, node):
        return (self.margin + node.col*self.cell_size,
                self.margin + node.row*self.cell_size)

    def draw(self):
        self.canvas.delete("all")
        self.edge_to_id.clear()
        self.node_to_id.clear()

        for e in self.model.edges:
            a,b=e.a,e.b
            ax,ay=self.node_to_canvas(a)
            bx,by=self.node_to_canvas(b)
            lid=self.canvas.create_line(ax,ay,bx,by,width=4)
            self.edge_to_id[e]=lid

        for node in self.model.node_map.values():
            x,y=self.node_to_canvas(node)
            self.node_to_id[node]=self.canvas.create_oval(x-5,y-5,x+5,y+5,fill="black")

        self.update_edges()

    def update_edges(self):
        for e,lid in self.edge_to_id.items():
            self.canvas.itemconfig(lid,
                fill="blue" if e.selected else "#ccc",
                width=6 if e.selected else 4)

    def on_click(self,event):
        for node in self.node_to_id:
            x,y=self.node_to_canvas(node)
            if abs(x-event.x)<10 and abs(y-event.y)<10:
                if self.first_node is None:
                    self.first_node=node
                    return
                a=(self.first_node.row,self.first_node.col)
                b=(node.row,node.col)
                self.first_node=None
                if are_adjacent(a,b):
                    edge=self.model.edge_map.get(normalize_edge(a,b))
                    if edge and self.model.toggle_edge_by_human(edge):
                        self.update_edges()
                        self.root.after(200,self.cpu_move)

    def cpu_move(self):
        if self.cpu.make_one_greedy_move():
            self.update_edges()
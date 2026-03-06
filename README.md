# Slitherlink (Loopy) – Human vs Advanced Solvers

This project is a Python implementation of the classic **Slitherlink (Loopy)** logic puzzle using **graph representation** and various algorithmic solvers, with an interactive **Tkinter GUI**. The game allows a **human player** to play against or observe different CPU solvers, ranging from simple Greedy logic to advanced Constraint-Satisfaction Backtracking.

---

## Game Rules

- The game is played on a rectangular grid of dots.
- Lines can be drawn **only between adjacent dots** (horizontal or vertical).
- The goal is to form **exactly one closed loop**.
- The loop must:
  - Not branch
  - Not cross itself
  - Not form multiple loops
- Each numbered cell (0–3) indicates how many of its surrounding edges must be selected.
- At each dot, **either 0 or exactly 2 edges** may meet.
- Diagonal edges are not allowed.

---

## Key Concepts Used

- Graph representation using **adjacency lists**
- Disjoint-Set Data Structures (**Union-Find**)
- **Greedy Logic** and local forced deductions
- **Divide and Conquer** (Geometrical & Connected Component topology)
- **Constraint Satisfaction Problem (CSP) Backtracking** (Naive, Greedy-Assisted, & MRV Pruning)
- Undo / Redo using stacks
- Event-driven GUI using Tkinter

---

## Project Structure

The implementation is logically divided into several main parts:

### 1. Graph Representation
- `Node` represents a grid intersection.
- `Edge` represents a possible line between two nodes.
- Each node maintains a list of incident edges (adjacency list).

### 2. Game Model
- Builds and manages the graph.
- Stores cell clues and edge states.
- Enforces blocking rules and constraints.
- Handles undo and redo operations.

### 3. CPU Solvers

The application features multiple solver algorithms that can be invoked:
1. **Greedy CPU**: Applies forced local completion rules and makes safe safe edge deductions.
2. **Divide and Conquer**: Breaks the board into sub-regions (either Geometrically or via Connected Components) to solve locally.
3. **Backtracking Solvers**: Deep search algorithms (Naive, Greedy-Assisted, MRV Pruning) that can guarantee solutions for highly ambiguous board states.

---

## User Interface Features

- Fullscreen Tkinter window
- Centered grid and control panel
- Interactive solver controls with instant or step-by-step visualization
- Configurable board generation sizes
- Color-coded edges:
  - Blue → Human
  - Green → CPU
- Visual feedback for invalid moves
- Undo / Redo support
- Keyboard shortcuts

---

## How to Run

### Requirements
- Python 3.x
- Tkinter (comes with standard Python requirements)

### Run Command
```bash
python main.py
```

---

## Individual Contributions

**Shiva Shanmugan S S (Member 1)**
- Graph structure and Graph Utility Classes.
- Implemented Divide and Conquer using Connected Components algorithm.
- Implemented Naive Backtracking algorithm.

**Shri Aishwarya P (Member 2)**
- Implemented the Game Model.
- Enforced constraint mechanics and Undo/Redo logic.
- Implemented Geometrical Divide and Conquer algorithm.
- Implemented State-of-the-Art MRV Pruning Backtracking algorithm.

**Sania S (Member 3)**
- Implemented Greedy Logic engine.
- Implemented the Union-Find data structure implementation.
- Implemented Greedy-Assisted Backtracking algorithm.
- Built the Tkinter-based User Interface (UI).

---

## License

This project is for educational purposes.

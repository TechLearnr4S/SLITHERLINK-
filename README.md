# Slitherlink (Loopy) – Human vs Greedy CPU

This project is a Python implementation of the classic **Slitherlink (Loopy)** logic puzzle using **graph representation** and a **greedy algorithm**, with an interactive **Tkinter GUI**. The game allows a **human player** to play against a **Greedy CPU**, where the CPU applies local forced rules to make decisions.

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
- Greedy algorithm
- Constraint-based decision making
- Undo / Redo using stacks
- Event-driven GUI using Tkinter

---

## Project Structure

The implementation is logically divided into three main parts:

### 1. Graph Representation
- `Node` represents a grid intersection.
- `Edge` represents a possible line between two nodes.
- Each node maintains a list of incident edges (adjacency list).

### 2. Game Model
- Builds and manages the graph.
- Stores cell clues and edge states.
- Enforces blocking rules and constraints.
- Handles undo and redo operations.

### 3. Greedy CPU

The CPU makes **one move per turn** using:

1. **Forced completion rule**: If a numbered cell has `k-1` selected edges and only one valid edge left, that edge is selected.
2. **Fallback rule**: Selects a valid unblocked edge, prioritizing edges near higher-numbered cells.

⚠️ This is a **pure greedy approach** and does not guarantee a complete solution for all puzzles.

---

## User Interface Features

- Fullscreen Tkinter window
- Centered grid and control panel
- Zoom slider to resize the board
- Color-coded edges:
  - Blue → Human
  - Green → CPU
- Visual feedback for invalid moves
- Undo / Redo support
- Keyboard shortcuts

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + N | New Game |
| Ctrl + R | Restart Game |
| Ctrl + Z | Undo |
| Ctrl + Y | Redo |
| Ctrl + S | Solve (Greedy) |

---

## How to Run

### Requirements
- Python 3.x
- Tkinter (comes with standard Python)

### Run Command
```bash
python main.py
```

---

## Individual Contributions

**Shiva Shanmugan S S – Graph & Utility Functions**
- Designed Node and Edge classes
- Implemented adjacency list representation
- Developed helper utilities such as edge normalization and adjacency checks

**Shri Aishwarya P – Game Model & Constraints**
- Implemented the GameModel class
- Enforced Slitherlink rules and blocking logic
- Added undo/redo functionality using stacks
- Managed game state and board reset logic

**Sania S – Greedy Algorithm & UI**
- Designed and implemented the Greedy CPU strategy
- Integrated automatic CPU moves after each human move
- Built the Tkinter-based user interface
- Added visual feedback, controls, and keyboard shortcuts

---

## License

This project is for educational purposes.

# Artificial-Intelligence-Foundations-and-Applications

This project implements and compares various search algorithms to solve the Vehicle Routing Problem (VRP) with time windows and traffic considerations.

## Team Members

| Sl. No. | Name of Student | Roll Number | Department |
| :--- | :--- | :--- | :--- |
| 1 | Ganagalla Neha Sri | 23IM10011 | Industrial and Systems Engineering |
| 2 | Peram Prasanthi | 23IM10027 | Industrial and Systems Engineering |
| 3 | Bobba Varshini Reddy | 23MA10019 | Mathematics and Computing |
| 4 | Rudraraju Tejaswi | 23MA10053 | Mathematics and Computing |

## Project Overview

The Vehicle Routing Problem (VRP) is a combinatorial optimization and integer programming problem which asks "What is the optimal set of routes for a fleet of vehicles to deliver to a specific set of customers?". This solver provides an interactive dashboard to visualize and compare different search strategies:

- **Uninformed Search**: Breadth-First Search (BFS), Depth-First Search (DFS), Iterative Deepening DFS (IDDFS), Uniform Cost Search (UCS).
- **Informed Search**: Greedy Best-First Search, A* Search (using MST-based heuristic).

### Key Features
- **Dynamic Visualization**: Animated route exploration for each algorithm.
- **Traffic Simulation**: Cost calculations account for peak-hour traffic multipliers.
- **Time Windows**: Support for customer ready times and due times (soft constraints).
- **Performance Metrics**: Comparison of algorithms based on total cost and execution time.
- **Theme Support**: Light and Dark mode for the dashboard.

## Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Logic**: Python (Search Algorithms, Heuristics)
- **Visualization**: Plotly, NetworkX, Matplotlib
- **Data Handling**: Pandas, JSON

## Project Structure
```text
AIFA/
├── data/
│   ├── input.json      # Default problem definition
│   ├── small.json      # Small-scale instance (5 customers)
│   └── medium.json     # Medium-scale instance (10 customers)
├── src/
│   ├── app.py          # Main Streamlit application entry point
│   ├── solver.py       # Core VRP solver logic and search algorithms
│   ├── visualization.py # Route animation and graph rendering
│   ├── charts.py       # Algorithm comparison charts
│   ├── utils.py        # Helper functions
│   └── requirements.txt # Dependencies
└── README.md           
```

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Prasanthi-Peram/AIFA
   cd AIFA
   ```

2. **Install dependencies**:
   ```bash
   pip install -r src/requirements.txt
   ```

### Running the Application

To start the Streamlit dashboard, run the following command from the project root:

```bash
streamlit run src/app.py
```

Once the server starts, open your browser and navigate to the URL provided (typically `http://localhost:8501`).

## Usage
1. **Choose a Dataset**: The solver requires a file named `data/input.json` to run. Choose one of the provided datasets and rename it:
   - For a small problem (5 customers): `cp data/small.json data/input.json`
   - For a medium problem (10 customers): `cp data/medium.json data/input.json`
2. **Select Algorithms**: In the sidebar, choose the search algorithms you want to compare.
3. **Run Simulation**: Click the "Run Simulation" button to execute the solvers.
4. **Explore Routes**: Use the tabs to view the animated route exploration for each algorithm.
5. **Compare Results**: Scroll down to see the performance comparison charts.
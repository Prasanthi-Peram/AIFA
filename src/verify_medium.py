import json
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(__file__))

from solver import run_solver

def verify():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "medium.json")
    with open(data_path, "r") as f:
        data = json.load(f)
    
    selected_algos = ["A*", "BFS", "UCS", "Greedy"]
    print(f"Running solver for {len(data['customers'])} customers and capacity {data['capacity']}...")
    
    results = run_solver(data, selected_algos)
    
    for res in results["results"]:
        print(f"Algorithm: {res['algorithm']}")
        print(f"  Cost: {res['cost']:.2f}")
        print(f"  Time: {res['time']:.4f}s")
        print(f"  Routes: {res['routes']}")
        
        # Basic validation
        visited = set()
        for route in res['routes']:
            for node in route:
                if node != 0:
                    visited.add(node)
        
        if len(visited) == len(data['customers']):
            print("  Status: SUCCESS (All customers visited)")
        else:
            print(f"  Status: FAILURE (Visited {len(visited)}/{len(data['customers'])} customers)")

if __name__ == "__main__":
    verify()

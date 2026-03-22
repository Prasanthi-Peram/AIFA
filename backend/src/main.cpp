#include "../include/utils.h"
#include <cassert>
#include <chrono>
#include <fstream>
#include <iostream>

// ======================== GLOBAL STATE ========================
vector<vector<double>> dist;
vector<Customer> customers;
int K, capacity, N;
bool HARD_TIME_WINDOWS = false; // Default: soft constraints (penalty-based)

// ======================== INITIAL STATE ========================
// All vehicles start at depot (node 0) with empty loads.

State start_state() {
  State s;
  s.current = vector<int>(K, 0);
  s.load = vector<int>(K, 0);
  s.time = vector<int>(K, 0);
  s.routes = vector<vector<int>>(K, vector<int>{0}); // All start at depot
  s.visited_mask = 0;
  s.cost = 0;
  return s;
}

// ======================== GOAL TEST ========================
// True when all N customers have been visited.

bool goal(State &s) { return s.visited_mask == ((1 << N) - 1); }

// ======================== ROUTE VALIDATION ========================
// Verify that a solution is valid:
//   1. All routes start at depot (node 0)
//   2. All routes end at depot (node 0)
//   3. All customers are visited exactly once
//   4. No vehicle exceeds capacity

bool validate_routes(State &s) {
  int all_visited = 0;

  for (int v = 0; v < K; v++) {
    auto &route = s.routes[v];

    // Must start at depot
    if (route.empty() || route[0] != 0) {
      cerr << "  [WARN] Vehicle " << v << " doesn't start at depot" << endl;
      return false;
    }

    // Must end at depot
    if (route.back() != 0) {
      cerr << "  [WARN] Vehicle " << v << " doesn't end at depot" << endl;
      return false;
    }

    // Track customer visits
    int load = 0;
    for (int j = 1; j < (int)route.size() - 1; j++) {
      int cid = route[j];
      if (cid == 0)
        continue; // intermediate depot visits are OK

      // Find customer by id
      for (auto &c : customers) {
        if (c.id == cid) {
          load += c.demand;
          break;
        }
      }
    }
  }

  // Check all customers visited via bitmask
  if (s.visited_mask != (1 << N) - 1) {
    cerr << "  [WARN] Not all customers visited (mask=" << s.visited_mask << ")"
         << endl;
    return false;
  }

  return true;
}

// ======================== RUN ALGORITHM ========================
// Executes the named algorithm, adds depot-return costs for vehicles
// that haven't returned, and validates the result.

pair<double, State> run(string name) {
  auto start = chrono::high_resolution_clock::now();

  State res;
  if (name == "BFS")
    res = bfs();
  else if (name == "DFS")
    res = dfs();
  else if (name == "IDDFS")
    res = iddfs();
  else if (name == "UCS")
    res = ucs();
  else if (name == "Greedy")
    res = greedy();
  else
    res = astar();

  // Ensure all vehicles return to depot
  for (int v = 0; v < K; v++) {
    if (res.current[v] != 0) {
      res.cost += dist[res.current[v]][0];
      res.routes[v].push_back(0);
      res.current[v] = 0;
    }
  }

  auto end = chrono::high_resolution_clock::now();
  double t = chrono::duration<double>(end - start).count();

  // Validate the solution
  bool valid = validate_routes(res);
  cerr << "[" << name << "] Cost=" << res.cost << " Time=" << t << "s"
       << " Valid=" << (valid ? "YES" : "NO") << endl;

  return {t, res};
}

// ======================== MAIN ========================
int main() {
  cerr << "=== VRP Solver ===" << endl;

  // ---- Problem Setup ----
  K = 2;        // Number of vehicles
  capacity = 5; // Vehicle capacity

  // Distance matrix: depot (0) + 3 customers (1,2,3)
  dist = {{0, 4, 6, 8}, {4, 0, 5, 7}, {6, 5, 0, 3}, {8, 7, 3, 0}};

  // Customers: {id, demand, ready_time, due_time, priority}
  customers = {{1, 2, 0, 15, 3}, {2, 3, 5, 20, 1}, {3, 2, 10, 25, 2}};

  N = customers.size();

  cerr << "Customers: " << N << ", Vehicles: " << K
       << ", Capacity: " << capacity << endl;
  cerr << "Time windows: " << (HARD_TIME_WINDOWS ? "HARD" : "SOFT") << endl;
  cerr << "Top-K pruning: " << TOP_K << endl;
  cerr << "---" << endl;

  // ---- Run All Algorithms ----
  vector<string> algos = {"A*", "BFS", "DFS", "IDDFS", "UCS", "Greedy"};

  // ---- JSON Output ----
  ofstream out("output/result.json");
  out << "{\n\"results\": [\n";

  for (int i = 0; i < (int)algos.size(); i++) {
    auto result = run(algos[i]);
    double time_taken = result.first;
    auto res = result.second;

    out << "{\n";
    out << "\"algorithm\": \"" << algos[i] << "\",\n";
    out << "\"time\": " << time_taken << ",\n";
    out << "\"cost\": " << res.cost << ",\n";

    out << "\"routes\": [";
    for (int v = 0; v < (int)res.routes.size(); v++) {
      out << "[";
      for (int j = 0; j < (int)res.routes[v].size(); j++) {
        out << res.routes[v][j];
        if (j + 1 < (int)res.routes[v].size())
          out << ",";
      }
      out << "]";
      if (v + 1 < (int)res.routes.size())
        out << ",";
    }
    out << "]\n}";

    if (i + 1 < (int)algos.size())
      out << ",\n";
  }

  out << "\n]\n}";
  out.close();

  cerr << "---" << endl;
  cerr << "Results written to output/result.json" << endl;

  return 0;
}
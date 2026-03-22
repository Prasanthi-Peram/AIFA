#include "../include/utils.h"
#include <algorithm>
#include <cmath>
#include <queue>
#include <unordered_map>

// ======================== MST-BASED HEURISTIC ========================
// Admissible heuristic using Prim's MST approximation.
//
// Computes a lower bound on the cost to visit all unvisited customers:
//   1. Find the minimum distance from any vehicle to any unvisited node
//   2. Compute MST over unvisited nodes using Prim's algorithm
//   3. Sum = min_connection_cost + MST_cost
//
// This is admissible because the actual cost >= MST cost
// (any valid tour/route is a spanning tree + extra edges).
// =====================================================================

double heuristic(State &s) {
  // Collect unvisited customer IDs
  vector<int> unvisited;
  for (int i = 0; i < N; i++) {
    if (!(s.visited_mask & (1 << i)))
      unvisited.push_back(customers[i].id);
  }

  if (unvisited.empty())
    return 0;

  int m = unvisited.size();

  // Step 1: Minimum connection cost from any vehicle to the unvisited set
  double min_connect = 1e18;
  for (int v = 0; v < K; v++) {
    for (int uid : unvisited) {
      min_connect = min(min_connect, dist[s.current[v]][uid]);
    }
  }

  if (m == 1)
    return min_connect;

  // Step 2: Prim's MST over unvisited nodes
  vector<double> min_edge(m, 1e18);
  vector<bool> in_mst(m, false);
  min_edge[0] = 0;
  double mst_cost = 0;

  for (int iter = 0; iter < m; iter++) {
    // Find the next node to add (closest to MST)
    int next = -1;
    double best = 1e18;
    for (int j = 0; j < m; j++) {
      if (!in_mst[j] && min_edge[j] < best) {
        best = min_edge[j];
        next = j;
      }
    }

    if (next == -1)
      break; // Disconnected graph
    in_mst[next] = true;
    mst_cost += best;

    // Update distances to remaining nodes
    for (int j = 0; j < m; j++) {
      if (!in_mst[j]) {
        double d = dist[unvisited[next]][unvisited[j]];
        min_edge[j] = min(min_edge[j], d);
      }
    }
  }

  return min_connect + mst_cost;
}

// ======================== A* SEARCH ========================
// Optimal search using f(s) = g(s) + h(s).
//
// Key improvements:
//   - MST-based admissible heuristic (guarantees optimality)
//   - Composite state key (visited_mask + vehicle positions)
//   - Prune states with worse cost than previously seen
// ============================================================

State astar() {
  // Priority queue entry: {state, f-value}
  struct PQEntry {
    State s;
    double f;
    bool operator>(const PQEntry &o) const { return f > o.f; }
  };

  priority_queue<PQEntry, vector<PQEntry>, greater<PQEntry>> pq;
  State start = start_state();
  pq.push({start, heuristic(start)});

  // State pruning: track best cost seen for each state key
  unordered_map<size_t, double> best;

  while (!pq.empty()) {
    auto cur = pq.top();
    pq.pop();
    State &s = cur.s;

    // Goal check: all customers visited
    if (goal(s))
      return s;

    // State pruning using composite key
    size_t key = s.state_key();
    if (best.count(key) && best[key] <= s.cost)
      continue;
    best[key] = s.cost;

    // Expand successors
    for (auto &ns : expand(s)) {
      size_t nkey = ns.state_key();
      // Skip if we've seen a better state
      if (best.count(nkey) && best[nkey] <= ns.cost)
        continue;
      double f = ns.cost + heuristic(ns);
      pq.push({ns, f});
    }
  }

  // No solution found — return start (will be detected as invalid)
  return start;
}
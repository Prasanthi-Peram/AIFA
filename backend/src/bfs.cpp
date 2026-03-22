#include "../include/utils.h"
#include <queue>
#include <unordered_map>

// ======================== BFS ========================
// Breadth-first search for VRP.
//
// Improvements:
//   - State pruning: skip states with worse cost than seen before
//   - Returns first goal found (shallowest solution)
//
// Note: BFS is not optimal for weighted graphs, but finds
// the solution with fewest customer assignments (shallowest).
// =====================================================

State bfs() {
  queue<State> q;
  q.push(start_state());

  // State pruning: best cost seen per state key
  unordered_map<size_t, double> best;

  while (!q.empty()) {
    State s = q.front();
    q.pop();

    // Goal check
    if (goal(s))
      return s;

    // Prune if we've seen this state with lower cost
    size_t key = s.state_key();
    if (best.count(key) && best[key] <= s.cost)
      continue;
    best[key] = s.cost;

    // Expand successors
    for (auto &ns : expand(s)) {
      size_t nkey = ns.state_key();
      if (best.count(nkey) && best[nkey] <= ns.cost)
        continue;
      q.push(ns);
    }
  }

  return start_state();
}
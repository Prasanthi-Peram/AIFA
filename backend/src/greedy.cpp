#include "../include/utils.h"
#include <queue>
#include <unordered_map>

// ======================== GREEDY SEARCH ========================
// Greedy best-first search for VRP.
//
// Expands states in order of h(s) only (ignores path cost).
// Fast but not guaranteed optimal.
//
// Improvements:
//   - State pruning: skip if same state seen with lower cost
//   - Uses MST-based heuristic for better guidance
// ===============================================================

State greedy() {
  // Priority queue entry
  struct PQEntry {
    State s;
    double h;
    bool operator>(const PQEntry &o) const { return h > o.h; }
  };

  priority_queue<PQEntry, vector<PQEntry>, greater<PQEntry>> pq;
  State start = start_state();
  pq.push({start, heuristic(start)});

  // State pruning
  unordered_map<size_t, double> best;

  while (!pq.empty()) {
    auto cur = pq.top();
    pq.pop();
    State &s = cur.s;

    // Goal check
    if (goal(s))
      return s;

    // State pruning
    size_t key = s.state_key();
    if (best.count(key) && best[key] <= s.cost)
      continue;
    best[key] = s.cost;

    // Expand successors, prioritize by heuristic
    for (auto &ns : expand(s)) {
      size_t nkey = ns.state_key();
      if (best.count(nkey) && best[nkey] <= ns.cost)
        continue;
      pq.push({ns, heuristic(ns)});
    }
  }

  return start;
}
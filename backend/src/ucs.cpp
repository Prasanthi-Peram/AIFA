#include "../include/utils.h"
#include <queue>
#include <unordered_map>

// ======================== UCS ========================
// Uniform Cost Search for VRP.
//
// Expands states in order of increasing g(s) cost.
// Guaranteed to find the optimal solution.
//
// Improvements:
//   - State pruning: skip if same state seen with lower cost
//   - Composite state key (visited_mask + vehicle positions)
// =====================================================

State ucs() {
  // Priority queue entry
  struct PQEntry {
    State s;
    double cost;
    bool operator>(const PQEntry &o) const { return cost > o.cost; }
  };

  priority_queue<PQEntry, vector<PQEntry>, greater<PQEntry>> pq;
  pq.push({start_state(), 0});

  // State pruning
  unordered_map<size_t, double> best;

  while (!pq.empty()) {
    auto cur = pq.top();
    pq.pop();
    State &s = cur.s;

    // Goal check: first goal popped is optimal
    if (goal(s))
      return s;

    // State pruning
    size_t key = s.state_key();
    if (best.count(key) && best[key] <= s.cost)
      continue;
    best[key] = s.cost;

    // Expand successors
    for (auto &ns : expand(s)) {
      size_t nkey = ns.state_key();
      if (best.count(nkey) && best[nkey] <= ns.cost)
        continue;
      pq.push({ns, ns.cost});
    }
  }

  return start_state();
}
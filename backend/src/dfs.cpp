#include "../include/utils.h"
#include <stack>
#include <unordered_map>

// ======================== DFS ========================
// Depth-first search for VRP.
//
// Improvements:
//   - State pruning: skip worse-cost revisits
//   - Tracks the best complete solution found
//   - Returns the best solution (not just any goal)
//
// DFS tends to find solutions fast but not necessarily optimal.
// =====================================================

State dfs() {
  stack<State> st;
  st.push(start_state());

  // State pruning
  unordered_map<size_t, double> best;

  // Track best complete solution
  State best_solution = start_state();
  double best_cost = 1e18;
  bool found = false;

  while (!st.empty()) {
    State s = st.top();
    st.pop();

    // Prune if this state already costs more than best solution
    if (found && s.cost >= best_cost)
      continue;

    // Prune if same state was seen with lower cost
    size_t key = s.state_key();
    if (best.count(key) && best[key] <= s.cost)
      continue;
    best[key] = s.cost;

    // Goal check: update best if better
    if (goal(s)) {
      if (s.cost < best_cost) {
        best_cost = s.cost;
        best_solution = s;
        found = true;
      }
      continue;
    }

    // Expand successors
    for (auto &ns : expand(s)) {
      if (found && ns.cost >= best_cost)
        continue;
      size_t nkey = ns.state_key();
      if (best.count(nkey) && best[nkey] <= ns.cost)
        continue;
      st.push(ns);
    }
  }

  return best_solution;
}
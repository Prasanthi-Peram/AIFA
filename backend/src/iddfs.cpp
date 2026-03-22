#include "../include/utils.h"
#include <unordered_map>

// ======================== IDDFS ========================
// Iterative Deepening Depth-First Search for VRP.
//
// Improvements over original:
//   - No global mutable state — uses references
//   - Depth = number of customers assigned (not tree depth)
//   - Proper max depth = N (one per customer)
//   - State pruning within each depth iteration
//   - Best-cost tracking to avoid worse solutions
// =======================================================

// ---- Depth-Limited Search (helper) ----
// depth: number of customer assignments made so far
// max_depth: maximum assignments allowed in this iteration
// result: best goal state found (passed by reference)
// found: whether any goal was found (passed by reference)
// best: state pruning map (reset per IDDFS iteration)

static void dls(State &s, int depth, int max_depth, State &result, bool &found,
                unordered_map<size_t, double> &best) {

  // Prune: stop if we already found a better solution
  if (found && s.cost >= result.cost)
    return;

  // Goal check
  if (goal(s)) {
    if (!found || s.cost < result.cost) {
      result = s;
      found = true;
    }
    return;
  }

  // Depth cutoff: stop if we've assigned max_depth customers
  if (depth >= max_depth)
    return;

  // State pruning
  size_t key = s.state_key();
  if (best.count(key) && best[key] <= s.cost)
    return;
  best[key] = s.cost;

  // Expand children
  for (auto &ns : expand(s)) {
    // Count how many new customers were assigned
    int new_assigned = __builtin_popcount(ns.visited_mask) -
                       __builtin_popcount(s.visited_mask);
    dls(ns, depth + new_assigned, max_depth, result, found, best);
  }
}

// ---- IDDFS Main ----
State iddfs() {
  State start = start_state();
  State result = start;
  bool found = false;

  // Iterate depth from 1 to N (each depth = max customer assignments)
  for (int max_depth = 1; max_depth <= N; max_depth++) {
    unordered_map<size_t, double> best;
    dls(start, 0, max_depth, result, found, best);

    if (found)
      return result;
  }

  return start;
}
#include "../include/utils.h"
#include <algorithm>

// ======================== EXPAND ========================
// Generate all valid successor states from the current state.
//
// Improvements over original:
//   1. Top-k pruning: for each vehicle, only expand nearest k unvisited
//   customers
//   2. Hard constraint rejection: skip if compute() returns -1
//   3. Depot-return option: allow a vehicle to return to depot (useful when
//      a vehicle has served some customers and should make room for others)
//   4. Strict capacity enforcement
// ================================================================

vector<State> expand(State &s) {
  vector<State> next;

  // Collect unvisited customer indices
  vector<int> unvisited;
  for (int i = 0; i < N; i++) {
    if (!(s.visited_mask & (1 << i)))
      unvisited.push_back(i);
  }

  // If no unvisited customers remain, no expansion needed
  if (unvisited.empty())
    return next;

  // For each vehicle, expand to top-k nearest unvisited customers
  for (int v = 0; v < K; v++) {

    // Sort unvisited customers by distance from this vehicle's position
    vector<int> candidates = unvisited;
    int vpos = s.current[v];
    sort(candidates.begin(), candidates.end(), [&](int a, int b) {
      return dist[vpos][customers[a].id] < dist[vpos][customers[b].id];
    });

    // Limit to top-k nearest neighbors to reduce branching factor
    int limit = min((int)candidates.size(), TOP_K);

    for (int idx = 0; idx < limit; idx++) {
      int i = candidates[idx];
      auto &c = customers[i];

      // Strict capacity check
      if (s.load[v] + c.demand > capacity)
        continue;

      // Compute cost and check feasibility
      auto result = compute(s.current[v], c, s.time[v]);
      double cost_add = result.first;
      int new_time = result.second;

      // Skip if hard time window constraint violated
      if (cost_add < 0)
        continue;

      // Create successor state
      State ns = s;
      ns.visited_mask |= (1 << i);
      ns.current[v] = c.id;
      ns.routes[v].push_back(c.id);
      ns.load[v] += c.demand;
      ns.time[v] = new_time;
      ns.cost += cost_add;

      next.push_back(ns);
    }

    // Depot-return option: allow vehicle v to return to depot
    // This is useful when:
    //   - The vehicle has visited at least one customer
    //   - It hasn't already returned to depot
    //   - Other vehicles can handle remaining customers
    if (s.current[v] != 0 && s.routes[v].size() > 1) {
      State ns = s;
      double return_cost = dist[s.current[v]][0];
      ns.cost += return_cost;
      ns.current[v] = 0;
      ns.routes[v].push_back(0);
      ns.load[v] = 0; // Reset load after returning
      ns.time[v] += (int)return_cost;

      next.push_back(ns);
    }
  }

  return next;
}
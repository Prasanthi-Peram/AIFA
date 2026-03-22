#pragma once
#include <functional>
#include <vector>
using namespace std;

// ======================== STATE ========================
// Represents the current state of all vehicles in the VRP.
// - current[v]:  node where vehicle v is currently located
// - load[v]:     total demand loaded onto vehicle v
// - time[v]:     current time for vehicle v
// - routes[v]:   ordered list of nodes visited by vehicle v
// - visited_mask: bitmask of which customers have been assigned
// - cost:        total accumulated cost
// ========================================================

struct State {
  vector<int> current;
  int visited_mask;

  vector<int> load;
  vector<int> time;

  double cost;
  vector<vector<int>> routes;

  // Generate a composite key for state pruning.
  // Combines visited_mask with vehicle positions for better discrimination.
  size_t state_key() const {
    size_t h = hash<int>()(visited_mask);
    for (int pos : current) {
      h ^= hash<int>()(pos) + 0x9e3779b9 + (h << 6) + (h >> 2);
    }
    return h;
  }

  // For priority queue ordering: lower cost = higher priority
  bool operator>(const State &other) const { return cost > other.cost; }
};
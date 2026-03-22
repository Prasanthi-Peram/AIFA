#pragma once
#include "customer.h"
#include "state.h"
#include <string>
#include <vector>
using namespace std;

// ======================== GLOBALS ========================
extern vector<vector<double>> dist;
extern vector<Customer> customers;
extern int K, capacity, N;

// Configuration flags
extern bool HARD_TIME_WINDOWS; // true = reject infeasible, false = penalize
const int TOP_K = 5;           // max neighbors to expand per vehicle

// ======================== CORE FUNCTIONS ========================

// Calculate travel cost between node i and node j at time t.
// Applies traffic multiplier during peak hours.
double travel_cost(int i, int j, int t);

// Compute the cost and arrival time for a vehicle at 'curr'
// visiting customer c at time 'time'.
// Returns {-1, -1} if hard time window is violated.
pair<double, int> compute(int curr, Customer &c, int time);

// Generate all valid successor states from state s.
// Applies top-k pruning and constraint checking.
vector<State> expand(State &s);

// Check if all customers have been visited.
bool goal(State &s);

// Admissible heuristic: MST-based lower bound on remaining cost.
double heuristic(State &s);

// Create the initial state with all vehicles at depot.
State start_state();

// ======================== SEARCH ALGORITHMS ========================
State bfs();
State dfs();
State iddfs();
State ucs();
State greedy();
State astar();
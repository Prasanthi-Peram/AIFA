#include "../include/utils.h"

// ======================== TRAVEL COST ========================
// Base distance with traffic multiplier during peak hours.
// Peak hours: 8-10 AM and 5-7 PM (1.5x multiplier).

double travel_cost(int i, int j, int t) {
  double base = dist[i][j];

  // Apply traffic congestion multiplier during peak hours
  if ((t >= 8 && t <= 10) || (t >= 17 && t <= 19))
    return base * 1.5;

  return base;
}

// ======================== COMPUTE ========================
// Calculate the cost of vehicle at 'curr' visiting customer c.
//
// Returns:
//   {total_cost, arrival_time} on success
//   {-1, -1} if hard time window is violated
//
// Behavior depends on HARD_TIME_WINDOWS:
//   HARD: reject if arrival > c.due (return {-1,-1})
//   SOFT: add penalty proportional to lateness and priority

pair<double, int> compute(int curr, Customer &c, int time) {
  double travel = travel_cost(curr, c.id, time);
  int arrival = time + (int)travel;

  // Wait if arriving before the customer's ready time
  if (arrival < c.ready)
    arrival = c.ready;

  // Time window violation check
  if (arrival > c.due) {
    if (HARD_TIME_WINDOWS) {
      // Hard constraint: reject this assignment entirely
      return {-1, -1};
    }
    // Soft constraint: add penalty proportional to lateness * priority
    double penalty = (arrival - c.due) * (10.0 * c.priority);
    return {travel + penalty, arrival};
  }

  return {travel, arrival};
}
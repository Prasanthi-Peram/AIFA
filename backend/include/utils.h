#pragma once
#include "state.h"
#include "customer.h"
#include <vector>
using namespace std;

extern vector<vector<double>> dist;
extern vector<Customer> customers;
extern int K, capacity, N;

double travel_cost(int i, int j, int t);
pair<double,int> compute(int curr, Customer &c, int time);
vector<State> expand(State &s);
bool goal(State &s);
double heuristic(State &s);
State start_state();
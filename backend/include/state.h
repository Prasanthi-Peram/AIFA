#pragma once
#include <vector>
using namespace std;

struct State {
    vector<int> current;
    int visited_mask;

    vector<int> load;
    vector<int> time;

    double cost;
    vector<vector<int>> routes;
};
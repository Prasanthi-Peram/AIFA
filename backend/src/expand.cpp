#include "../include/utils.h"

vector<State> expand(State &s) {
    vector<State> next;

    for (int i = 0; i < N; i++) {
        if (s.visited_mask & (1 << i)) continue;

        auto &c = customers[i];

        for (int v = 0; v < K; v++) {
            if (s.load[v] + c.demand > capacity) continue;

            auto result = compute(s.current[v], c, s.time[v]);
            int cost_add = result.first;
            int new_time = result.second;

            State ns = s;
            ns.visited_mask |= (1 << i);

            ns.current[v] = c.id;
            ns.routes[v].push_back(c.id);
            ns.load[v] += c.demand;
            ns.time[v] = new_time;
            ns.cost += cost_add;

            next.push_back(ns);
        }
    }

    return next;
}
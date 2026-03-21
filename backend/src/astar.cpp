#include "../include/utils.h"
#include <queue>
#include <unordered_map>

struct PQ {
    State s;
    double p;
};

struct cmp {
    bool operator()(PQ &a, PQ &b) {
        return a.p > b.p;
    }
};

double heuristic(State &s) {
    double h = 0;
    for (int i=0;i<N;i++) {
        if (!(s.visited_mask & (1<<i)))
            h += dist[s.current[0]][customers[i].id];
    }
    return h;
}

State astar() {
    priority_queue<PQ, vector<PQ>, cmp> pq;
    State start = start_state();
    pq.push({start, 0});

    unordered_map<int,double> best;

    while (!pq.empty()) {
        auto cur = pq.top(); pq.pop();
        State s = cur.s;

        if (goal(s)) return s;

        int key = s.visited_mask;

        if (best.count(key) && best[key] <= s.cost)
            continue;

        best[key] = s.cost;

        for (auto &ns: expand(s)) {
            double f = ns.cost + heuristic(ns);
            pq.push({ns, f});
        }
    }

    return start;
}
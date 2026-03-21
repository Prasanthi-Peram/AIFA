#include "../include/utils.h"
#include <queue>

struct PQ {
    State s;
    double p;
};

struct cmp {
    bool operator()(PQ &a, PQ &b) {
        return a.p > b.p;
    }
};

State greedy() {
    priority_queue<PQ, vector<PQ>, cmp> pq;

    State start = start_state();
    pq.push({start, heuristic(start)});

    while (!pq.empty()) {
        auto cur = pq.top(); pq.pop();
        State s = cur.s;

        if (goal(s)) return s;

        for (auto &ns : expand(s))
            pq.push({ns, heuristic(ns)});
    }

    return start;
}
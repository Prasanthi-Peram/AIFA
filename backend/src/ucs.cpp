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

State ucs() {
    priority_queue<PQ, vector<PQ>, cmp> pq;
    pq.push({start_state(), 0});

    while (!pq.empty()) {
        auto cur = pq.top(); pq.pop();
        State s = cur.s;

        if (goal(s)) return s;

        for (auto &ns : expand(s))
            pq.push({ns, ns.cost});
    }

    return start_state();
}
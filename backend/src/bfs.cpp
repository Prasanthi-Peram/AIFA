#include "../include/utils.h"
#include <queue>

State bfs() {
    queue<State> q;
    q.push(start_state());

    while (!q.empty()) {
        State s = q.front(); q.pop();

        if (goal(s)) return s;

        for (auto &ns : expand(s))
            q.push(ns);
    }

    return start_state();
}
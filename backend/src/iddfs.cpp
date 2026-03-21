#include "../include/utils.h"
#include <limits>

State result_state;
bool found = false;

// -------------------- DEPTH LIMITED SEARCH --------------------
void dls(State s, int depth, int max_depth) {

    if (found) return;

    // goal condition
    if (goal(s)) {
        result_state = s;
        found = true;
        return;
    }

    // depth cutoff
    if (depth >= max_depth) return;

    // expand children
    for (auto &ns : expand(s)) {
        dls(ns, depth + 1, max_depth);
    }
}

// -------------------- IDDFS --------------------
State iddfs() {

    State start = start_state();

    // max depth = number of customers (safe upper bound)
    for (int max_depth = 1; max_depth <= N; max_depth++) {

        found = false;

        dls(start, 0, max_depth);

        if (found) return result_state;
    }

    return start;
}
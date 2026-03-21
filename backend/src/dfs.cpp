#include "../include/utils.h"
#include <stack>

State dfs() {
    stack<State> st;
    st.push(start_state());

    while (!st.empty()) {
        State s = st.top(); st.pop();

        if (goal(s)) return s;

        for (auto &ns : expand(s))
            st.push(ns);
    }

    return start_state();
}
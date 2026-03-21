#include "../include/utils.h"

double travel_cost(int i, int j, int t) {
    double base = dist[i][j];
    if ((t >= 8 && t <= 10) || (t >= 17 && t <= 19))
        return base * 1.5;
    return base;
}

pair<double,int> compute(int curr, Customer &c, int time) {
    double travel = travel_cost(curr, c.id, time);
    int arrival = time + travel;

    if (arrival < c.ready) arrival = c.ready;

    double penalty = 0;
    if (arrival > c.due)
        penalty = (arrival - c.due) * (10 * c.priority);

    return {travel + penalty, arrival};
}
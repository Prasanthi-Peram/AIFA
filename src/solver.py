import heapq
import time
import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Set

@dataclass
class Customer:
    id: int
    demand: int
    ready: int
    due: int
    priority: int

@dataclass
class State:
    current: List[int]
    visited_mask: int
    load: List[int]
    time: List[int]
    cost: float
    routes: List[List[int]]

    def state_key(self) -> Tuple:
        return (self.visited_mask, tuple(self.current))

    def __gt__(self, other):
        return self.cost > other.cost

# Global-like configuration (will be passed or set per run)
class Solver:
    def __init__(self, K, capacity, dist, customers, top_k=5, hard_time_windows=False):
        self.K = K
        self.capacity = capacity
        self.dist = dist
        self.customers_list = customers
        self.customers_dict = {c.id: c for c in customers}
        self.N = len(customers)
        self.TOP_K = top_k
        self.HARD_TIME_WINDOWS = hard_time_windows

    def start_state(self) -> State:
        return State(
            current=[0] * self.K,
            visited_mask=0,
            load=[0] * self.K,
            time=[0] * self.K,
            cost=0.0,
            routes=[[0] for _ in range(self.K)]
        )

    def goal(self, s: State) -> bool:
        return s.visited_mask == (1 << self.N) - 1

    def travel_cost(self, i, j, t) -> float:
        base = self.dist[i][j]
        # Peak hours: 8-10 AM and 5-7 PM (1.5x multiplier)
        if (8 <= t <= 10) or (17 <= t <= 19):
            return base * 1.5
        return base

    def compute(self, curr, c: Customer, time_val) -> Tuple[float, int]:
        travel = self.travel_cost(curr, c.id, time_val)
        arrival = time_val + int(travel)

        if arrival < c.ready:
            arrival = c.ready

        if arrival > c.due:
            if self.HARD_TIME_WINDOWS:
                return -1.0, -1
            penalty = (arrival - c.due) * (10.0 * c.priority)
            return travel + penalty, arrival

        return travel, arrival

    def expand(self, s: State) -> List[State]:
        next_states = []
        unvisited = [i for i in range(self.N) if not (s.visited_mask & (1 << i))]

        if not unvisited:
            return next_states

        for v in range(self.K):
            # Sort unvisited customers by distance from this vehicle's position
            candidates = sorted(unvisited, key=lambda i: self.dist[s.current[v]][self.customers_list[i].id])
            
            limit = min(len(candidates), self.TOP_K)
            for idx in range(limit):
                i = candidates[idx]
                c = self.customers_list[i]

                if s.load[v] + c.demand > self.capacity:
                    continue

                cost_add, new_time = self.compute(s.current[v], c, s.time[v])
                if cost_add < 0:
                    continue

                ns = State(
                    current=list(s.current),
                    visited_mask=s.visited_mask | (1 << i),
                    load=list(s.load),
                    time=list(s.time),
                    cost=s.cost + cost_add,
                    routes=[list(r) for r in s.routes]
                )
                ns.current[v] = c.id
                ns.routes[v].append(c.id)
                ns.load[v] += c.demand
                ns.time[v] = new_time
                next_states.append(ns)

            # Depot-return option
            if s.current[v] != 0 and len(s.routes[v]) > 1:
                ns = State(
                    current=list(s.current),
                    visited_mask=s.visited_mask,
                    load=list(s.load),
                    time=list(s.time),
                    cost=s.cost + self.dist[s.current[v]][0],
                    routes=[list(r) for r in s.routes]
                )
                return_cost = self.dist[s.current[v]][0]
                ns.current[v] = 0
                ns.routes[v].append(0)
                ns.load[v] = 0
                ns.time[v] += int(return_cost)
                next_states.append(ns)

        return next_states

    def heuristic(self, s: State) -> float:
        unvisited = [self.customers_list[i].id for i in range(self.N) if not (s.visited_mask & (1 << i))]
        if not unvisited:
            return 0.0

        # Step 1: Min connection cost
        min_connect = float('inf')
        for v in range(self.K):
            for uid in unvisited:
                min_connect = min(min_connect, self.dist[s.current[v]][uid])

        if len(unvisited) == 1:
            return min_connect

        # Step 2: Prim's MST
        m = len(unvisited)
        min_edge = [float('inf')] * m
        in_mst = [False] * m
        min_edge[0] = 0.0
        mst_cost = 0.0

        for _ in range(m):
            next_node = -1
            best = float('inf')
            for j in range(m):
                if not in_mst[j] and min_edge[j] < best:
                    best = min_edge[j]
                    next_node = j
            
            if next_node == -1:
                break
            in_mst[next_node] = True
            mst_cost += best

            for j in range(m):
                if not in_mst[j]:
                    d = self.dist[unvisited[next_node]][unvisited[j]]
                    min_edge[j] = min(min_edge[j], d)

        return min_connect + mst_cost

    def astar(self) -> State:
        start = self.start_state()
        pq = [(self.heuristic(start), start)]
        best_costs = {}

        while pq:
            f, s = heapq.heappop(pq)
            if self.goal(s):
                return s

            key = s.state_key()
            if key in best_costs and best_costs[key] <= s.cost:
                continue
            best_costs[key] = s.cost

            for ns in self.expand(s):
                nkey = ns.state_key()
                if nkey in best_costs and best_costs[nkey] <= ns.cost:
                    continue
                heapq.heappush(pq, (ns.cost + self.heuristic(ns), ns))
        return start

    def bfs(self) -> State:
        from collections import deque
        q = deque([self.start_state()])
        best_costs = {}
        while q:
            s = q.popleft()
            if self.goal(s):
                return s
            key = s.state_key()
            if key in best_costs and best_costs[key] <= s.cost:
                continue
            best_costs[key] = s.cost
            for ns in self.expand(s):
                nkey = ns.state_key()
                if nkey in best_costs and best_costs[nkey] <= ns.cost:
                    continue
                q.append(ns)
        return self.start_state()

    def dfs(self) -> State:
        stack = [self.start_state()]
        best_costs = {}
        best_sol = self.start_state()
        best_sol_cost = float('inf')
        found = False

        while stack:
            s = stack.pop()
            if found and s.cost >= best_sol_cost:
                continue
            key = s.state_key()
            if key in best_costs and best_costs[key] <= s.cost:
                continue
            best_costs[key] = s.cost

            if self.goal(s):
                if s.cost < best_sol_cost:
                    best_sol_cost = s.cost
                    best_sol = s
                    found = True
                continue

            for ns in self.expand(s):
                if found and ns.cost >= best_sol_cost:
                    continue
                stack.append(ns)
        return best_sol

    def iddfs(self) -> State:
        start = self.start_state()
        self.iddfs_result = start
        self.iddfs_found = False

        def dls(s, depth, max_depth, best_costs):
            if self.iddfs_found and s.cost >= self.iddfs_result.cost:
                return
            if self.goal(s):
                if not self.iddfs_found or s.cost < self.iddfs_result.cost:
                    self.iddfs_result = s
                    self.iddfs_found = True
                return
            if depth >= max_depth:
                return
            key = s.state_key()
            if key in best_costs and best_costs[key] <= s.cost:
                return
            best_costs[key] = s.cost
            for ns in self.expand(s):
                # Count newly assigned customers
                new_assigned = bin(ns.visited_mask).count('1') - bin(s.visited_mask).count('1')
                dls(ns, depth + new_assigned, max_depth, best_costs)

        for max_d in range(1, self.N + 1):
            best_costs = {}
            dls(start, 0, max_d, best_costs)
            if self.iddfs_found:
                return self.iddfs_result
        return start

    def ucs(self) -> State:
        start = self.start_state()
        pq = [(0.0, start)]
        best_costs = {}
        while pq:
            cost, s = heapq.heappop(pq)
            if self.goal(s):
                return s
            key = s.state_key()
            if key in best_costs and best_costs[key] <= s.cost:
                continue
            best_costs[key] = s.cost
            for ns in self.expand(s):
                nkey = ns.state_key()
                if nkey in best_costs and best_costs[nkey] <= ns.cost:
                    continue
                heapq.heappush(pq, (ns.cost, ns))
        return start

    def greedy(self) -> State:
        start = self.start_state()
        pq = [(self.heuristic(start), start)]
        best_costs = {}
        while pq:
            h, s = heapq.heappop(pq)
            if self.goal(s):
                return s
            key = s.state_key()
            if key in best_costs and best_costs[key] <= s.cost:
                continue
            best_costs[key] = s.cost
            for ns in self.expand(s):
                nkey = ns.state_key()
                if nkey in best_costs and best_costs[nkey] <= ns.cost:
                    continue
                heapq.heappush(pq, (self.heuristic(ns), ns))
        return start

def run_solver(data, selected_algos):
    K = data['K']
    capacity = data['capacity']
    dist = data['dist']
    customers = [Customer(**c) for c in data['customers']]
    
    solver = Solver(K, capacity, dist, customers)
    results = []
    
    for name in selected_algos:
        start_time = time.time()
        if name == "A*":
            res = solver.astar()
        elif name == "BFS":
            res = solver.bfs()
        elif name == "DFS":
            res = solver.dfs()
        elif name == "IDDFS":
            res = solver.iddfs()
        elif name == "UCS":
            res = solver.ucs()
        elif name == "Greedy":
            res = solver.greedy()
        else:
            continue
            
        # Final return to depot
        for v in range(K):
            if res.current[v] != 0:
                res.cost += dist[res.current[v]][0]
                res.routes[v].append(0)
                res.current[v] = 0
                
        end_time = time.time()
        results.append({
            "algorithm": name,
            "time": end_time - start_time,
            "cost": res.cost,
            "routes": res.routes
        })
        
    return {"results": results}

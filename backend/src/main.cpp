#include "../include/utils.h"
#include <chrono>
#include <fstream>

vector<vector<double>> dist;
vector<Customer> customers;
int K, capacity, N;

// forward declarations
State bfs();
State dfs();
State ucs();
State greedy();
State astar();

State start_state() {
  State s;
  s.current = vector<int>(K, 0);
  s.load = vector<int>(K, 0);
  s.time = vector<int>(K, 0);
  s.routes = vector<vector<int>>(K, vector<int>{0});
  s.visited_mask = 0;
  s.cost = 0;
  return s;
}

bool goal(State &s) { return s.visited_mask == ((1 << N) - 1); }

pair<double, State> run(string name) {
  auto start = chrono::high_resolution_clock::now();

  State res;
  if (name == "BFS")
    res = bfs();
  else if (name == "DFS")
    res = dfs();
  else if (name == "UCS")
    res = ucs();
  else if (name == "Greedy")
    res = greedy();
  else
    res = astar();

  for (int v = 0; v < K; v++) {
    res.cost += dist[res.current[v]][0];
    res.routes[v].push_back(0);
  }

  auto end = chrono::high_resolution_clock::now();
  double t = chrono::duration<double>(end - start).count();

  return {t, res};
}

int main() {

  // sample input
  K = 2;
  capacity = 5;

  dist = {{0, 4, 6, 8}, {4, 0, 5, 7}, {6, 5, 0, 3}, {8, 7, 3, 0}};

  customers = {{1, 2, 0, 15, 3}, {2, 3, 5, 20, 1}, {3, 2, 10, 25, 2}};

  N = customers.size();

  vector<string> algos = {"A*", "BFS", "DFS", "UCS", "Greedy"};

  ofstream out("output/result.json");

  out << "{\n\"results\": [\n";

  for (int i = 0; i < algos.size(); i++) {
    auto result = run(algos[i]);
    double time_taken = result.first;
    auto res = result.second;

    out << "{\n";
    out << "\"algorithm\": \"" << algos[i] << "\",\n";
    out << "\"time\": " << time_taken << ",\n";
    out << "\"cost\": " << res.cost << ",\n";

    out << "\"routes\": [";

    for (int v = 0; v < res.routes.size(); v++) {
      out << "[";
      for (int j = 0; j < res.routes[v].size(); j++) {
        out << res.routes[v][j];
        if (j + 1 < res.routes[v].size())
          out << ",";
      }
      out << "]";
      if (v + 1 < res.routes.size())
        out << ",";
    }

    out << "]\n}";

    if (i + 1 < algos.size())
      out << ",\n";
  }

  out << "\n]\n}";

  out.close();
}
import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
import time

def animate_routes(dist, routes):
    G = nx.Graph()

    n = len(dist)
    for i in range(n):
        G.add_node(i)

    pos = nx.spring_layout(G, seed=42)

    placeholder = st.empty()
    colors = ["red", "blue", "green", "purple", "orange"]

    max_len = max(len(r) for r in routes)

    for step in range(max_len - 1):
        plt.figure()

        nx.draw(G, pos, with_labels=True, node_color="lightblue")

        for vidx, route in enumerate(routes):
            edges = []
            for i in range(min(step, len(route) - 1)):
                edges.append((route[i], route[i+1]))

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=edges,
                edge_color=colors[vidx % len(colors)],
                width=3
            )

        plt.title(f"Step {step + 1}")
        placeholder.pyplot(plt)

        time.sleep(0.6)
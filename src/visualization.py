import networkx as nx
import matplotlib.pyplot as plt
import streamlit as st
import time

def animate_routes(dist, routes):
    G = nx.Graph()

    n = len(dist)
    for i in range(n):
        G.add_node(i)

    # Use a fixed layout for all frames
    pos = nx.spring_layout(G, seed=42)
    
    # Pre-calculate axis limits to prevent jumping
    x_values = [p[0] for p in pos.values()]
    y_values = [p[1] for p in pos.values()]
    x_margin = (max(x_values) - min(x_values)) * 0.2
    y_margin = (max(y_values) - min(y_values)) * 0.2
    xlim = (min(x_values) - x_margin, max(x_values) + x_margin)
    ylim = (min(y_values) - y_margin, max(y_values) + y_margin)

    placeholder = st.empty()
    colors = ["#FF4B4B", "#0068C9", "#29B09D", "#7D3598", "#FFAA00"]

    max_len = max(len(r) for r in routes)

    for step in range(max_len):
        # Smaller figure size
        fig, ax = plt.subplots(figsize=(6, 4))
        
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        nx.draw(G, pos, with_labels=True, node_color="#E1E4E8", 
                node_size=500, font_size=10, ax=ax)

        for vidx, route in enumerate(routes):
            edges = []
            # Show progress up to current step
            for i in range(min(step, len(route) - 1)):
                edges.append((route[i], route[i+1]))

            nx.draw_networkx_edges(
                G,
                pos,
                edgelist=edges,
                edge_color=colors[vidx % len(colors)],
                width=2,
                ax=ax,
                label=f"Vehicle {vidx+1}"
            )

        ax.set_title(f"Route Progress: Step {step}", fontsize=12)
        # Use container width False to keep it small
        placeholder.pyplot(fig, use_container_width=False)
        plt.close(fig)

        time.sleep(0.3) # Faster animation
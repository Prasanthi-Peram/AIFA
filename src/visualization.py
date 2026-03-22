import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st
import textwrap

def animate_routes(dist, routes, algo_name, demands, route_colors=None, theme=None, step=1):
    """
    Minimal visualization UI optimized for Unified Route Explorer.
    - Uses an external step argument (from a slider in app.py).
    - Removed internal playback buttons.
    - Strictly professional, emoji-free.
    """
    if route_colors is None:
        route_colors = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]
    if theme is None:
        theme = {}

    # Theme colors
    face_color = theme.get("viz_face", "#f8fafc")
    node_unvisited = theme.get("viz_node_unvisited", "#f1f5f9")
    node_unvisited_edge = theme.get("viz_node_unvisited_edge", "#cbd5e1")
    label_color = theme.get("viz_label_color", "#1e293b")
    faded_edge = theme.get("viz_faded_edge", "#e2e8f0")
    edge_label_bg = theme.get("viz_edge_label_bg", "white")
    edge_label_fg = theme.get("viz_edge_label_fg", "#94a3b8")
    spine_color = theme.get("viz_spine", "#e2e8f0")
    text_primary = theme.get("text_primary", "#1e293b")
    text_muted = theme.get("text_muted", "#94a3b8")

    max_len = max(len(r) for r in routes)
    
    # ---- STEP DESCRIPTION ----
    description = "Initializing routes at the depot."
    if step > 1:
        actions = []
        for vidx, route in enumerate(routes):
            if step <= len(route):
                prev_node = route[step-2]
                curr_node = route[step-1]
                if prev_node != curr_node:
                    if curr_node == 0:
                        actions.append(f"V{vidx+1} returns to Depot")
                    else:
                        actions.append(f"V{vidx+1} visits C{curr_node}")
        if actions:
            description = " & ".join(actions) + "."
        else:
            description = "Vehicles maintaining current positions."
    if step == max_len:
        description = "Optimization complete."

    # ---- HEADER (Centered) ----
    _, hcol, _ = st.columns([1, 2, 1])
    with hcol:
        st.markdown(textwrap.dedent(f"""
        <div style="display: flex; align-items: flex-start; gap: 20px; margin-bottom: 10px; padding: 10px; border-bottom: 1px solid {faded_edge};">
            <div style="display: flex; flex-direction: column; align-items: center; border-right: 2px solid {faded_edge}; padding-right: 20px;">
                <div style="color: #22c55e; font-size: 2.5rem; font-weight: 800; line-height: 1;">{step:02d}</div>
                <div style="color: {text_primary}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Step</div>
            </div>
            <div style="padding-top: 5px;">
                <h3 style="margin: 0; color: {text_primary}; font-size: 1.2rem; font-weight: 600;">
                    {algo_name} Strategy
                </h3>
                <p style="margin: 5px 0 0 0; color: {text_primary}; font-size: 1rem; font-weight: 500;">
                    {description}
                </p>
            </div>
        </div>
        """), unsafe_allow_html=True)

    # ---- DRAW GRAPH ----
    G = nx.Graph()
    n = len(dist)
    for i in range(n):
        for j in range(i + 1, n):
            if dist[i][j] > 0:
                G.add_edge(i, j, weight=dist[i][j])

    pos = nx.circular_layout(G)
    pos = {k: v * 1.5 for k, v in pos.items()}
    x_values = [p[0] for p in pos.values()]
    y_values = [p[1] for p in pos.values()]
    x_margin = (max(x_values) - min(x_values)) * 0.35
    y_margin = (max(y_values) - min(y_values)) * 0.35
    xlim = (min(x_values) - x_margin, max(x_values) + x_margin)
    ylim = (min(y_values) - y_margin, max(y_values) + y_margin)

    # Node labels with Demand
    node_labels = {0: "D"}
    for i in range(1, n):
        d = demands[i] if i < len(demands) else "?"
        node_labels[i] = f"C{i}\n({d})"

    # Optimized figsize for Unified Explorer
    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor=face_color)
    ax.set_facecolor(face_color)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.axis('off')

    # Background edges
    nx.draw_networkx_edges(G, pos, edge_color=faded_edge, width=1.0, style='dashed', alpha=0.5, ax=ax)

    # Edge weights
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=9, font_color=edge_label_fg,
        font_family='sans-serif', ax=ax,
        bbox=dict(boxstyle='round,pad=0.15', facecolor=edge_label_bg, edgecolor='none', alpha=0.9)
    )

    # Depot node
    nx.draw_networkx_nodes(G, pos, nodelist=[0], node_color='#667eea', node_size=800,
                           edgecolors='#4f46e5', linewidths=2.5, ax=ax)

    # Visited / unvisited customer nodes
    customer_nodes = list(range(1, n))
    visited_nodes = set()
    for route in routes:
        limit = min(step, len(route))
        for i in range(limit):
            if route[i] != 0:
                visited_nodes.add(route[i])

    unvisited = [nd for nd in customer_nodes if nd not in visited_nodes]
    visited = [nd for nd in customer_nodes if nd in visited_nodes]

    if unvisited:
        nx.draw_networkx_nodes(G, pos, nodelist=unvisited, node_color=node_unvisited,
                               node_size=600, edgecolors=node_unvisited_edge, linewidths=2, ax=ax)
    if visited:
        nx.draw_networkx_nodes(G, pos, nodelist=visited, node_color='#dcfce7',
                               node_size=600, edgecolors='#22c55e', linewidths=2.5, ax=ax)

    # Node labels
    depot_label = {0: node_labels[0]}
    unvisited_labels = {nd: node_labels[nd] for nd in unvisited}
    visited_labels = {nd: node_labels[nd] for nd in visited}

    # Draw depot label
    nx.draw_networkx_labels(G, pos, labels=depot_label, font_size=9, font_weight='bold',
                            font_family='sans-serif', font_color=label_color, ax=ax)
    # Draw unvisited labels
    if unvisited_labels:
        nx.draw_networkx_labels(G, pos, labels=unvisited_labels, font_size=9, font_weight='bold',
                                font_family='sans-serif', font_color=label_color, ax=ax)
    # Draw visited labels with potentially different color
    if visited_labels:
        visited_label_color = theme.get("viz_visited_label_color", label_color)
        nx.draw_networkx_labels(G, pos, labels=visited_labels, font_size=9, font_weight='bold',
                                font_family='sans-serif', font_color=visited_label_color, ax=ax)

    # Route edges
    for vidx, route in enumerate(routes):
        color = route_colors[vidx % len(route_colors)]
        edges = []
        for i in range(min(step, len(route) - 1)):
            edges.append((route[i], route[i + 1]))

        if edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=edges, edge_color=color, width=3, alpha=0.85, ax=ax,
                arrows=True, arrowsize=12, arrowstyle='-|>',
                connectionstyle=f'arc3,rad={0.1 * (vidx + 1)}',
                min_source_margin=12, min_target_margin=12
            )

    # Legend
    legend_patches = []
    for vidx in range(len(routes)):
        color = route_colors[vidx % len(route_colors)]
        legend_patches.append(mpatches.Patch(color=color, label=f'Vehicle {vidx + 1}'))
    legend_patches.append(mpatches.Patch(color='#667eea', label='Depot'))
    legend_patches.append(mpatches.Patch(color='#dcfce7', label='Visited'))
    legend_patches.append(mpatches.Patch(color=node_unvisited, label='Unvisited'))

    ax.legend(handles=legend_patches, loc='upper right', fontsize=7,
              frameon=True, fancybox=True, shadow=False, framealpha=0.95,
              edgecolor=spine_color, facecolor=face_color, borderpad=0.8,
              labelcolor=label_color)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor(spine_color)
        spine.set_linewidth(1)

    fig.tight_layout()
    
    # Center the plot using columns
    _, pcol, _ = st.columns([1, 2, 1])
    with pcol:
        st.pyplot(fig, width='stretch')
    plt.close(fig)
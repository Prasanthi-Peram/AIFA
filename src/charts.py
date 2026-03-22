import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import textwrap

# Consistent color palette
CHART_COLORS = {
    "A*":     "#f59e0b",
    "BFS":    "#3b82f6",
    "DFS":    "#8b5cf6",
    "UCS":    "#10b981",
    "Greedy": "#f97316",
    "IDDFS":  "#ef4444",
}

def _get_color(algo):
    return CHART_COLORS.get(algo, "#94a3b8")


def show_comparison(results, theme=None):
    if not results:
        st.warning("No results to display")
        return

    if theme is None:
        theme = {}
    bg = theme.get("chart_bg", "white")
    paper = theme.get("chart_paper", "white")
    grid = theme.get("chart_grid", "#f1f5f9")
    text_color = theme.get("chart_text", "#1e293b")
    text_muted = theme.get("text_muted", "#94a3b8")

    df = pd.DataFrame(results)
    colors = [_get_color(a) for a in df["algorithm"]]

    # ---- Bar Charts: Cost & Time ----
    col1, col2 = st.columns(2)

    with col1:
        fig_cost = go.Figure()
        fig_cost.add_trace(go.Bar(
            x=df["algorithm"], y=df["cost"],
            marker=dict(color=colors, line=dict(width=0), cornerradius=6),
            text=[f"{c:.1f}" for c in df["cost"]],
            textposition='outside',
            textfont=dict(size=12, family="Inter", color=text_color),
            hovertemplate="<b>%{x}</b><br>Cost: %{y:.2f}<extra></extra>",
        ))
        fig_cost.update_layout(
            title=dict(text="Total Cost", font=dict(size=16, family="Inter", color=text_color)),
            xaxis=dict(tickfont=dict(size=12, family="Inter", color=text_muted), showgrid=False),
            yaxis=dict(title=dict(text="Cost", font=dict(size=12, family="Inter", color=text_muted)),
                       tickfont=dict(size=10, family="Inter", color=text_muted),
                       gridcolor=grid, showgrid=True, zeroline=False),
            plot_bgcolor=bg, paper_bgcolor=paper, height=350,
            margin=dict(l=50, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_cost, width='stretch')

    with col2:
        times_ms = df["time"] * 1000
        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(
            x=df["algorithm"], y=times_ms,
            marker=dict(color=colors, line=dict(width=0), cornerradius=6),
            text=[f"{t:.3f}ms" for t in times_ms],
            textposition='outside',
            textfont=dict(size=11, family="Inter", color=text_color),
            hovertemplate="<b>%{x}</b><br>Time: %{y:.4f} ms<extra></extra>",
        ))
        fig_time.update_layout(
            title=dict(text="Execution Time", font=dict(size=16, family="Inter", color=text_color)),
            xaxis=dict(tickfont=dict(size=12, family="Inter", color=text_muted), showgrid=False),
            yaxis=dict(title=dict(text="Time (ms)", font=dict(size=12, family="Inter", color=text_muted)),
                       tickfont=dict(size=10, family="Inter", color=text_muted),
                       gridcolor=grid, showgrid=True, zeroline=False),
            plot_bgcolor=bg, paper_bgcolor=paper, height=350,
            margin=dict(l=50, r=20, t=50, b=40),
        )
        st.plotly_chart(fig_time, width='stretch')

    # ---- Side-by-Side: Radar & Table ----
    st.markdown("<br>", unsafe_allow_html=True)
    rcol1, rcol2 = st.columns([1, 1])

    with rcol1:
        max_cost = df["cost"].max() if df["cost"].max() > 0 else 1
        max_time = df["time"].max() if df["time"].max() > 0 else 1

        fig_radar = go.Figure()
        for _, row in df.iterrows():
            algo = row["algorithm"]
            color = _get_color(algo)
            cost_score = 1 - (row["cost"] / max_cost) if max_cost > 0 else 0
            time_score = 1 - (row["time"] / max_time) if max_time > 0 else 0
            num_routes = len(row["routes"])
            route_efficiency = 1 / num_routes if num_routes > 0 else 0
            total_nodes = sum(len(r) for r in row["routes"]) - num_routes
            node_score = min(total_nodes / 6, 1.0)
            values = [cost_score, time_score, route_efficiency, node_score, cost_score]
            categories = ['Cost Efficiency', 'Speed', 'Route Efficiency', 'Coverage', 'Cost Efficiency']
            
            hex_col = color.lstrip('#')
            r_val, g_val, b_val = tuple(int(hex_col[i:i+2], 16) for i in (0, 2, 4))
            fill_rgba = f'rgba({r_val}, {g_val}, {b_val}, 0.1)'
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values, theta=categories, fill='toself',
                fillcolor=fill_rgba, line=dict(color=color, width=2),
                name=algo,
            ))

        fig_radar.update_layout(
            title=dict(text="Multi-Dimensional Comparison", font=dict(size=16, family="Inter", color=text_color)),
            polar=dict(
                bgcolor=bg,
                radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=8, color=text_muted), gridcolor=grid),
                angularaxis=dict(tickfont=dict(size=11, family="Inter", color=text_muted), gridcolor=grid),
            ),
            paper_bgcolor=paper, height=400,
            margin=dict(l=40, r=40, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=10, family="Inter", color=text_muted), bgcolor=bg),
        )
        st.plotly_chart(fig_radar, width='stretch')

    with rcol2:
        st.markdown(f'<h3 style="font-size: 1.1rem; font-weight: 600; color: {text_color}; margin-bottom: 1rem;">Comparison Summary</h3>', unsafe_allow_html=True)
        
        # Build rows without leading spaces to avoid Streamlit code-block interpretation
        rows_html = ""
        for _, row in df.iterrows():
            algo = row["algorithm"]
            color = _get_color(algo)
            routes_str = " | ".join([" → ".join(str(n) for n in r) for r in row["routes"]])
            rows_html += f'<tr style="border-bottom: 1px solid {grid};">'
            rows_html += f'<td style="padding: 12px 8px; font-weight: 600; color: {text_color};">'
            rows_html += f'<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:{color}; margin-right:8px;"></span>{algo}'
            rows_html += '</td>'
            rows_html += f'<td style="padding: 12px 8px; color: {text_color};">{row["cost"]:.1f}</td>'
            rows_html += f'<td style="padding: 12px 8px; color: {text_color};">{row["time"]*1000:.3f}ms</td>'
            rows_html += f'<td style="padding: 12px 8px; color: {text_muted}; font-size: 0.85rem; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{routes_str}">{routes_str}</td>'
            rows_html += '</tr>'

        # Minimal table without outer div border to avoid "extra thing" in dark mode
        table_html = textwrap.dedent(f"""
<table style="width: 100%; border-collapse: collapse; font-family: Inter, sans-serif; font-size: 0.95rem; text-align: left; background: {bg}; border-radius: 8px; overflow: hidden;">
<thead>
<tr style="background: {grid}; color: {text_muted}; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px;">
<th style="padding: 10px 8px;">Algorithm</th>
<th style="padding: 10px 8px;">Cost</th>
<th style="padding: 10px 8px;">Time</th>
<th style="padding: 10px 8px;">Routes</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>
""").strip()
        st.markdown(table_html, unsafe_allow_html=True)
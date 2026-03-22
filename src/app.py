import streamlit as st
import subprocess
import json
import time
import os
import textwrap

from utils import load_results
from visualization import animate_routes
from charts import show_comparison
from solver import run_solver

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="VRP Solver — AI Route Optimizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------------- DATA LOADING ----------------
# Load problem data from input.json at the start to make the UI dynamic
try:
    input_json_path = os.path.join(os.path.dirname(__file__), "..", "data", "input.json")
    with open(input_json_path, 'r') as f:
        problem_data = json.load(f)
    num_customers = len(problem_data["customers"])
    num_vehicles = problem_data["K"]
    vehicle_capacity = problem_data["capacity"]
except Exception as e:
    st.error(f"❌ Error loading problem data: {e}")
    st.stop()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    # Title and Theme Toggle inline
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("## VRP Solver")
    with col2:
        st.write("") # Vertical alignment padding
        try:
            import base64
            # Load sun icon
            sun_path = os.path.join(os.path.dirname(__file__), "assets", "sun_icon.png")
            with open(sun_path, "rb") as f:
                sun_b64 = base64.b64encode(f.read()).decode()
            
            # Load moon icon
            moon_path = os.path.join(os.path.dirname(__file__), "assets", "moon_icon.png")
            with open(moon_path, "rb") as f:
                moon_b64 = base64.b64encode(f.read()).decode()
            
            # Select icon based on current theme (show sun in dark mode, moon in light mode)
            current_b64 = sun_b64 if st.session_state.dark_mode else moon_b64
            
            # Clickable image button using custom CSS
            if st.button(" ", help="Toggle Light/Dark Mode", key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
            
            st.markdown(f"""
                <style>
                /* Target the button in the second column of the sidebar */
                [data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button {{
                    background-image: url("data:image/png;base64,{current_b64}") !important;
                    background-size: 24px 24px !important;
                    background-repeat: no-repeat !important;
                    background-position: center !important;
                    background-color: transparent !important;
                    border: none !important;
                    height: 32px !important;
                    width: 32px !important;
                    color: transparent !important;
                    filter: invert(1) !important; /* Make icon white */
                }}
                [data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button:hover {{
                    background-color: rgba(255, 255, 255, 0.1) !important;
                    border-radius: 4px !important;
                }}
                /* Hide the default button text */
                [data-testid="stSidebar"] [data-testid="column"]:nth-child(2) button div {{
                    display: none !important;
                }}
                </style>
                """, unsafe_allow_html=True)
        except Exception:
            # Fallback to emoji if image fails
            icon = "☀️" if st.session_state.dark_mode else "🌙"
            if st.button(icon, help="Toggle Light/Dark Mode"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()

    st.markdown("---")
    
    # Apply custom theme colors based on session state
    if st.session_state.dark_mode:
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] {
                background-color: #0e1117;
                color: #fafafa;
            }
            [data-testid="stSidebar"] {
                background-color: #262730;
            }
            /* Change multiselect tag colors to grey */
            span[data-baseweb="tag"] {
                background-color: #475569 !important;
                color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] {
                background-color: #ffffff;
                color: #31333f;
            }
            [data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
            /* Change multiselect tag colors to grey */
            span[data-baseweb="tag"] {
                background-color: #e2e8f0 !important;
                color: #475569 !important;
            }
            </style>
            """, unsafe_allow_html=True)

    st.markdown("### Configuration")

    # Algorithm selection for comparison
    algorithms = st.multiselect(
        "Select algorithms to compare",
        ["BFS", "DFS", "IDDFS", "UCS", "Greedy", "A*"],
        default=["A*", "Greedy", "BFS"]
    )

    st.markdown("---")
    st.markdown("### Problem Setup")
    # Dynamic problem setup based on input.json
    st.markdown(f"""
    - **Nodes:** Depot + {num_customers} Customers
    - **Vehicles:** {num_vehicles}
    - **Capacity:** {vehicle_capacity}
    """)

    st.markdown("---")
    # Button to trigger the solver
    run = st.button("Run Simulation", width='stretch')

# ---------------- THEME COLORS ----------------
if st.session_state.dark_mode:
    BG = "#0f172a"
    BG_CARD = "#1e293b"
    BG_SECONDARY = "#334155"
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    BORDER = "#334155"
    SHADOW = "rgba(0,0,0,0.4)"
    SHADOW_HOVER = "rgba(0,0,0,0.6)"
    TAG_BG = "#334155"
    STEP_BG = "#1e293b"
    CHART_BG = BG
    CHART_PAPER = BG
    CHART_GRID = "#334155"
    CHART_TEXT = "#e2e8f0"
    VIZ_FACE = "#1e293b"
    VIZ_NODE_UNVISITED = "#1e293b"
    VIZ_NODE_UNVISITED_EDGE = "#6366f1"
    VIZ_LABEL_COLOR = "#ffffff"
    VIZ_FADED_EDGE = "#334155"
    VIZ_EDGE_LABEL_BG = "#0f172a"
    VIZ_EDGE_LABEL_FG = "#94a3b8"
    VIZ_SPINE = "#334155"
else:
    BG = "#ffffff"
    BG_CARD = "#ffffff"
    BG_SECONDARY = "#f8fafc"
    TEXT_PRIMARY = "#1e293b"
    TEXT_SECONDARY = "#475569"
    TEXT_MUTED = "#94a3b8"
    BORDER = "#e2e8f0"
    SHADOW = "rgba(0,0,0,0.06)"
    SHADOW_HOVER = "rgba(0,0,0,0.12)"
    TAG_BG = "#f1f5f9"
    STEP_BG = "#f8fafc"
    CHART_BG = BG
    CHART_PAPER = BG
    CHART_GRID = "#f1f5f9"
    CHART_TEXT = "#1e293b"
    VIZ_FACE = "#f8fafc"
    VIZ_NODE_UNVISITED = "#f1f5f9"
    VIZ_NODE_UNVISITED_EDGE = "#cbd5e1"
    VIZ_LABEL_COLOR = "#1e293b"
    VIZ_FADED_EDGE = "#e2e8f0"
    VIZ_EDGE_LABEL_BG = "white"
    VIZ_EDGE_LABEL_FG = "#94a3b8"
    VIZ_SPINE = "#e2e8f0"

# Build theme dict for passing to charts/viz
THEME = {
    "dark_mode": st.session_state.dark_mode,
    "bg": BG, "bg_card": BG_CARD, "bg_secondary": BG_SECONDARY,
    "text_primary": TEXT_PRIMARY, "text_secondary": TEXT_SECONDARY, "text_muted": TEXT_MUTED,
    "border": BORDER, "shadow": SHADOW,
    "chart_bg": CHART_BG, "chart_paper": CHART_PAPER, "chart_grid": CHART_GRID, "chart_text": CHART_TEXT,
    "viz_face": VIZ_FACE, "viz_node_unvisited": VIZ_NODE_UNVISITED,
    "viz_node_unvisited_edge": VIZ_NODE_UNVISITED_EDGE, "viz_label_color": VIZ_LABEL_COLOR,
    "viz_faded_edge": VIZ_FADED_EDGE, "viz_edge_label_bg": VIZ_EDGE_LABEL_BG,
    "viz_edge_label_fg": VIZ_EDGE_LABEL_FG, "viz_spine": VIZ_SPINE,
    "viz_visited_label_color": "#000000" if st.session_state.dark_mode else TEXT_PRIMARY,
}

# ---------------- CUSTOM CSS (theme-aware) ----------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    .stApp {{
        font-family: 'Inter', sans-serif;
        background-color: {BG};
        font-size: 18px;
    }}
    h1 {{ font-size: 2.5rem !important; font-weight: 800 !important; margin-bottom: 0.5rem !important; }}
    h2 {{ font-size: 1.8rem !important; font-weight: 700 !important; margin-top: 2rem !important; }}
    h3 {{ font-size: 1.4rem !important; font-weight: 600 !important; }}

    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(99, 102, 241, 0.2);
    }}
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label {{
        color: #e2e8f0 !important;
    }}

    /* Hero header */
    .hero-header {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }}
    .hero-header h1 {{
        color: {TEXT_PRIMARY};
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
    }}
    .hero-header p {{
        color: {TEXT_MUTED};
        font-size: 1.2rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }}

    /* Metric cards */
    .metric-card {{
        background: {BG_CARD};
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        border: 1px solid {BORDER};
        box-shadow: 0 1px 3px {SHADOW}, 0 1px 2px {SHADOW};
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .metric-card:hover {{
        box-shadow: 0 10px 25px {SHADOW_HOVER};
        transform: translateY(-2px);
    }}
    .metric-card .label {{
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {TEXT_MUTED};
        margin-bottom: 0.25rem;
    }}
    .metric-card .value {{
        font-size: 2rem;
        font-weight: 700;
        color: {TEXT_PRIMARY};
    }}
    .metric-card .accent-bar {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
    }}

    /* Algorithm result card */
    .algo-card {{
        background: {BG_CARD};
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid {BORDER};
        box-shadow: 0 4px 16px {SHADOW};
        transition: all 0.3s ease;
    }}
    .algo-card:hover {{
        box-shadow: 0 8px 30px {SHADOW_HOVER};
    }}
    .algo-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 100px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    }}

    /* Section headers */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1.5rem 0 1rem 0;
    }}
    .section-header .icon {{
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }}
    .section-header h3 {{
        margin: 0;
        font-size: 1.15rem;
        font-weight: 700;
        color: {TEXT_PRIMARY};
    }}

    /* Route tags */
    .route-tag {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: {TAG_BG};
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        color: {TEXT_SECONDARY};
        margin: 0.2rem;
        border: 1px solid {BORDER};
    }}
    .route-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }}

    /* Step indicator */
    .step-indicator {{
        background: {STEP_BG};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }}
    .step-number {{
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }}
    .step-text {{
        font-size: 0.9rem;
        color: {TEXT_SECONDARY};
        line-height: 1.5;
    }}
    .step-text strong {{
        color: {TEXT_PRIMARY};
    }}

    /* Legend */
    .legend-box {{
        background: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 0.75rem 1rem;
        display: inline-flex;
        gap: 1rem;
        flex-wrap: wrap;
    }}
    .legend-item {{
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        font-weight: 500;
        color: {TEXT_SECONDARY};
    }}
    .legend-color {{
        width: 14px;
        height: 14px;
        border-radius: 4px;
        display: inline-block;
    }}

    /* Footer */
    .footer {{
        text-align: center;
        padding: 3rem 0;
        color: {TEXT_MUTED};
        font-size: 0.95rem;
        border-top: 1px solid {BORDER};
        margin-top: 6rem;
        width: 100%;
    }}

    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Ensure sidebar toggle is visible and prominent */
    button[data-testid="stSidebarCollapseButton"] {{
        background-color: rgba(102, 126, 234, 0.2) !important;
        border-radius: 8px !important;
        z-index: 1000001 !important;
        color: white !important;
    }}
    header[data-testid="stHeader"] {{
        background: transparent !important;
        z-index: 1000000 !important;
    }}

    /* Playback bar button overrides */
    div[data-testid="stHorizontalBlock"] button {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {TEXT_PRIMARY} !important;
        font-size: 1.5rem !important;
    }}
    div[data-testid="stHorizontalBlock"] button:hover {{
        color: #22c55e !important;
        background: rgba(102, 126, 234, 0.1) !important;
    }}
    
    /* Playback bar container styling */
    .playback-container {{
        background-color: {BG_CARD};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 10px;
        margin-top: 10px;
        box-shadow: 0 4px 12px {SHADOW};
    }}

    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }}
    .stButton > button:hover {{
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        transform: translateY(-1px);
    }}

    /* Divider styling */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, {BORDER}, transparent);
        margin: 2rem 0;
    }}

    /* Description text */
    .desc-text {{
        color: {TEXT_MUTED};
        font-size: 0.8rem;
        font-style: italic;
    }}

    /* Style tabs to be grey and reasonable size */
    div[data-baseweb="tab-list"] {{
        width: 100% !important;
        display: flex !important;
        justify-content: space-between !important;
        gap: 2rem !important;
    }}
    button[data-baseweb="tab"] p {{
        font-size: 20px !important;
        font-weight: 600 !important;
    }}
    button[data-baseweb="tab"] {{
        color: {TEXT_MUTED} !important;
        flex: 1 !important;
        text-align: center !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: #ef4444 !important; /* Keep selected tab red as in user image */
    }}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO HEADER ----------------
st.markdown(textwrap.dedent("""
<div class="hero-header">
    <h1>Vehicle Routing Problem Solver</h1>
    <p>AI-powered route optimization using search algorithms — BFS, DFS, UCS, Greedy, A*</p>
</div>
"""), unsafe_allow_html=True)

# ---------------- ALGORITHM INFO ----------------
ALGO_INFO = {
    "A*":      {"icon": "", "color": "#f59e0b", "desc": "Optimal – uses heuristic + cost"},
    "BFS":     {"icon": "", "color": "#3b82f6", "desc": "Complete – level-order exploration"},
    "DFS":     {"icon": "", "color": "#8b5cf6", "desc": "Fast – deep-first exploration"},
    "UCS":     {"icon": "", "color": "#10b981", "desc": "Optimal – uniform cost expansion"},
    "Greedy":  {"icon": "", "color": "#f97316", "desc": "Fast – heuristic-driven search"},
    "IDDFS":   {"icon": "", "color": "#ef4444", "desc": "Complete – iterative deepening"},
}

ROUTE_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#06b6d4"]

# Initialize session state
if "all_results" not in st.session_state:
    st.session_state.all_results = None
if "run_performed" not in st.session_state:
    st.session_state.run_performed = False

# ---------------- RUN ----------------
if run:
    if not algorithms:
        st.warning("Please select at least one algorithm from the sidebar.")
        st.stop()

    # Progress bar
    progress_bar = st.progress(0, text="Initializing solver...")
    progress_bar.progress(30, text="Running solver...")
    
    # Run Python solver
    try:
        input_json_path = os.path.join(os.path.dirname(__file__), "..", "data", "input.json")
        with open(input_json_path, 'r') as f:
            data = json.load(f)
        
        all_results_dict = run_solver(data, algorithms)
        all_results = all_results_dict["results"]
        
        # Write results to output.json for the user
        output_json_path = os.path.join(os.path.dirname(__file__), "..", "data", "output.json")
        with open(output_json_path, 'w') as f:
            json.dump(all_results_dict, f, indent=2)
            
    except Exception as e:
        st.error(f"❌ Error running solver: {e}")
        st.stop()

    progress_bar.progress(70, text="Loading results...")
    
    # Store in session state
    st.session_state.all_results = all_results
    st.session_state.run_performed = True

    progress_bar.progress(100, text="✅ Complete!")
    time.sleep(0.5)
    progress_bar.empty()

# ---------------- DISPLAY ----------------
if st.session_state.run_performed:
    all_results = st.session_state.all_results
    # Filter to only user-selected algorithms (dynamic filtering)
    results = [r for r in all_results if r["algorithm"] in algorithms]

    if not results:
        st.warning("None of the selected algorithms have results in the current run. Please click 'Run Simulation' again.")
        # We don't stop here, we still show the landing state if no results are selected
        st.session_state.run_performed = False
        st.rerun()

    # Load input data for visualization
    input_json_path = os.path.join(os.path.dirname(__file__), "..", "data", "input.json")
    try:
        with open(input_json_path, 'r') as f:
            input_data = json.load(f)
        dist = input_data["dist"]
        # Extract demands from customers list (depot at index 0 has 0 demand)
        demands = [0] * (len(input_data["customers"]) + 1)
        for c in input_data["customers"]:
            demands[c["id"]] = c["demand"]
    except Exception as e:
        st.error(f"❌ Error loading input data for visualization: {e}")
        st.stop()

    # ---- SUMMARY METRICS ----
    st.markdown(textwrap.dedent(f"""
<div class="section-header">
<h3>Summary Overview</h3>
</div>
""").strip(), unsafe_allow_html=True)

    best_cost = min(r["cost"] for r in results)
    fastest_time = min(r["time"] for r in results)
    best_algo = [r["algorithm"] for r in results if r["cost"] == best_cost][0]

    scol1, scol2, scol3, scol4 = st.columns(4)

    with scol1:
        st.markdown(f"""
<div class="metric-card">
    <div class="accent-bar" style="background: linear-gradient(90deg, #6366f1, #8b5cf6);"></div>
    <div class="label">Algorithms Run</div>
    <div class="value">{len(results)}</div>
</div>
""", unsafe_allow_html=True)

    with scol2:
        st.markdown(f"""
<div class="metric-card">
    <div class="accent-bar" style="background: linear-gradient(90deg, #10b981, #34d399);"></div>
    <div class="label">Best Cost</div>
    <div class="value">{best_cost}</div>
</div>
""", unsafe_allow_html=True)

    with scol3:
        st.markdown(f"""
<div class="metric-card">
    <div class="accent-bar" style="background: linear-gradient(90deg, #f59e0b, #fbbf24);"></div>
    <div class="label">Fastest Time</div>
    <div class="value">{fastest_time:.4f}s</div>
</div>
""", unsafe_allow_html=True)

    with scol4:
        st.markdown(f"""
<div class="metric-card">
    <div class="accent-bar" style="background: linear-gradient(90deg, #ef4444, #f87171);"></div>
    <div class="label">Best Algorithm</div>
    <div class="value" style="font-size:1.3rem;">{best_algo}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    # ---- ROUTE ANIMATIONS (TABS) ----
    if len(results) > 0:
        # ---- UNIFIED ROUTE EXPLORER ----
        st.markdown(textwrap.dedent(f"""
<div class="section-header">
<h3>Unified Route Explorer</h3>
</div>
""").strip(), unsafe_allow_html=True)

        algo_names = [res["algorithm"] for res in results]
        tabs = st.tabs(algo_names)
        
        for i, tab in enumerate(tabs):
            with tab:
                res = results[i]
                selected_algo = res["algorithm"]
                max_steps = max(len(r) for r in res["routes"])
                
                # Navigation state (unique per tab)
                step_key = f"step_slider_{selected_algo}"
                if step_key not in st.session_state:
                    st.session_state[step_key] = 1
                
                # Ensure current_step is within bounds
                if st.session_state[step_key] > max_steps:
                    st.session_state[step_key] = max_steps
                
                # Visualization Area
                st.markdown("<br>", unsafe_allow_html=True)
                animate_routes(dist, res["routes"], selected_algo, demands, ROUTE_COLORS, THEME, step=st.session_state[step_key])
                
                # Custom Navigation Bar at the Bottom
                st.markdown(f"""
                    <style>
                    .nav-bar {{
                        background-color: {BG_SECONDARY};
                        padding: 0.5rem 1rem;
                        border-radius: 0 0 8px 8px;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-top: -1rem;
                        border: 1px solid {BORDER};
                        border-top: none;
                    }}
                    .step-indicator {{
                        color: {TEXT_MUTED};
                        font-family: monospace;
                        font-size: 0.9rem;
                    }}
                    /* Increase size of navigation arrow icons */
                    div[data-testid="stButton"] button:has(div[data-testid="stMarkdownContainer"] p:contains(" < ")),
                    div[data-testid="stButton"] button:has(div[data-testid="stMarkdownContainer"] p:contains(" > ")) {{
                        font-size: 1.5rem !important;
                        font-weight: 700 !important;
                        height: 40px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

                # Navigation logic
                col_nav_left, col_nav_center, col_nav_right = st.columns([1, 1, 1])
                
                with col_nav_center:
                    # Centered Arrows
                    c_prev, c_next = st.columns(2)
                    with c_prev:
                        if st.button(" < ", help="Previous Step", key=f"prev_{selected_algo}", use_container_width=True):
                            if st.session_state[step_key] > 1:
                                st.session_state[step_key] -= 1
                                st.rerun()
                    with c_next:
                        if st.button(" > ", help="Next Step", key=f"next_{selected_algo}", use_container_width=True):
                            if st.session_state[step_key] < max_steps:
                                st.session_state[step_key] += 1
                                st.rerun()
                
                with col_nav_right:
                    # Right-aligned Step Indicator
                    st.markdown(f"""
                        <div style="text-align: right; padding-top: 0.5rem; color: {TEXT_MUTED}; font-family: monospace;">
                            {st.session_state[step_key]} / {max_steps}
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br><br>", unsafe_allow_html=True)

    # ---- COMPARISON CHARTS (only when multiple algorithms) ----
    if len(results) > 1:
        st.markdown("---")
        st.markdown(textwrap.dedent(f"""
<div class="section-header">
<h3>Algorithm Comparison</h3>
</div>
""").strip(), unsafe_allow_html=True)
        show_comparison(results, THEME)

    # ---- FOOTER ----
    st.markdown(textwrap.dedent(f"""
<div class="footer">
    VRP Solver Dashboard · Built with Streamlit + C++ Backend · AI Search Algorithms
</div>
"""), unsafe_allow_html=True)

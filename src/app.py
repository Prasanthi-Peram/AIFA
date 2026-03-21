import streamlit as st
import subprocess
import json
import time
import os

from utils import load_results
from visualization import animate_routes
from charts import show_comparison

# ---------------- UI ----------------
st.set_page_config(page_title="VRP Solver", layout="wide")

st.title("Vehicle Routing Problem Dashboard")

st.markdown("### Select Algorithms")

algorithms = st.multiselect(
    "Choose algorithms to run",
    ["BFS", "DFS", "IDDFS", "UCS", "Greedy", "A*"],
    default=["A*"]
)

run = st.button("Run Simulation")

# ---------------- RUN ----------------
if run:

    st.info("Running C++ backend...")

    # (Optional) Save selected algorithms
    try:
        data_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "data")
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "selected.json"), "w") as f:
            json.dump({"algorithms": algorithms}, f)
    except Exception as e:
        st.warning(f"Could not save selected algorithms: {e}")

    # Run C++ executable
    try:
        backend_exe = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "vrp_solver"))
        subprocess.run([backend_exe], check=True, cwd=os.path.dirname(backend_exe))
    except Exception as e:
        st.error(f"Error running backend: {e}")
        st.stop()

    st.success("Execution completed!")

    # Load results
    results = load_results()

    if not results:
        st.error("No results found. Check backend output.")
        st.stop()

    # Dummy distance (keep same as backend for now)
    dist = [
        [0, 4, 6, 8],
        [4, 0, 5, 7],
        [6, 5, 0, 3],
        [8, 7, 3, 0]
    ]

    # ---------------- DISPLAY ----------------
    for res in results:
        st.divider()
        st.subheader(f"🔹 {res['algorithm']}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Cost", round(res["cost"], 2))
            st.metric("Time (s)", round(res["time"], 4))

        with col2:
            st.write("Routes:")
            for i, r in enumerate(res["routes"]):
                st.write(f"Vehicle {i+1}: {r}")

        st.markdown("### 🛣️ Route Animation")
        animate_routes(dist, res["routes"])

        time.sleep(0.3)

    # ---------------- CHARTS ----------------
    st.divider()
    show_comparison(results)
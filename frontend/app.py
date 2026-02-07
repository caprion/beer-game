"""
Beer Game Simulation — Streamlit Frontend
==========================================
Interactive simulation with all agents, demand patterns, information
sharing modes, KPI dashboards, and experiment runners.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import itertools
import time

from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from profiles_beergame.engine.demand_patterns import step_demand, seasonal_demand, noisy_demand, shock_demand
from profiles_beergame.metrics.analytics import (
    compute_bullwhip, summarize_kpis, compute_system_cost,
    compute_service_level, compute_order_oscillation, compare_scenarios,
)
from profiles_beergame.agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from profiles_beergame.agents.conservative_custodian import ConservativeCustodianAgent
from profiles_beergame.agents.myopic_firefighter import MyopicFirefighterAgent
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent
from profiles_beergame.agents.random_baseline import RandomBaselineAgent
from profiles_beergame.agents.signal_chaser import SignalChaserAgent
from profiles_beergame.agents.rational_analyst import RationalAnalystAgent
from profiles_beergame.agents.stabilizer import StabilizerAgent
from profiles_beergame.agents.production_smoother import ProductionSmootherAgent
from profiles_beergame.agents.bayesian_updater import BayesianUpdaterAgent
from profiles_beergame.agents.inverter import InverterAgent
from profiles_beergame.agents.antifragile_adapter import AntifragileAdapterAgent
from profiles_beergame.agents.info_aware import InfoAwareAgent

st.set_page_config(page_title="Beer Game Simulation", layout="wide")

# ──────────────────────────────────────────────────────────────
# Indian Earth Design System — Custom CSS
# ──────────────────────────────────────────────────────────────

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Base typography ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif;
    color: #3d2b1f;
    line-height: 1.6;
}
h1, h2, h3, h4 {
    font-family: 'Libre Baskerville', Georgia, serif;
    font-weight: 400;
    color: #3d2b1f;
    line-height: 1.2;
}
h1 { font-size: 2.25rem; }
h2 { font-size: 1.875rem; }
h3 { font-size: 1.5rem; }
h4 { font-size: 1.25rem; font-weight: 500; }

/* ── App background ── */
[data-testid="stAppViewContainer"] { background-color: #faf6f0; }
[data-testid="stHeader"] { background-color: #faf6f0; }
[data-testid="stSidebar"] {
    background-color: #f5efe5;
    border-right: 1px solid #ede4d5;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2 {
    font-family: 'Libre Baskerville', Georgia, serif;
    color: #3d2b1f;
}

/* ── Captions & secondary text ── */
[data-testid="stCaptionContainer"] { color: #6b5443; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #ede4d5;
    border-radius: 8px;
    padding: 0.75rem;
    box-shadow: 0 1px 2px rgba(61, 43, 31, 0.04);
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 2px 8px rgba(61, 43, 31, 0.06);
}
[data-testid="stMetricLabel"] { color: #6b5443; font-weight: 500; }
[data-testid="stMetricValue"] { color: #1a5c4c; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #ede4d5;
    border-radius: 8px;
}
[data-testid="stExpander"]:hover {
    box-shadow: 0 2px 8px rgba(61, 43, 31, 0.06);
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid #ede4d5;
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 500;
    color: #6b5443;
    border-radius: 6px 6px 0 0;
}
.stTabs [aria-selected="true"] {
    color: #1a5c4c;
    border-bottom: 2px solid #1a5c4c;
}

/* ── Buttons ── */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: #1a5c4c;
    border: 1px solid #1a5c4c;
    color: #faf6f0;
    border-radius: 6px;
    font-weight: 500;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: #14483b;
    border-color: #14483b;
}
.stDownloadButton > button {
    background: transparent;
    border: 1px solid #1a5c4c;
    color: #1a5c4c;
    border-radius: 6px;
    font-weight: 500;
}
.stDownloadButton > button:hover {
    background: #e4f0ec;
    border-color: #14483b;
    color: #14483b;
}

/* ── Data tables (markdown-rendered) ── */
.table-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    margin-bottom: 0.5rem;
}
table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.875rem;
    white-space: nowrap;
}
th {
    background: #f5efe5;
    color: #3d2b1f;
    border-bottom: 2px solid #1a5c4c;
    padding: 0.5rem 0.75rem;
    text-align: left;
    font-weight: 600;
    letter-spacing: 0.02em;
}
td {
    border-bottom: 1px solid #ede4d5;
    padding: 0.5rem 0.75rem;
    color: #3d2b1f;
}
tr:hover td { background: #fdf9f4; }

/* ── Dividers & alerts ── */
hr { border-color: #ede4d5; }
[data-testid="stAlert"] {
    border-radius: 8px;
    border: 1px solid #ede4d5;
}

/* ── Selectbox / inputs ── */
[data-baseweb="select"] > div {
    border-color: #ede4d5;
    border-radius: 6px;
}
[data-baseweb="input"] > div {
    border-color: #ede4d5;
    border-radius: 6px;
}

/* ── Success / error callouts ── */
[data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 8px;
}
</style>
""")

# ──────────────────────────────────────────────────────────────
# Earth-toned chart palette
# ──────────────────────────────────────────────────────────────

EARTH_PALETTE = ["#1a5c4c", "#c2452d", "#6b5744", "#8B6914", "#4a7c6f", "#d4815a"]
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#faf6f0",
    plot_bgcolor="#faf6f0",
    font=dict(family="IBM Plex Sans, sans-serif", color="#3d2b1f"),
)

# ──────────────────────────────────────────────────────────────
# Agent registry — maps profile name → (class, default params, param specs)
# ──────────────────────────────────────────────────────────────

AGENT_REGISTRY = {
    "passive_pipeline": {
        "class": PassivePipelineAgent,
        "label": "Passive Pipeline",
        "category": "rational",
        "params": {"target_inventory": ("slider", 4, 24, 12, "Target Inventory")},
    },
    "stabilizer": {
        "class": StabilizerAgent,
        "label": "Stabilizer (System Thinker)",
        "category": "rational",
        "params": {
            "target_inventory": ("slider", 4, 24, 12, "Target Inventory"),
            "smoothing_alpha": ("float_slider", 0.05, 0.8, 0.3, "Smoothing Alpha"),
            "max_correction_per_period": ("slider", 1, 10, 4, "Max Correction/Period"),
        },
    },
    "bayesian_updater": {
        "class": BayesianUpdaterAgent,
        "label": "Bayesian Updater",
        "category": "rational",
        "params": {
            "target_inventory": ("slider", 4, 24, 12, "Target Inventory"),
            "prior_demand": ("float_slider", 1.0, 10.0, 4.0, "Prior Demand"),
            "prior_strength": ("slider", 1, 20, 5, "Prior Strength"),
        },
    },
    "inverter": {
        "class": InverterAgent,
        "label": "Inverter (Munger's Inversion)",
        "category": "rational",
        "params": {
            "target_inventory": ("slider", 4, 24, 12, "Target Inventory"),
            "max_change_rate": ("slider", 1, 8, 3, "Max Change Rate"),
        },
    },
    "antifragile_adapter": {
        "class": AntifragileAdapterAgent,
        "label": "Antifragile Adapter",
        "category": "rational",
        "params": {
            "target_inventory": ("slider", 4, 24, 12, "Target Inventory"),
            "initial_buffer": ("float_slider", 0.5, 5.0, 1.0, "Initial Buffer"),
            "learning_rate": ("float_slider", 0.01, 0.3, 0.1, "Learning Rate"),
            "max_buffer": ("float_slider", 2.0, 12.0, 6.0, "Max Buffer"),
        },
    },
    "info_aware": {
        "class": InfoAwareAgent,
        "label": "Info-Aware",
        "category": "rational",
        "params": {
            "target_inventory": ("slider", 4, 24, 12, "Target Inventory"),
            "smoothing_alpha": ("float_slider", 0.05, 0.8, 0.3, "Smoothing Alpha"),
            "info_weight": ("float_slider", 0.0, 1.0, 0.5, "Info Weight"),
        },
    },
    "production_smoother": {
        "class": ProductionSmootherAgent,
        "label": "Production Smoother",
        "category": "moderate",
        "params": {
            "window_size": ("slider", 2, 10, 5, "Window Size"),
            "min_production": ("slider", 0, 6, 2, "Min Production"),
            "max_production": ("slider", 8, 30, 15, "Max Production"),
        },
    },
    "rational_analyst": {
        "class": RationalAnalystAgent,
        "label": "Rational Analyst (ignores pipeline)",
        "category": "moderate",
        "params": {
            "target_inventory": ("slider", 4, 24, 12, "Target Inventory"),
            "smoothing": ("float_slider", 0.0, 0.8, 0.0, "Smoothing"),
        },
    },
    "random_baseline": {
        "class": RandomBaselineAgent,
        "label": "Random Baseline",
        "category": "noise",
        "params": {
            "low": ("slider", 0, 8, 0, "Low"),
            "high": ("slider", 4, 20, 10, "High"),
            "seed": ("number", 1, 9999, 42, "Seed"),
        },
    },
    "aggressive_growth_hacker": {
        "class": AggressiveGrowthHackerAgent,
        "label": "Aggressive Growth-Hacker",
        "category": "behavioral",
        "params": {
            "amplification_factor": ("float_slider", 1.0, 3.0, 1.5, "Amplification Factor"),
            "safety_buffer": ("slider", 0, 10, 3, "Safety Buffer"),
            "panic_threshold": ("slider", 0, 10, 2, "Panic Threshold"),
        },
    },
    "conservative_custodian": {
        "class": ConservativeCustodianAgent,
        "label": "Conservative Custodian",
        "category": "behavioral",
        "params": {
            "conservation_factor": ("float_slider", 0.4, 1.0, 0.8, "Conservation Factor"),
            "max_inventory_target": ("slider", 3, 20, 8, "Max Inventory Target"),
            "panic_backlog_threshold": ("slider", 2, 12, 5, "Panic Backlog Threshold"),
        },
    },
    "myopic_firefighter": {
        "class": MyopicFirefighterAgent,
        "label": "Myopic Firefighter",
        "category": "behavioral",
        "params": {
            "panic_inventory_threshold": ("slider", 1, 10, 3, "Panic Inventory Threshold"),
            "panic_backlog_threshold": ("slider", 1, 10, 2, "Panic Backlog Threshold"),
            "overstock_threshold": ("slider", 8, 30, 15, "Overstock Threshold"),
            "emotional_volatility": ("float_slider", 0.0, 1.0, 0.3, "Emotional Volatility"),
            "seed": ("number", 1, 9999, 42, "Seed"),
        },
    },
    "signal_chaser": {
        "class": SignalChaserAgent,
        "label": "Signal Chaser",
        "category": "behavioral",
        "params": {
            "trend_sensitivity": ("float_slider", 1.0, 4.0, 2.0, "Trend Sensitivity"),
            "momentum_window": ("slider", 2, 6, 3, "Momentum Window"),
            "extrapolation_factor": ("float_slider", 1.0, 3.0, 1.8, "Extrapolation Factor"),
            "min_trend_threshold": ("slider", 0, 5, 1, "Min Trend Threshold"),
        },
    },
}

PROFILE_NAMES = list(AGENT_REGISTRY.keys())
PROFILE_LABELS = {k: v["label"] for k, v in AGENT_REGISTRY.items()}
LABEL_TO_KEY = {v["label"]: k for k, v in AGENT_REGISTRY.items()}

ROLES = ["retailer", "wholesaler", "distributor", "factory"]


# ──────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────

def render_param_widgets(profile_key: str, role: str) -> dict:
    """Render Streamlit widgets for agent parameters and return values."""
    spec = AGENT_REGISTRY[profile_key]
    params = {}
    for param_name, (widget_type, lo, hi, default, label) in spec["params"].items():
        key = f"{role}_{param_name}"
        if widget_type == "slider":
            params[param_name] = st.slider(label, lo, hi, default, key=key)
        elif widget_type == "float_slider":
            params[param_name] = st.slider(label, float(lo), float(hi), float(default), step=0.05, key=key)
        elif widget_type == "number":
            params[param_name] = int(st.number_input(label, min_value=lo, max_value=hi, value=default, key=key))
    return params


def create_agent(profile_key: str, params: dict):
    """Instantiate an agent from profile key and params dict."""
    cls = AGENT_REGISTRY[profile_key]["class"]
    return cls(**params)


def build_demand_fn(demand_type: str, demand_params: dict):
    """Build a demand function from UI selections."""
    if demand_type == "Constant":
        return constant_demand(demand_params["base"])
    elif demand_type == "Step":
        return step_demand(
            initial=demand_params["initial"],
            final=demand_params["final"],
            step_period=demand_params["step_period"],
        )
    elif demand_type == "Seasonal":
        return seasonal_demand(
            base=demand_params["base"],
            amplitude=demand_params["amplitude"],
            period=demand_params["period"],
        )
    elif demand_type == "Noisy":
        return noisy_demand(
            base=demand_params["base"],
            noise=demand_params["noise"],
            seed=demand_params.get("seed", 42),
        )
    elif demand_type == "Shock":
        return shock_demand(
            base=demand_params["base"],
            shock_period=demand_params["shock_period"],
            shock_duration=demand_params["shock_duration"],
            shock_magnitude=demand_params["shock_magnitude"],
        )
    return constant_demand(4)


def plot_orders(df: pd.DataFrame, title: str = "Orders Placed") -> go.Figure:
    fig = px.line(df, x="t", y="placed_order", color="role", title=title,
                  color_discrete_sequence=EARTH_PALETTE,
                  labels={"t": "Period", "placed_order": "Order Qty", "role": "Role"})
    fig.update_layout(height=350, margin=dict(t=40, b=30), **PLOTLY_LAYOUT)
    return fig


def plot_inventory_backlog(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Inventory", "Backlog"], shared_xaxes=True)
    for i, role in enumerate(ROLES):
        role_df = df[df["role"] == role]
        color = EARTH_PALETTE[i % len(EARTH_PALETTE)]
        fig.add_trace(go.Scatter(x=role_df["t"], y=role_df["inventory"], name=role,
                                 line=dict(color=color)), row=1, col=1)
        fig.add_trace(go.Scatter(x=role_df["t"], y=role_df["backlog"], name=role,
                                 line=dict(color=color), showlegend=False), row=1, col=2)
    fig.update_layout(height=350, margin=dict(t=40, b=30), **PLOTLY_LAYOUT)
    return fig


def plot_costs(df: pd.DataFrame) -> go.Figure:
    cost_df = df.groupby("role").agg(
        holding=("cost_holding", "sum"),
        backlog=("cost_backlog", "sum"),
    ).reset_index()
    cost_df = cost_df.melt(id_vars="role", var_name="cost_type", value_name="total_cost")
    fig = px.bar(cost_df, x="role", y="total_cost", color="cost_type", barmode="stack",
                 title="Cost Breakdown by Role",
                 color_discrete_sequence=["#1a5c4c", "#c2452d"],
                 labels={"total_cost": "Total Cost (\u20b9)", "role": "Role", "cost_type": "Cost Type"})
    fig.update_layout(height=350, margin=dict(t=40, b=30), **PLOTLY_LAYOUT)
    return fig


def plot_bullwhip(bw: pd.DataFrame) -> go.Figure:
    bw_display = bw.copy()
    bw_display["bullwhip_capped"] = bw_display["bullwhip_factor"].clip(upper=100)
    bw_display["label"] = bw_display["bullwhip_factor"].apply(lambda x: f"{x:.1f}" if x < 100 else f"{x:.0f}")
    fig = px.bar(bw_display, x="role", y="bullwhip_capped", text="label",
                 title="Bullwhip Factor by Role (variance amplification)",
                 color_discrete_sequence=["#c2452d"],
                 labels={"bullwhip_capped": "Bullwhip Factor", "role": "Role"})
    fig.add_hline(y=1.0, line_dash="dash", line_color="#1a5c4c", annotation_text="No amplification (1.0)")
    fig.update_layout(height=350, margin=dict(t=40, b=30), **PLOTLY_LAYOUT)
    return fig


def display_kpi_cards(df: pd.DataFrame):
    """Display key metrics as Streamlit metric cards."""
    bw = compute_bullwhip(df)
    sl = compute_service_level(df)
    sys_cost = compute_system_cost(df)
    kpis = summarize_kpis(df)
    osc = compute_order_oscillation(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("System Total Cost", f"\u20b9{sys_cost:,.0f}")
    c2.metric("Avg Bullwhip", f"{bw['bullwhip_factor'].mean():.1f}x")
    c3.metric("Max Bullwhip", f"{bw['bullwhip_factor'].max():.1f}x")
    c4.metric("Avg Fill Rate", f"{sl['fill_rate'].mean():.0%}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Inventory", f"{kpis['avg_inventory'].mean():.1f}")
    c6.metric("Avg Backlog", f"{kpis['avg_backlog'].mean():.1f}")
    c7.metric("Order Variance", f"{kpis['order_variance'].mean():.1f}")
    c8.metric("Avg Oscillation", f"{osc['oscillation_index'].mean():.2f}")


def df_to_markdown(df: pd.DataFrame, float_fmt: str = ".2f") -> str:
    """Convert a DataFrame to an HTML table wrapped in a scrollable div."""
    cols = list(df.columns)
    thead = "<tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>"
    rows = []
    for _, row in df.iterrows():
        cells = []
        for c in cols:
            val = row[c]
            if isinstance(val, float):
                cells.append(f"<td>{val:{float_fmt}}</td>")
            else:
                cells.append(f"<td>{val}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    tbody = "\n".join(rows)
    return f'<div class="table-scroll"><table><thead>{thead}</thead><tbody>{tbody}</tbody></table></div>'


# ──────────────────────────────────────────────────────────────
# Main app
# ──────────────────────────────────────────────────────────────

tab_sim, tab_experiment, tab_info_exp, tab_optimizer = st.tabs([
    "Single Simulation",
    "Profile Comparison",
    "Info Symmetry Experiment",
    "Combination Optimizer",
])


# ═══════════════════════════════════════════════════════════════
# TAB 1: Single Simulation
# ═══════════════════════════════════════════════════════════════

with tab_sim:
    st.header("Beer Game Simulation")
    st.caption("Configure agents, demand, and information sharing, then run.")

    col_config, col_demand = st.columns([1, 1])

    with col_config:
        st.subheader("Simulation Settings")
        num_periods = st.slider("Periods", 10, 100, 52, key="sim_periods")
        info_mode = st.selectbox("Information Sharing", ["none", "adjacent"],
                                 help="'adjacent' lets agents see upstream/downstream partner state", key="sim_info")
        random_seed = st.number_input("Random Seed", value=42, key="sim_seed")

    with col_demand:
        st.subheader("Demand Pattern")
        demand_type = st.selectbox("Pattern", ["Constant", "Step", "Seasonal", "Noisy", "Shock"], key="sim_demand")
        demand_params = {}
        if demand_type == "Constant":
            demand_params["base"] = st.slider("Demand", 1, 20, 4, key="d_base")
        elif demand_type == "Step":
            demand_params["initial"] = st.slider("Initial Demand", 1, 15, 4, key="d_init")
            demand_params["final"] = st.slider("Final Demand", 2, 25, 8, key="d_final")
            demand_params["step_period"] = st.slider("Step at Period", 1, 50, 10, key="d_step")
        elif demand_type == "Seasonal":
            demand_params["base"] = st.slider("Base Demand", 1, 15, 4, key="d_sbase")
            demand_params["amplitude"] = st.slider("Amplitude", 1, 10, 3, key="d_amp")
            demand_params["period"] = st.slider("Cycle Length", 4, 26, 12, key="d_period")
        elif demand_type == "Noisy":
            demand_params["base"] = st.slider("Base Demand", 1, 15, 4, key="d_nbase")
            demand_params["noise"] = st.slider("Noise Range (+/-)", 0, 8, 2, key="d_noise")
            demand_params["seed"] = int(st.number_input("Noise Seed", value=42, key="d_nseed"))
        elif demand_type == "Shock":
            demand_params["base"] = st.slider("Base Demand", 1, 15, 4, key="d_shbase")
            demand_params["shock_period"] = st.slider("Shock at Period", 1, 50, 15, key="d_shper")
            demand_params["shock_duration"] = st.slider("Shock Duration (periods)", 1, 10, 3, key="d_shdur")
            demand_params["shock_magnitude"] = st.slider("Shock Magnitude", 5, 30, 12, key="d_shmag")

    st.divider()
    st.subheader("Agent Selection")
    labels_list = [PROFILE_LABELS[k] for k in PROFILE_NAMES]
    default_profiles = {
        "retailer": "signal_chaser",
        "wholesaler": "passive_pipeline",
        "distributor": "passive_pipeline",
        "factory": "production_smoother",
    }
    agent_selections = {}
    agent_params = {}

    cols = st.columns(4)
    for i, role in enumerate(ROLES):
        with cols[i]:
            st.markdown(f"**{role.upper()}**")
            default_idx = labels_list.index(PROFILE_LABELS[default_profiles[role]])
            label = st.selectbox("Profile", labels_list, index=default_idx, key=f"sim_{role}_profile", label_visibility="collapsed")
            profile_key = LABEL_TO_KEY[label]
            agent_selections[role] = profile_key
            with st.expander("Parameters"):
                agent_params[role] = render_param_widgets(profile_key, f"sim_{role}")

    st.divider()
    if st.button("Run Simulation", type="primary", key="run_sim"):
        agents = {role: create_agent(agent_selections[role], agent_params[role]) for role in ROLES}
        config = SimulationConfig(
            periods=num_periods,
            information_sharing=info_mode,
            random_seed=int(random_seed),
        )
        demand_fn = build_demand_fn(demand_type, demand_params)
        runner = SimulationRunner(agents, demand_fn, config)
        df = runner.run()
        st.session_state["last_sim"] = df
        st.session_state["last_sim_config"] = {
            "agents": {r: PROFILE_LABELS[agent_selections[r]] for r in ROLES},
            "demand": demand_type,
            "info_mode": info_mode,
            "periods": num_periods,
        }

    if "last_sim" in st.session_state:
        df = st.session_state["last_sim"]
        cfg = st.session_state["last_sim_config"]

        st.subheader("Key Performance Indicators")
        display_kpi_cards(df)

        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(plot_orders(df), width="stretch")
        with col_b:
            st.plotly_chart(plot_inventory_backlog(df), width="stretch")

        col_c, col_d = st.columns(2)
        with col_c:
            st.plotly_chart(plot_bullwhip(compute_bullwhip(df)), width="stretch")
        with col_d:
            st.plotly_chart(plot_costs(df), width="stretch")

        with st.expander("View Raw Data"):
            st.markdown(df_to_markdown(df), unsafe_allow_html=True)

        with st.expander("Detailed KPIs Table"):
            st.markdown("**KPI Summary**")
            st.markdown(df_to_markdown(summarize_kpis(df)), unsafe_allow_html=True)
            st.markdown("**Service Level & Oscillation**")
            sl = compute_service_level(df)
            osc = compute_order_oscillation(df)
            st.markdown(df_to_markdown(sl.merge(osc, on="role")), unsafe_allow_html=True)

        csv = df.to_csv(index=False)
        st.download_button("Download Results CSV", csv, "beer_game_results.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════
# TAB 2: Profile Comparison Experiment
# ═══════════════════════════════════════════════════════════════

with tab_experiment:
    st.header("Profile Comparison — All Agents Head-to-Head")
    st.caption("Runs every agent as a homogeneous 4-role team and compares bullwhip, cost, and service level.")

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        exp_periods = st.slider("Periods", 10, 100, 52, key="exp_periods")
    with col_e2:
        exp_demand = st.selectbox("Demand Pattern", ["Constant", "Step", "Seasonal", "Shock"], key="exp_demand")
    with col_e3:
        exp_seed = st.number_input("Seed", value=42, key="exp_seed")

    # Demand config
    exp_demand_params = {}
    if exp_demand == "Constant":
        exp_demand_params["base"] = st.slider("Demand", 1, 15, 4, key="exp_d_base")
    elif exp_demand == "Step":
        c1, c2, c3 = st.columns(3)
        exp_demand_params["initial"] = c1.slider("Initial", 1, 15, 4, key="exp_d_init")
        exp_demand_params["final"] = c2.slider("Final", 2, 25, 8, key="exp_d_final")
        exp_demand_params["step_period"] = c3.slider("Step at", 1, 50, 10, key="exp_d_step")
    elif exp_demand == "Seasonal":
        c1, c2, c3 = st.columns(3)
        exp_demand_params["base"] = c1.slider("Base", 1, 15, 4, key="exp_d_sb")
        exp_demand_params["amplitude"] = c2.slider("Amplitude", 1, 10, 3, key="exp_d_amp")
        exp_demand_params["period"] = c3.slider("Cycle", 4, 26, 12, key="exp_d_per")
    elif exp_demand == "Shock":
        c1, c2, c3, c4 = st.columns(4)
        exp_demand_params["base"] = c1.slider("Base", 1, 15, 4, key="exp_d_shb")
        exp_demand_params["shock_period"] = c2.slider("At", 1, 50, 15, key="exp_d_shp")
        exp_demand_params["shock_duration"] = c3.slider("Duration", 1, 10, 3, key="exp_d_shd")
        exp_demand_params["shock_magnitude"] = c4.slider("Magnitude", 5, 30, 12, key="exp_d_shm")

    profiles_to_compare = st.multiselect(
        "Profiles to Compare",
        options=PROFILE_NAMES,
        default=PROFILE_NAMES,
        format_func=lambda k: PROFILE_LABELS[k],
        key="exp_profiles",
    )

    if st.button("Run Comparison", type="primary", key="run_exp"):
        demand_fn = build_demand_fn(exp_demand, exp_demand_params)
        config = SimulationConfig(periods=exp_periods, random_seed=int(exp_seed))

        all_results = {}
        progress = st.progress(0)
        for i, profile_key in enumerate(profiles_to_compare):
            cls = AGENT_REGISTRY[profile_key]["class"]
            default_params = {k: v[3] for k, v in AGENT_REGISTRY[profile_key]["params"].items()}
            agents = {role: cls(**default_params) for role in ROLES}
            runner = SimulationRunner(agents, demand_fn, config)
            all_results[profile_key] = runner.run()
            progress.progress((i + 1) / len(profiles_to_compare))
        progress.empty()

        st.session_state["exp_results"] = all_results

    if "exp_results" in st.session_state:
        all_results = st.session_state["exp_results"]
        comparison = compare_scenarios(all_results)
        comparison = comparison.sort_values("system_total_cost")
        comparison["scenario_label"] = comparison["scenario"].map(PROFILE_LABELS)

        st.subheader("Ranking (by Total System Cost)")

        if len(comparison) >= 2:
            col_best, col_worst = st.columns(2)
            best = comparison.iloc[0]
            worst = comparison.iloc[-1]
            col_best.success(f"**Best:** {PROFILE_LABELS.get(best['scenario'], best['scenario'])}  \nCost: \u20b9{best['system_total_cost']:,.0f} | Bullwhip: {best['avg_bullwhip']:.1f}x")
            col_worst.error(f"**Worst:** {PROFILE_LABELS.get(worst['scenario'], worst['scenario'])}  \nCost: \u20b9{worst['system_total_cost']:,.0f} | Bullwhip: {worst['avg_bullwhip']:.1f}x")

        fig_cost = px.bar(comparison, x="scenario_label", y="system_total_cost",
                          title="System Total Cost by Profile",
                          color_discrete_sequence=["#1a5c4c"],
                          labels={"system_total_cost": "Total Cost (\u20b9)", "scenario_label": "Profile"},
                          log_y=True)
        fig_cost.update_layout(height=400, xaxis_tickangle=-45, **PLOTLY_LAYOUT)
        st.plotly_chart(fig_cost, width="stretch")

        col_bw, col_fr = st.columns(2)
        with col_bw:
            fig_bw = px.bar(comparison, x="scenario_label", y="avg_bullwhip",
                            title="Average Bullwhip Factor", log_y=True,
                            color_discrete_sequence=["#c2452d"],
                            labels={"avg_bullwhip": "Avg Bullwhip", "scenario_label": "Profile"})
            fig_bw.add_hline(y=1.0, line_dash="dash", line_color="#1a5c4c")
            fig_bw.update_layout(height=350, xaxis_tickangle=-45, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_bw, width="stretch")
        with col_fr:
            fig_fr = px.bar(comparison, x="scenario_label", y="avg_fill_rate",
                            title="Average Fill Rate (service level)",
                            color_discrete_sequence=["#6b5744"],
                            labels={"avg_fill_rate": "Fill Rate", "scenario_label": "Profile"})
            fig_fr.update_layout(height=350, xaxis_tickangle=-45, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_fr, width="stretch")

        with st.expander("Full Comparison Table"):
            st.markdown(df_to_markdown(comparison), unsafe_allow_html=True)

        csv_exp = comparison.to_csv(index=False)
        st.download_button("Download Comparison CSV", csv_exp, "profile_comparison.csv", "text/csv", key="dl_exp")


# ═══════════════════════════════════════════════════════════════
# TAB 3: Information Symmetry Experiment
# ═══════════════════════════════════════════════════════════════

with tab_info_exp:
    st.header("Information Symmetry vs Asymmetry")
    st.caption("Does giving agents visibility into neighbors' positions change bullwhip?")

    st.info("This runs the **same agents** under `none` (classic) and `adjacent` (neighbor visibility) modes and compares results.", icon="ℹ️")

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        info_periods = st.slider("Periods", 10, 100, 52, key="info_periods")
        info_seed = st.number_input("Seed", value=42, key="info_seed")
    with col_i2:
        info_demand_type = st.selectbox("Demand Pattern", ["Constant", "Step", "Seasonal", "Shock"], key="info_demand")

    info_demand_params = {}
    if info_demand_type == "Constant":
        info_demand_params["base"] = st.slider("Demand", 1, 15, 4, key="info_d_base")
    elif info_demand_type == "Step":
        c1, c2, c3 = st.columns(3)
        info_demand_params["initial"] = c1.slider("Initial", 1, 15, 4, key="info_d_init")
        info_demand_params["final"] = c2.slider("Final", 2, 25, 8, key="info_d_final")
        info_demand_params["step_period"] = c3.slider("Step at", 1, 50, 10, key="info_d_step")
    elif info_demand_type == "Seasonal":
        c1, c2, c3 = st.columns(3)
        info_demand_params["base"] = c1.slider("Base", 1, 15, 4, key="info_d_sb")
        info_demand_params["amplitude"] = c2.slider("Amplitude", 1, 10, 3, key="info_d_amp")
        info_demand_params["period"] = c3.slider("Cycle", 4, 26, 12, key="info_d_per")
    elif info_demand_type == "Shock":
        c1, c2, c3, c4 = st.columns(4)
        info_demand_params["base"] = c1.slider("Base", 1, 15, 4, key="info_d_shb")
        info_demand_params["shock_period"] = c2.slider("At", 1, 50, 15, key="info_d_shp")
        info_demand_params["shock_duration"] = c3.slider("Duration", 1, 10, 3, key="info_d_shd")
        info_demand_params["shock_magnitude"] = c4.slider("Magnitude", 5, 30, 12, key="info_d_shm")

    st.subheader("Agent Sets to Compare")

    AGENT_SETS = {
        "Behavioral Mix": {
            "retailer": ("signal_chaser", {}),
            "wholesaler": ("passive_pipeline", {}),
            "distributor": ("aggressive_growth_hacker", {}),
            "factory": ("myopic_firefighter", {"seed": 42}),
        },
        "Smart Agents (Stabilizer + Adapter)": {
            "retailer": ("stabilizer", {}),
            "wholesaler": ("stabilizer", {}),
            "distributor": ("antifragile_adapter", {}),
            "factory": ("stabilizer", {}),
        },
        "Info-Aware Team": {
            "retailer": ("info_aware", {"info_weight": 0.7}),
            "wholesaler": ("info_aware", {"info_weight": 0.7}),
            "distributor": ("info_aware", {"info_weight": 0.7}),
            "factory": ("info_aware", {"info_weight": 0.7}),
        },
        "All Passive Pipeline": {
            "retailer": ("passive_pipeline", {}),
            "wholesaler": ("passive_pipeline", {}),
            "distributor": ("passive_pipeline", {}),
            "factory": ("passive_pipeline", {}),
        },
    }

    selected_sets = st.multiselect(
        "Agent sets",
        options=list(AGENT_SETS.keys()),
        default=["Behavioral Mix", "Smart Agents (Stabilizer + Adapter)", "Info-Aware Team"],
        key="info_sets",
    )

    if st.button("Run Info Sharing Experiment", type="primary", key="run_info"):
        demand_fn = build_demand_fn(info_demand_type, info_demand_params)
        info_results = {}
        total_runs = len(selected_sets) * 2
        progress = st.progress(0)
        run_i = 0

        for set_name in selected_sets:
            agent_spec = AGENT_SETS[set_name]
            for info_mode_val in ["none", "adjacent"]:
                agents = {}
                for role, (profile_key, extra_params) in agent_spec.items():
                    default_params = {k: v[3] for k, v in AGENT_REGISTRY[profile_key]["params"].items()}
                    default_params.update(extra_params)
                    agents[role] = create_agent(profile_key, default_params)

                config = SimulationConfig(
                    periods=info_periods,
                    information_sharing=info_mode_val,
                    random_seed=int(info_seed),
                )
                runner = SimulationRunner(agents, demand_fn, config)
                info_label = "No Sharing" if info_mode_val == "none" else "Neighbor Sharing"
                label = f"{set_name} \u2014 {info_label}"
                info_results[label] = runner.run()
                run_i += 1
                progress.progress(run_i / total_runs)
        progress.empty()

        st.session_state["info_results"] = info_results

    if "info_results" in st.session_state:
        info_results = st.session_state["info_results"]

        st.subheader("Comparison: No Sharing vs Neighbor Sharing")

        rows = []
        scenario_names = list(info_results.keys())
        for name in scenario_names:
            df_r = info_results[name]
            bw = compute_bullwhip(df_r)
            sl = compute_service_level(df_r)
            rows.append({
                "Scenario": name,
                "Total Cost": compute_system_cost(df_r),
                "Avg Bullwhip": bw["bullwhip_factor"].mean(),
                "Max Bullwhip": bw["bullwhip_factor"].max(),
                "Avg Fill Rate": sl["fill_rate"].mean(),
            })
        paired_df = pd.DataFrame(rows)

        for set_name in selected_sets:
            none_label = f"{set_name} \u2014 No Sharing"
            adj_label = f"{set_name} \u2014 Neighbor Sharing"
            if none_label in info_results and adj_label in info_results:
                st.markdown(f"### {set_name}")
                none_row = paired_df[paired_df["Scenario"] == none_label].iloc[0]
                adj_row = paired_df[paired_df["Scenario"] == adj_label].iloc[0]

                cost_delta = adj_row["Total Cost"] - none_row["Total Cost"]
                cost_pct = (cost_delta / none_row["Total Cost"] * 100) if none_row["Total Cost"] != 0 else 0
                bw_delta = adj_row["Avg Bullwhip"] - none_row["Avg Bullwhip"]

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Cost (No Sharing)", f"\u20b9{none_row['Total Cost']:,.0f}")
                c2.metric("Cost (Neighbor Sharing)", f"\u20b9{adj_row['Total Cost']:,.0f}", delta=f"{cost_pct:.1f}%", delta_color="inverse")
                c3.metric("Bullwhip (No Sharing)", f"{none_row['Avg Bullwhip']:.1f}x")
                c4.metric("Bullwhip (Neighbor Sharing)", f"{adj_row['Avg Bullwhip']:.1f}x",
                          delta=f"{bw_delta:.1f}", delta_color="inverse")

        fig = px.bar(paired_df, x="Scenario", y="Total Cost", title="Total Cost by Scenario",
                     color_discrete_sequence=["#1a5c4c"],
                     log_y=True, labels={"Total Cost": "System Cost (\u20b9)"})
        fig.update_layout(height=400, xaxis_tickangle=-45, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, width="stretch")

        col_bw2, col_fr2 = st.columns(2)
        with col_bw2:
            fig_bw2 = px.bar(paired_df, x="Scenario", y="Avg Bullwhip", title="Average Bullwhip",
                             color_discrete_sequence=["#c2452d"],
                             log_y=True)
            fig_bw2.add_hline(y=1.0, line_dash="dash", line_color="#1a5c4c")
            fig_bw2.update_layout(height=350, xaxis_tickangle=-45, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_bw2, width="stretch")
        with col_fr2:
            fig_fr2 = px.bar(paired_df, x="Scenario", y="Avg Fill Rate", title="Average Fill Rate",
                             color_discrete_sequence=["#6b5744"])
            fig_fr2.update_layout(height=350, xaxis_tickangle=-45, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_fr2, width="stretch")

        with st.expander("Per-Role Bullwhip Detail"):
            for name, df_detail in info_results.items():
                bw = compute_bullwhip(df_detail)
                st.markdown(f"**{name}**")
                st.markdown(df_to_markdown(bw), unsafe_allow_html=True)

        with st.expander("Full Comparison Table"):
            st.markdown(df_to_markdown(paired_df), unsafe_allow_html=True)

        csv_info = paired_df.to_csv(index=False)
        st.download_button("Download Info Experiment CSV", csv_info, "info_experiment.csv", "text/csv", key="dl_info")


# ═══════════════════════════════════════════════════════════════
# TAB 4: Combination Optimizer
# ═══════════════════════════════════════════════════════════════

with tab_optimizer:
    st.header("Combination Optimizer")
    st.caption(
        "Search agent combinations across all four roles to find the "
        "highest fill rates and lowest bullwhip effect."
    )

    # ----- configuration -----
    col_oc1, col_oc2 = st.columns(2)
    with col_oc1:
        opt_periods = st.slider("Periods", 10, 100, 52, key="opt_periods")
        opt_info = st.selectbox(
            "Information Sharing", ["none", "adjacent"], key="opt_info",
        )
        opt_seed = st.number_input("Random Seed", value=42, key="opt_seed")

    with col_oc2:
        opt_demand_type = st.selectbox(
            "Demand Pattern",
            ["Constant", "Step", "Seasonal", "Noisy", "Shock"],
            key="opt_demand",
        )
        opt_demand_params: dict = {}
        if opt_demand_type == "Constant":
            opt_demand_params["base"] = st.slider("Demand", 1, 20, 4, key="opt_d_base")
        elif opt_demand_type == "Step":
            opt_demand_params["initial"] = st.slider("Initial Demand", 1, 15, 4, key="opt_d_init")
            opt_demand_params["final"] = st.slider("Final Demand", 2, 25, 8, key="opt_d_final")
            opt_demand_params["step_period"] = st.slider("Step at Period", 1, 50, 10, key="opt_d_step")
        elif opt_demand_type == "Seasonal":
            opt_demand_params["base"] = st.slider("Base Demand", 1, 15, 4, key="opt_d_sb")
            opt_demand_params["amplitude"] = st.slider("Amplitude", 1, 10, 3, key="opt_d_amp")
            opt_demand_params["period"] = st.slider("Cycle", 4, 26, 12, key="opt_d_per")
        elif opt_demand_type == "Noisy":
            opt_demand_params["base"] = st.slider("Base Demand", 1, 15, 4, key="opt_d_nb")
            opt_demand_params["noise"] = st.slider("Noise Range (+/-)", 0, 8, 2, key="opt_d_noise")
            opt_demand_params["seed"] = int(st.number_input("Noise Seed", value=42, key="opt_d_nseed"))
        elif opt_demand_type == "Shock":
            opt_demand_params["base"] = st.slider("Base Demand", 1, 15, 4, key="opt_d_shb")
            opt_demand_params["shock_period"] = st.slider("Shock at Period", 1, 50, 15, key="opt_d_shp")
            opt_demand_params["shock_duration"] = st.slider("Shock Duration", 1, 10, 3, key="opt_d_shd")
            opt_demand_params["shock_magnitude"] = st.slider("Shock Magnitude", 5, 30, 12, key="opt_d_shm")

    st.divider()

    # ----- agent selection per role -----
    st.subheader("Agent Candidates")
    st.markdown(
        "Select which agents to include in the search. "
        "Fewer agents = faster search. "
        "Total combinations = (agents selected)^4."
    )

    # Sensible defaults — rational + moderate agents tend to perform better
    _defaults_opt = [
        k for k, v in AGENT_REGISTRY.items()
        if v["category"] in ("rational", "moderate")
    ]

    opt_agents = st.multiselect(
        "Agents to search",
        options=PROFILE_NAMES,
        default=_defaults_opt,
        format_func=lambda k: PROFILE_LABELS[k],
        key="opt_agents",
    )

    n_agents = len(opt_agents)
    n_combos = n_agents ** 4
    st.info(
        f"**{n_agents}** agents selected  \u2192  **{n_combos:,}** combinations to evaluate",
        icon="\u2139\ufe0f",
    )

    if n_combos > 50_000:
        st.warning(
            "More than 50,000 combinations — this may take several minutes. "
            "Consider narrowing the agent list.",
            icon="\u26a0\ufe0f",
        )

    # ----- scoring weights -----
    with st.expander("Scoring Weights"):
        st.markdown(
            "The optimizer ranks combinations by a **composite score**:  \n"
            "`Score = w_fill \u00d7 Fill Rate \u2212 w_bullwhip \u00d7 normalised_bullwhip \u2212 w_cost \u00d7 normalised_cost`  \n"
            "Higher is better. Adjust weights to emphasise what matters most."
        )
        w_fill = st.slider("Fill Rate Weight", 0.0, 10.0, 5.0, 0.5, key="w_fill")
        w_bw = st.slider("Bullwhip Penalty Weight", 0.0, 10.0, 3.0, 0.5, key="w_bw")
        w_cost = st.slider("Cost Penalty Weight", 0.0, 10.0, 2.0, 0.5, key="w_cost")

    top_n = st.slider("Show top N results", 5, 50, 20, key="opt_topn")

    # ----- run -----
    if st.button("Run Optimizer", type="primary", key="run_opt"):
        if n_agents < 2:
            st.error("Select at least 2 agents to search.")
        else:
            demand_fn = build_demand_fn(opt_demand_type, opt_demand_params)
            config = SimulationConfig(
                periods=opt_periods,
                information_sharing=opt_info,
                random_seed=int(opt_seed),
            )

            # Pre-build agent instances (keyed by profile) — reuse across combos
            agent_cache: dict = {}
            for pk in opt_agents:
                default_params = {k: v[3] for k, v in AGENT_REGISTRY[pk]["params"].items()}
                agent_cache[pk] = lambda _pk=pk, _dp=default_params: create_agent(_pk, _dp)

            combos = list(itertools.product(opt_agents, repeat=4))
            results_rows = []
            progress = st.progress(0, text="Evaluating combinations...")
            t0 = time.time()

            for idx, combo in enumerate(combos):
                agents = {
                    role: agent_cache[combo[i]]()
                    for i, role in enumerate(ROLES)
                }
                runner = SimulationRunner(agents, demand_fn, config)
                df_run = runner.run()

                bw = compute_bullwhip(df_run)
                sl = compute_service_level(df_run)
                sys_cost = compute_system_cost(df_run)

                results_rows.append({
                    "retailer": PROFILE_LABELS[combo[0]],
                    "wholesaler": PROFILE_LABELS[combo[1]],
                    "distributor": PROFILE_LABELS[combo[2]],
                    "factory": PROFILE_LABELS[combo[3]],
                    "retailer_key": combo[0],
                    "wholesaler_key": combo[1],
                    "distributor_key": combo[2],
                    "factory_key": combo[3],
                    "avg_fill_rate": sl["fill_rate"].mean(),
                    "min_fill_rate": sl["fill_rate"].min(),
                    "avg_bullwhip": bw["bullwhip_factor"].mean(),
                    "max_bullwhip": bw["bullwhip_factor"].max(),
                    "system_cost": sys_cost,
                })

                if (idx + 1) % max(1, len(combos) // 100) == 0 or idx == len(combos) - 1:
                    elapsed = time.time() - t0
                    pct = (idx + 1) / len(combos)
                    eta = (elapsed / pct - elapsed) if pct > 0 else 0
                    progress.progress(
                        pct,
                        text=f"Evaluated {idx+1:,}/{len(combos):,} "
                             f"({pct:.0%}) — ETA {eta:.0f}s",
                    )

            progress.empty()
            elapsed_total = time.time() - t0
            st.success(f"Evaluated **{len(combos):,}** combinations in **{elapsed_total:.1f}s**")

            opt_df = pd.DataFrame(results_rows)

            # --- Composite score ---
            # Normalise bullwhip and cost to [0,1]
            bw_min, bw_max = opt_df["avg_bullwhip"].min(), opt_df["avg_bullwhip"].max()
            cost_min, cost_max = opt_df["system_cost"].min(), opt_df["system_cost"].max()
            bw_range = bw_max - bw_min if bw_max != bw_min else 1.0
            cost_range = cost_max - cost_min if cost_max != cost_min else 1.0

            opt_df["norm_bullwhip"] = (opt_df["avg_bullwhip"] - bw_min) / bw_range
            opt_df["norm_cost"] = (opt_df["system_cost"] - cost_min) / cost_range
            opt_df["score"] = (
                w_fill * opt_df["avg_fill_rate"]
                - w_bw * opt_df["norm_bullwhip"]
                - w_cost * opt_df["norm_cost"]
            )
            opt_df = opt_df.sort_values("score", ascending=False).reset_index(drop=True)
            opt_df.index = opt_df.index + 1  # 1-based rank
            opt_df.index.name = "rank"

            st.session_state["opt_df"] = opt_df
            st.session_state["opt_top_n"] = top_n

    # ----- display results -----
    if "opt_df" in st.session_state:
        opt_df = st.session_state["opt_df"]
        show_n = st.session_state.get("opt_top_n", 20)
        top = opt_df.head(show_n)

        st.subheader(f"Top {show_n} Combinations")

        # Best combo callout
        best = opt_df.iloc[0]
        st.success(
            f"**Best combination** (Score {best['score']:.3f})  \n"
            f"Retailer: {best['retailer']}  |  "
            f"Wholesaler: {best['wholesaler']}  |  "
            f"Distributor: {best['distributor']}  |  "
            f"Factory: {best['factory']}  \n"
            f"Fill Rate: {best['avg_fill_rate']:.0%}  |  "
            f"Bullwhip: {best['avg_bullwhip']:.1f}x  |  "
            f"Cost: \u20b9{best['system_cost']:,.0f}"
        )

        # KPI cards for best
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Fill Rate (best)", f"{best['avg_fill_rate']:.0%}")
        c2.metric("Min Role Fill Rate", f"{best['min_fill_rate']:.0%}")
        c3.metric("Avg Bullwhip", f"{best['avg_bullwhip']:.1f}x")
        c4.metric("System Cost", f"\u20b9{best['system_cost']:,.0f}")

        # Ranking table
        display_cols = [
            "retailer", "wholesaler", "distributor", "factory",
            "avg_fill_rate", "min_fill_rate", "avg_bullwhip",
            "max_bullwhip", "system_cost", "score",
        ]
        st.markdown(df_to_markdown(top[display_cols].reset_index()), unsafe_allow_html=True)

        # ----- Scatter: fill rate vs bullwhip (Pareto front) -----
        st.subheader("Fill Rate vs Bullwhip — All Combinations")

        # Compute Pareto frontier (fill rate ↑, bullwhip ↓)
        # Sort by fill rate descending, then scan for non-dominated points
        _sorted = opt_df.sort_values("avg_fill_rate", ascending=False)
        pareto_idx = []
        best_bw = float("inf")
        for i, row in _sorted.iterrows():
            if row["avg_bullwhip"] <= best_bw:
                pareto_idx.append(i)
                best_bw = row["avg_bullwhip"]
        opt_df["pareto"] = False
        opt_df.loc[pareto_idx, "pareto"] = True
        pareto_points = opt_df[opt_df["pareto"]].sort_values("avg_fill_rate")

        fig_pareto = go.Figure()

        # All combos as faded scatter
        fig_pareto.add_trace(go.Scatter(
            x=opt_df["avg_fill_rate"],
            y=opt_df["avg_bullwhip"],
            mode="markers",
            marker=dict(size=4, color="#ede4d5", opacity=0.5),
            name="All combinations",
            hovertemplate=(
                "Fill Rate: %{x:.0%}<br>Bullwhip: %{y:.1f}x<br>"
                "<extra></extra>"
            ),
        ))

        # Top-N highlighted
        fig_pareto.add_trace(go.Scatter(
            x=top["avg_fill_rate"],
            y=top["avg_bullwhip"],
            mode="markers",
            marker=dict(size=7, color="#1a5c4c", opacity=0.8),
            name=f"Top {show_n}",
            text=[
                f"R:{r}<br>W:{w}<br>D:{d}<br>F:{f}"
                for r, w, d, f in zip(top["retailer"], top["wholesaler"],
                                       top["distributor"], top["factory"])
            ],
            hovertemplate=(
                "%{text}<br>Fill Rate: %{x:.0%}<br>Bullwhip: %{y:.1f}x"
                "<extra></extra>"
            ),
        ))

        # Pareto frontier line
        if len(pareto_points) > 0:
            fig_pareto.add_trace(go.Scatter(
                x=pareto_points["avg_fill_rate"],
                y=pareto_points["avg_bullwhip"],
                mode="lines+markers",
                marker=dict(size=9, color="#c2452d", symbol="diamond"),
                line=dict(color="#c2452d", dash="dash", width=1.5),
                name="Pareto frontier",
                text=[
                    f"R:{r}<br>W:{w}<br>D:{d}<br>F:{f}"
                    for r, w, d, f in zip(
                        pareto_points["retailer"], pareto_points["wholesaler"],
                        pareto_points["distributor"], pareto_points["factory"],
                    )
                ],
                hovertemplate=(
                    "%{text}<br>Fill Rate: %{x:.0%}<br>Bullwhip: %{y:.1f}x"
                    "<extra></extra>"
                ),
            ))

        fig_pareto.update_layout(
            xaxis_title="Average Fill Rate",
            yaxis_title="Average Bullwhip Factor",
            height=500,
            margin=dict(t=30, b=40),
            **PLOTLY_LAYOUT,
        )
        st.plotly_chart(fig_pareto, width="stretch")

        # ----- Which agents appear most in top combos, by role -----
        st.subheader("Best Agents by Role (frequency in top combos)")

        freq_data = []
        for role in ROLES:
            counts = top[role].value_counts()
            for agent_label, count in counts.items():
                freq_data.append({
                    "role": role,
                    "agent": agent_label,
                    "count": count,
                    "pct": count / len(top),
                })
        freq_df = pd.DataFrame(freq_data)

        if not freq_df.empty:
            fig_freq = px.bar(
                freq_df, x="role", y="count", color="agent",
                title=f"Agent Frequency in Top {show_n} Combinations",
                barmode="stack",
                color_discrete_sequence=EARTH_PALETTE * 3,
                labels={"count": "Appearances", "role": "Role", "agent": "Agent"},
            )
            fig_freq.update_layout(
                height=400, xaxis_tickangle=0, **PLOTLY_LAYOUT,
            )
            st.plotly_chart(fig_freq, width="stretch")

            # Per-role best agent summary
            st.markdown("**Most frequent agent per role in top combinations:**")
            role_best = []
            for role in ROLES:
                role_freq = freq_df[freq_df["role"] == role].sort_values("count", ascending=False)
                if not role_freq.empty:
                    best_agent = role_freq.iloc[0]
                    role_best.append({
                        "Role": role.title(),
                        "Best Agent": best_agent["agent"],
                        f"Appearances (of {show_n})": int(best_agent["count"]),
                        "Share": f"{best_agent['pct']:.0%}",
                    })
            st.markdown(
                df_to_markdown(pd.DataFrame(role_best)),
                unsafe_allow_html=True,
            )

        # ----- Pareto frontier table -----
        with st.expander(f"Pareto-Optimal Combinations ({len(pareto_points)})"):
            st.markdown(
                "These combinations are **not dominated** by any other — "
                "no other combo has both higher fill rate *and* lower bullwhip."
            )
            st.markdown(
                df_to_markdown(pareto_points[display_cols].reset_index()),
                unsafe_allow_html=True,
            )

        # ----- Summary statistics -----
        with st.expander("Distribution Summary"):
            st.markdown(f"**Total combinations evaluated:** {len(opt_df):,}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Median Fill Rate", f"{opt_df['avg_fill_rate'].median():.0%}")
            c2.metric("Median Bullwhip", f"{opt_df['avg_bullwhip'].median():.1f}x")
            c3.metric("Median Cost", f"\u20b9{opt_df['system_cost'].median():,.0f}")

            # Fill rate distribution
            fig_hist = px.histogram(
                opt_df, x="avg_fill_rate", nbins=30,
                title="Fill Rate Distribution Across All Combinations",
                color_discrete_sequence=["#1a5c4c"],
                labels={"avg_fill_rate": "Average Fill Rate", "count": "Combinations"},
            )
            fig_hist.update_layout(height=300, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_hist, width="stretch")

        # ----- Download -----
        csv_opt = opt_df[display_cols + ["pareto"]].reset_index().to_csv(index=False)
        st.download_button(
            "Download All Results CSV", csv_opt,
            "combination_optimizer.csv", "text/csv", key="dl_opt",
        )
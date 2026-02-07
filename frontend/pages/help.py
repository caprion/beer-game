import streamlit as st

st.set_page_config(page_title="Help - Beer Game Simulation", layout="wide")

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

/* ── Captions & secondary text ── */
[data-testid="stCaptionContainer"] { color: #6b5443; }

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #ffffff;
    border: 1px solid #ede4d5;
    border-radius: 8px;
}
[data-testid="stExpander"]:hover {
    box-shadow: 0 2px 8px rgba(61, 43, 31, 0.06);
}

/* ── Dividers ── */
hr { border-color: #ede4d5; }

/* ── Code blocks in docs ── */
code {
    font-family: 'IBM Plex Mono', Consolas, monospace;
    font-size: 0.9em;
    background: #f5efe5;
    padding: 2px 6px;
    border-radius: 4px;
}
</style>
""")

st.title("Agent Profiles & Concepts Help")

# ──────────────────────────────────────────────────────────────
# Rational / Smart Agents
# ──────────────────────────────────────────────────────────────

st.header("Rational / Smart Agents")
st.caption("Agents designed to minimize bullwhip and total cost using analytical strategies.")

with st.expander("Passive Pipeline", expanded=False):
    st.markdown("""
    **Mindset:** Keep it simple — maintain a target inventory level.

    **Strategy:** Orders enough to close the gap between current inventory (minus backlog) and target.

    **Impact:** Low amplification but not adaptive to demand changes.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    """)

with st.expander("Stabilizer (System Thinker)", expanded=False):
    st.markdown("""
    **Mindset:** The supply chain is a system of delays — smooth inputs, smooth outputs.

    **Strategy:** Uses exponential smoothing on incoming demand plus rate-limiting on order changes.
    When neighbor info is available (adjacent mode), adjusts orders based on upstream/downstream state.

    **Impact:** Strong bullwhip dampener. Benefits significantly from information sharing.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    - **smoothing_alpha:** Exponential smoothing weight for demand (default: 0.3)
    - **max_correction_per_period:** Maximum order change per period (default: 4)
    """)

with st.expander("Bayesian Updater", expanded=False):
    st.markdown("""
    **Mindset:** Start with a prior belief about demand, update with evidence.

    **Strategy:** Maintains a Bayesian estimate of true demand using a normal prior that updates
    with each observation. Orders to meet expected demand + cover gaps.

    **Impact:** Converges to true demand over time. Resistant to noise.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    - **prior_demand:** Initial demand belief (default: 4.0)
    - **prior_strength:** How strongly to weight the prior vs data (default: 5)
    """)

with st.expander("Inverter (Munger's Inversion)", expanded=False):
    st.markdown("""
    **Mindset:** "Invert, always invert." — Avoid catastrophic outcomes first.

    **Strategy:** Identifies the two worst states (massive backlog, massive overstock) and
    explicitly steers away from both. Rate-limits order changes to avoid amplification.

    **Impact:** Very low bullwhip. Sacrifices peak performance for downside protection.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    - **max_change_rate:** Maximum period-over-period order change (default: 3)
    """)

with st.expander("Antifragile Adapter", expanded=False):
    st.markdown("""
    **Mindset:** Learn from prediction errors — volatility is information.

    **Strategy:** Tracks prediction errors and grows a safety buffer when errors are large,
    shrinks it when predictions are accurate. Uses neighbor info to detect upstream stress.

    **Impact:** Gets *better* under volatility. Strong info-sharing beneficiary.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    - **initial_buffer:** Starting safety buffer (default: 1.0)
    - **learning_rate:** How fast buffer adapts to errors (default: 0.1)
    - **max_buffer:** Maximum allowed buffer size (default: 6.0)
    """)

with st.expander("Info-Aware Agent", expanded=False):
    st.markdown("""
    **Mindset:** Purpose-built to exploit information sharing.

    **Strategy:** When neighbor state is available, blends own demand estimate with upstream/
    downstream signals. Adjusts inventory targets based on neighbor stress indicators.

    **Impact:** Maximum benefit from `adjacent` information sharing mode. Minimal bullwhip.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    - **smoothing_alpha:** Demand smoothing weight (default: 0.3)
    - **info_weight:** How much to weight neighbor info vs own estimate (default: 0.5)
    """)

# ──────────────────────────────────────────────────────────────
# Moderate Agents
# ──────────────────────────────────────────────────────────────

st.header("Moderate Agents")
st.caption("Agents that balance simplicity with some analytical approach.")

with st.expander("Production Smoother", expanded=False):
    st.markdown("""
    **Mindset:** Smooth production by averaging recent demand, clamped to capacity limits.

    **Strategy:** Maintains a rolling window of recent demand and orders the average, bounded
    by min/max production constraints.

    **Impact:** Good cost control. Can lag behind large demand shifts.

    **Parameters:**
    - **window_size:** Rolling average window (default: 5)
    - **min_production:** Floor on order quantity (default: 2)
    - **max_production:** Ceiling on order quantity (default: 15)
    """)

with st.expander("Rational Analyst (ignores pipeline)", expanded=False):
    st.markdown("""
    **Mindset:** Analyze demand rationally but *ignore* in-transit pipeline inventory.

    **Strategy:** Smooths demand estimates and orders to close the gap vs target inventory,
    but doesn't account for units already in transit (leading to double-ordering).

    **Impact:** Moderate bullwhip — analytical but with a structural blind spot.

    **Parameters:**
    - **target_inventory:** Desired inventory level (default: 12)
    - **smoothing:** Demand smoothing weight (default: 0.0 = no smoothing)
    """)

# ──────────────────────────────────────────────────────────────
# Noise / Baseline
# ──────────────────────────────────────────────────────────────

st.header("Noise / Baseline Agents")

with st.expander("Random Baseline", expanded=False):
    st.markdown("""
    **Mindset:** Roll the dice.

    **Strategy:** Orders a uniformly random amount each period, ignoring all state.

    **Impact:** Pure noise generator. Useful as a baseline for comparison.

    **Parameters:**
    - **low:** Minimum random order (default: 0)
    - **high:** Maximum random order (default: 10)
    - **seed:** Random seed for reproducibility
    """)

# ──────────────────────────────────────────────────────────────
# Behavioral / Bullwhip-Amplifying Agents
# ──────────────────────────────────────────────────────────────

st.header("Behavioral / Bullwhip-Amplifying Agents")
st.caption("Agents modeled on real human biases. Strong bullwhip amplifiers.")

with st.expander("Aggressive Growth-Hacker", expanded=False):
    st.markdown("""
    **Mindset:** Stock-outs are catastrophic. Overstocking is manageable.

    **Strategy:** Amplifies demand by ordering more than needed. Maintains large safety buffers.
    Panics when inventory drops below threshold.

    **Impact:** Strongly amplifies bulwhip. Turns small fluctuations into major upstream surges.

    **Parameters:**
    - **amplification_factor:** Multiplier on incoming demand (default: 1.5)
    - **safety_buffer:** Extra units as safety stock (default: 3)
    - **panic_threshold:** Inventory triggering panic orders (default: 2)
    """)

with st.expander("Conservative Custodian", expanded=False):
    st.markdown("""
    **Mindset:** Keep inventory minimal. Demand spikes are probably anomalies.

    **Strategy:** Consistently orders less than received demand. BUT eventually panics when
    backlog gets too large, placing sudden large orders.

    **Impact:** Initially dampens demand, then creates sharp spikes. Time-delayed bullwhip.

    **Parameters:**
    - **conservation_factor:** Fraction of demand to order (default: 0.8)
    - **max_inventory_target:** Desired inventory ceiling (default: 8)
    - **panic_backlog_threshold:** Backlog triggering panic (default: 5)
    """)

with st.expander("Myopic Firefighter", expanded=False):
    st.markdown("""
    **Mindset:** Everything is urgent. React to whatever crisis is in front of me.

    **Strategy:** Swings between zero orders (when overstocked) and panic orders (when short).
    Random emotional volatility adds unpredictability.

    **Impact:** Maximum chaos. Makes demand patterns untraceable upstream.

    **Parameters:**
    - **panic_inventory_threshold:** Low-inventory panic trigger (default: 3)
    - **panic_backlog_threshold:** Backlog panic trigger (default: 2)
    - **overstock_threshold:** Inventory halting orders (default: 15)
    - **emotional_volatility:** Random noise factor 0-1 (default: 0.3)
    - **seed:** Random seed for reproducibility
    """)

with st.expander("Signal Chaser", expanded=False):
    st.markdown("""
    **Mindset:** Every demand change is a meaningful trend to exploit.

    **Strategy:** Detects "trends" in recent demand history and extrapolates them aggressively.
    Overreacts to random fluctuations.

    **Impact:** Primary bullwhip initiator. Misinterprets noise as signal.

    **Parameters:**
    - **trend_sensitivity:** Reaction strength to detected trends (default: 2.0)
    - **momentum_window:** Lookback periods for trend detection (default: 3)
    - **extrapolation_factor:** Forward projection multiplier (default: 1.8)
    - **min_trend_threshold:** Minimum change to flag as trend (default: 1)
    """)

# ──────────────────────────────────────────────────────────────
# Concepts
# ──────────────────────────────────────────────────────────────

st.divider()
st.header("Key Concepts")

with st.expander("Bullwhip Effect"):
    st.markdown("""
    The **bullwhip effect** is the amplification of order variability as you move upstream
    in a supply chain. Small fluctuations at the retail level become large swings at the
    factory level.

    **Measured as:** `Var(orders) / Var(incoming_demand)` per role.
    A value > 1.0 means the role is *amplifying* demand variance.
    """)

with st.expander("Information Sharing Modes"):
    st.markdown("""
    - **none (classic):** Each role only sees its own inventory, backlog, and incoming demand.
      This is the traditional Beer Game setup and the root cause of information asymmetry.

    - **adjacent:** Each role can see its immediate upstream and downstream partner's
      `inventory`, `backlog`, and `last_placed_order`. This simulates real-world
      information sharing (e.g., vendor-managed inventory, EDI).

    Smart agents (Stabilizer, Antifragile, Info-Aware) actively use this data.
    Behavioral agents ignore it — they don't look at the extra fields.
    """)

with st.expander("Demand Patterns"):
    st.markdown("""
    - **Constant:** Steady demand every period (baseline)
    - **Step:** Demand jumps from one level to another at a specific period
    - **Seasonal:** Demand follows a sinusoidal cycle
    - **Noisy:** Constant base demand with random uniform noise
    - **Shock:** Normal demand with a sudden temporary spike
    """)

with st.expander("KPI Definitions"):
    st.markdown("""
    - **System Total Cost:** Sum of holding + backlog costs across all roles and periods
    - **Bullwhip Factor:** `Var(orders) / Var(incoming_demand)` — amplification ratio
    - **Fill Rate:** Fraction of periods where demand was fully met without backlog
    - **Order Oscillation:** Mean absolute period-over-period order change (stability indicator)
    - **Avg Inventory / Avg Backlog:** Mean levels across all periods
    """)
import streamlit as st

st.set_page_config(page_title="Help - Beer Game Simulation", page_icon="❓")

st.title("Agent Profiles Help")

st.header("Aggressive Growth-Hacker")
st.markdown("""
**Mindset:** Avoid stock-outs at all costs. Overstocking is manageable; running out is catastrophic.

**Strategy:** Responds to any demand increase by ordering even more than needed, creating a large safety buffer.

**Impact:** Strongly amplifies the bullwhip effect by turning small demand fluctuations into major upstream order surges.
""")

st.subheader("Parameters")
st.markdown("""
- **amplification_factor:** How much to amplify demand increases (>1.0)
- **safety_buffer:** Additional units to order as safety stock
- **panic_threshold:** Inventory level that triggers panic ordering
""")

st.header("Conservative Custodian")
st.markdown("""
**Mindset:** Keep inventory as low as possible, even tolerating minor backlogs.

**Strategy:** Consistently orders less than received, dismissing demand spikes as anomalies.

**Impact:** Initially dampens demand spikes but eventually places large "panic orders" when shortages occur.
""")

st.subheader("Parameters")
st.markdown("""
- **conservation_factor:** Fraction of demand to order (< 1.0 for conservative approach)
- **max_inventory_target:** Maximum desired inventory level
- **panic_backlog_threshold:** Backlog level that triggers panic ordering
""")

st.header("Myopic Firefighter")
st.markdown("""
**Mindset:** Feels beset by unreliable partners and unpredictable demand and acts reactively.

**Strategy:** Swings between zero orders and large, sudden orders based on immediate needs.

**Impact:** Introduces volatility and unpredictability, making demand patterns impossible to trace upstream.
""")

st.subheader("Parameters")
st.markdown("""
- **panic_inventory_threshold:** Inventory level that triggers panic
- **panic_backlog_threshold:** Backlog level that triggers panic
- **overstock_threshold:** Inventory level that triggers zero orders
- **emotional_volatility:** Random factor for emotional swings (0-1)
- **seed:** Random seed for reproducibility
""")

st.header("Passive Pipeline")
st.markdown("""
This agent follows a simple pipeline strategy. It tries to maintain a target inventory level.
""")

st.subheader("Parameters")
st.markdown("""
- **target_inventory:** The desired inventory level.
""")

st.header("Random Baseline")
st.markdown("""
This agent orders a random amount of beer in each period.
""")

st.subheader("Parameters")
st.markdown("""
- **low:** The lower bound of the random order quantity.
- **high:** The upper bound of the random order quantity.
- **seed:** Random seed for reproducibility.
""")

st.header("Signal Chaser")
st.markdown("""
**Mindset:** Treats every change in sales as a significant trend, aiming to capitalize quickly.

**Strategy:** Overreacts to random fluctuations, causing substantial demand amplification upstream.

**Impact:** Strongly initiates the bullwhip effect by misinterpreting natural sales variation.
""")

st.subheader("Parameters")
st.markdown("""
- **trend_sensitivity:** How strongly to react to detected trends
- **momentum_window:** Number of periods to analyze for trends
- **extrapolation_factor:** How far to extrapolate trends into the future
- **min_trend_threshold:** Minimum change to consider a trend
""")
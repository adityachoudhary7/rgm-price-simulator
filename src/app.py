import streamlit as st
from simulator import PriceSimulator

# 1. Page Configuration
st.set_page_config(page_title="RGM Scenario Simulator", layout="wide")

st.title("Price Elasticity & Profit Optimization Dashboard")
st.markdown("Simulate pricing strategies using the log-log econometric elasticity model.")
st.markdown("""
### 💡 How to use this tool:
1. **Simulate Scenarios:** Use the Strategy Levers on the left to adjust the Proposed Price and COGS.
2. **Watch the Volume Trap:** Notice how dropping the price might increase top-line Revenue, but frequently destroys bottom-line Gross Profit. 
3. **The Engine:** Volume changes are dynamically predicted using an own-price elasticity coefficient of **-1.87**. This parameter was extracted from historical retail POS data using a Log-Log OLS econometric regression model.
---
""")
# 2. Sidebar for User Inputs
st.sidebar.header("Strategy Levers")
new_price = st.sidebar.slider(
    "Proposed Price (₹)", 
    min_value=70.0, 
    max_value=130.0, 
    value=105.0, 
    step=1.0
)
cogs = st.sidebar.number_input("Cost of Goods Sold (COGS) (₹)", value=58.0)

# 3. Connect to the Mathematical Engine
# We initialize the simulator with the updated COGS, then run the scenario
sim = PriceSimulator(cogs=cogs)
result = sim.simulate_scenario(new_price)

# 4. Build the Executive UI
st.subheader("Financial Impact (vs Baseline)")

# Create columns for KPI cards
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Predicted Volume**\n\n{result['Predicted Volume']}")

with col2:
    st.success(f"**Projected Revenue**\n\n{result['Projected Revenue']}")

with col3:
    st.warning(f"**Projected Gross Profit**\n\n{result['Projected Gross Profit']}")

# Margin prominently displayed below
st.metric(label="New Gross Margin %", value=result["Gross Margin %"])

st.markdown("---")
st.markdown("*Note: Baseline Price is ₹100.00. Elasticity coefficient (Own-Price): -1.87*")


st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: grey; font-size: 14px;'>"
    "Engineered by <b>Aditya Choudhary</b> | Revenue Growth Management Portfolio"
    "</div>", 
    unsafe_allow_html=True
)
import pandas as pd

class PriceSimulator:
    def __init__(self, base_price=100.0, base_volume=12000, cogs=58.0, own_elasticity=-1.8713):
        """
        Initializes the simulator with the base baseline metrics and the exact 
        elasticity coefficient we extracted from our OLS regression model.
        """
        self.base_price = base_price
        self.base_volume = base_volume
        self.cogs = cogs
        self.elasticity = own_elasticity
        
        # Calculate Base Financials
        self.base_revenue = self.base_price * self.base_volume
        self.base_profit = self.base_volume * (self.base_price - self.cogs)
        self.base_margin_pct = (self.base_profit / self.base_revenue) * 100

    def simulate_scenario(self, new_price: float) -> dict:
        """
        Calculates new volume and financials based on a proposed price change.
        Uses the constant elasticity formula: Q_new = Q_base * (P_new / P_base)^E
        """
        # Calculate how much the price changed relative to the base
        price_ratio = new_price / self.base_price
        
        # Predict new volume using our OLS elasticity coefficient
        new_volume = int(self.base_volume * (price_ratio ** self.elasticity))
        
        # Calculate new commercial metrics
        new_revenue = new_volume * new_price
        new_profit = new_volume * (new_price - self.cogs)
        new_margin_pct = (new_profit / new_revenue) * 100 if new_revenue > 0 else 0
        
        # Calculate deltas (differences from baseline)
        vol_delta = new_volume - self.base_volume
        rev_delta = new_revenue - self.base_revenue
        profit_delta = new_profit - self.base_profit
        
        return {
            "Proposed Price": f"₹{new_price:.2f}",
            "Predicted Volume": f"{new_volume:,} units (Change: {vol_delta:,})",
            "Projected Revenue": f"₹{new_revenue:,.2f} (Change: ₹{rev_delta:,.2f})",
            "Projected Gross Profit": f"₹{new_profit:,.2f} (Change: ₹{profit_delta:,.2f})",
            "Gross Margin %": f"{new_margin_pct:.1f}%"
        }

if __name__ == "__main__":
    # Initialize the simulator engine
    sim = PriceSimulator()
    
    print("="*55)
    print("SCENARIO 1: PRICE DECREASE (₹95.00)")
    print("="*55)
    discount_result = sim.simulate_scenario(new_price=95.00)
    for key, value in discount_result.items():
        print(f"{key}: {value}")
        
    print("\n" + "="*55)
    print("SCENARIO 2: PRICE INCREASE (₹105.00)")
    print("="*55)
    premium_result = sim.simulate_scenario(new_price=105.00)
    for key, value in premium_result.items():
        print(f"{key}: {value}")
    print("="*55)
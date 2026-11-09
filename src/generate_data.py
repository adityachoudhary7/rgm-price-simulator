import os
import numpy as np
import pandas as pd

def generate_rgm_pos_data(weeks: int = 104, seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic 2-year weekly POS dataset for 3 competing SKUs
    with embedded own-price elasticity, cross-price cannibalization,
    feature/display promotions, and seasonality.
    """
    np.random.seed(seed)
    
    # Time index: 2 years of weekly data
    dates = pd.date_range(start="2024-11-04", periods=weeks, freq="W-MON")
    week_num = np.arange(1, weeks + 1)
    
    # Seasonality: Sine wave peaking in summer weeks (+15% peak-to-trough)
    seasonality_index = 1.0 + 0.15 * np.sin(2 * np.pi * (week_num - 10) / 52)
    
    # Base prices and unit COGS (in INR)
    base_p_a, cogs_a = 100.0, 58.0
    base_p_b, cogs_b = 125.0, 72.0
    base_p_c, cogs_c = 80.0, 48.0
    
    # Generate promotional flags (binary: 1 = feature/display promo, 0 = regular)
    promo_a = np.random.binomial(1, 0.22, weeks)
    promo_b = np.random.binomial(1, 0.18, weeks)
    promo_c = np.random.binomial(1, 0.25, weeks)
    
    # Generate weekly shelf prices (regular noise +/- 4%, deeper drops during promos)
    price_a = base_p_a * np.random.uniform(0.97, 1.05, weeks) * (1 - promo_a * np.random.uniform(0.08, 0.18, weeks))
    price_b = base_p_b * np.random.uniform(0.97, 1.05, weeks) * (1 - promo_b * np.random.uniform(0.08, 0.15, weeks))
    price_c = base_p_c * np.random.uniform(0.97, 1.04, weeks) * (1 - promo_c * np.random.uniform(0.05, 0.12, weeks))
    
    price_a = np.round(price_a, 2)
    price_b = np.round(price_b, 2)
    price_c = np.round(price_c, 2)
    
    # True Elasticity Matrix [Row i = Volume of SKU i, Col j = Price of SKU j]
    # Diagonal = Own-Price Elasticity (negative)
    # Off-diagonal = Cross-Price Elasticity (positive for substitutes)
    E = np.array([
        [-1.85,  0.45,  0.25],  # Brand A (Target Brand)
        [ 0.35, -1.40,  0.10],  # Brand B (Premium Competitor)
        [ 0.50,  0.15, -2.20]   # Brand C (Economy Private Label)
    ])
    
    base_vols = np.array([12000, 7500, 16000])
    promo_lifts = np.array([0.14, 0.12, 0.18]) # Incremental display lift independent of price
    
    # Relative price ratios
    p_ratio_a = price_a / base_p_a
    p_ratio_b = price_b / base_p_b
    p_ratio_c = price_c / base_p_c
    
    # Random log-normal noise (unexplained retail variance)
    noise_a = np.random.normal(0, 0.035, weeks)
    noise_b = np.random.normal(0, 0.035, weeks)
    noise_c = np.random.normal(0, 0.035, weeks)
    
    # Multiplicative constant-elasticity demand equation:
    # Q = Q_base * (P_a/P_base_a)^e_11 * (P_b/P_base_b)^e_12 * (P_c/P_base_c)^e_13 * Seasonality * exp(Promo + Noise)
    vol_a = (
        base_vols[0]
        * (p_ratio_a ** E[0, 0])
        * (p_ratio_b ** E[0, 1])
        * (p_ratio_c ** E[0, 2])
        * seasonality_index
        * np.exp(promo_lifts[0] * promo_a + noise_a)
    )
    
    vol_b = (
        base_vols[1]
        * (p_ratio_a ** E[1, 0])
        * (p_ratio_b ** E[1, 1])
        * (p_ratio_c ** E[1, 2])
        * seasonality_index
        * np.exp(promo_lifts[1] * promo_b + noise_b)
    )
    
    vol_c = (
        base_vols[2]
        * (p_ratio_a ** E[2, 0])
        * (p_ratio_b ** E[2, 1])
        * (p_ratio_c ** E[2, 2])
        * seasonality_index
        * np.exp(promo_lifts[2] * promo_c + noise_c)
    )
    
    df = pd.DataFrame({
        "date": dates,
        "week_num": week_num,
        "seasonality_index": np.round(seasonality_index, 4),
        "price_brand_a": price_a,
        "price_comp_b": price_b,
        "price_comp_c": price_c,
        "promo_flag_a": promo_a,
        "promo_flag_b": promo_b,
        "promo_flag_c": promo_c,
        "vol_brand_a": np.round(vol_a).astype(int),
        "vol_comp_b": np.round(vol_b).astype(int),
        "vol_comp_c": np.round(vol_c).astype(int),
        "cogs_brand_a": cogs_a,
        "cogs_comp_b": cogs_b,
        "cogs_comp_c": cogs_c,
        "base_price_a": base_p_a,
        "base_price_b": base_p_b,
        "base_price_c": base_p_c
    })
    
    # Calculate commercial metrics for Brand A
    df["rev_brand_a"] = np.round(df["vol_brand_a"] * df["price_brand_a"], 2)
    df["gross_profit_a"] = np.round(df["vol_brand_a"] * (df["price_brand_a"] - df["cogs_brand_a"]), 2)
    df["margin_pct_a"] = np.round((df["gross_profit_a"] / df["rev_brand_a"]) * 100, 2)
    
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    pos_df = generate_rgm_pos_data()
    output_path = os.path.join("data", "synthetic_pos_data.csv")
    pos_df.to_csv(output_path, index=False)
    
    print(f"Dataset generated successfully: {output_path}")
    print(f"Shape: {pos_df.shape[0]} rows, {pos_df.shape[1]} columns\n")
    print(pos_df[["date", "price_brand_a", "vol_brand_a", "rev_brand_a", "margin_pct_a"]].head())
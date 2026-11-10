import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
print("started")
def run_elasticity_regression(data_path: str = "data/synthetic_pos_data.csv"):
    """
    Loads POS data, applies log-log transformation, 
    and estimates price elasticity coefficients using OLS regression.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_data.py first.")
        
    df = pd.read_csv(data_path)
    
    # 1. Log-Log Transformation
    # We take the natural logarithm (ln) of continuous variables.
    # In a log-log model, the resulting coefficients represent exact elasticities.
    df["ln_vol_a"] = np.log(df["vol_brand_a"])
    df["ln_price_a"] = np.log(df["price_brand_a"])
    df["ln_price_b"] = np.log(df["price_comp_b"])
    df["ln_price_c"] = np.log(df["price_comp_c"])
    df["ln_seasonality"] = np.log(df["seasonality_index"])
    
    # 2. Define the Independent Variables (X) and Dependent Variable (y)
    # We control for competitor prices, promotions, and seasonality so they don't skew our own-price elasticity.
    X = df[["ln_price_a", "ln_price_b", "ln_price_c", "promo_flag_a", "ln_seasonality"]]
    X = sm.add_constant(X) # Adds the intercept term required for OLS
    
    y = df["ln_vol_a"]
    
    # 3. Fit the Ordinary Least Squares (OLS) model
    model = sm.OLS(y, X).fit()
    
    # 4. Output the Executive Summary
    print("="*65)
    print("ECONOMETRIC PRICE ELASTICITY MODEL RESULTS (BRAND A)")
    print("="*65)
    print(model.summary().tables[1])
    print(f"\nModel R-squared: {model.rsquared:.4f}")
    print("="*65)
    
    return model

if __name__ == "__main__":
    # Suppress scientific notation in pandas for cleaner terminal output
    pd.set_option('display.float_format', lambda x: '%.4f' % x)
    
    # Run the engine
    run_elasticity_regression()
"""
Data Simulation Module for Difference-in-Differences Analysis

Generates synthetic member-month and market-month level healthcare cost data
for a two-market, three-year observational study with an intervention in one market.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def set_seed(seed=42):
    """Set random seed for reproducibility."""
    np.random.seed(seed)


def generate_member_month_data(
    n_members_per_market=1000,
    baseline_pmpm=500,
    market_effect_treated=15,
    time_trend_per_month=1.5,
    treatment_effect=-35,
    risk_score_effect=80,
    noise_std=50,
    seed=42
):
    """
    Generate synthetic member-month level data.
    
    Parameters
    ----------
    n_members_per_market : int
        Number of unique members per market
    baseline_pmpm : float
        Baseline average cost PMPM
    market_effect_treated : float
        Persistent difference in treated market baseline
    time_trend_per_month : float
        Linear time trend (cost growth per month)
    treatment_effect : float
        True intervention effect (negative = cost reduction)
    risk_score_effect : float
        Effect of risk score on cost
    noise_std : float
        Standard deviation of random noise
    seed : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple of (member_df, market_df)
        member_df: member-month level data
        market_df: aggregated market-month level data
    """
    set_seed(seed)
    
    # Generate date range: January 2023 - December 2025 (36 months)
    start_date = datetime(2023, 1, 1)
    dates = pd.date_range(start=start_date, periods=36, freq='MS')
    
    # Create intervention indicator (starts January 2025)
    intervention_start = datetime(2025, 1, 1)
    
    # Initialize list to store member-month records
    records = []
    
    # Generate data for both markets
    markets = ['Control', 'Treated']
    
    for market in markets:
        # Generate unique member IDs for this market
        member_ids = [f"{market[0]}{str(i).zfill(4)}" for i in range(1, n_members_per_market + 1)]
        
        # Generate member-level risk scores (mean=1.0, realistic range)
        risk_scores = np.random.gamma(shape=4, scale=0.25, size=n_members_per_market)
        member_risk_dict = dict(zip(member_ids, risk_scores))
        
        for month_idx, date in enumerate(dates):
            year = date.year
            month = date.month
            
            # Create indicators
            treated_market = 1 if market == 'Treated' else 0
            post = 1 if date >= intervention_start else 0
            did = treated_market * post
            
            # Calculate time index (0-35)
            time_index = month_idx
            
            # Seasonality component (higher in winter months)
            seasonality = get_seasonality(month)
            
            for member_id in member_ids:
                risk_score = member_risk_dict[member_id]
                
                # Calculate cost PMPM with all components
                cost_pmpm = (
                    baseline_pmpm +
                    market_effect_treated * treated_market +
                    time_trend_per_month * time_index +
                    seasonality +
                    risk_score_effect * (risk_score - 1.0) +  # Center around mean risk
                    treatment_effect * did +
                    np.random.normal(0, noise_std)
                )
                
                # Ensure non-negative costs
                cost_pmpm = max(cost_pmpm, 0)
                
                records.append({
                    'member_id': member_id,
                    'market': market,
                    'date': date,
                    'year': year,
                    'month': month,
                    'time_index': time_index,
                    'treated_market': treated_market,
                    'post': post,
                    'did': did,
                    'risk_score': risk_score,
                    'cost_pmpm': cost_pmpm
                })
    
    # Create DataFrame
    member_df = pd.DataFrame(records)
    
    # Aggregate to market-month level
    market_df = aggregate_to_market_month(member_df)
    
    return member_df, market_df


def get_seasonality(month):
    """
    Generate seasonal cost adjustment.
    Healthcare costs are typically higher in winter months.
    
    Parameters
    ----------
    month : int
        Month number (1-12)
        
    Returns
    -------
    float
        Seasonal adjustment to cost
    """
    # Higher costs in January, February, and December
    seasonal_pattern = {
        1: 20,   # January - high (flu season, new deductibles)
        2: 15,   # February - high
        3: 5,    # March
        4: 0,    # April
        5: -5,   # May
        6: -8,   # June
        7: -10,  # July - low (summer)
        8: -8,   # August
        9: -5,   # September
        10: 0,   # October
        11: 5,   # November
        12: 18   # December - high (holidays, year-end)
    }
    return seasonal_pattern.get(month, 0)


def aggregate_to_market_month(member_df):
    """
    Aggregate member-month data to market-month level.
    
    Parameters
    ----------
    member_df : pd.DataFrame
        Member-month level data
        
    Returns
    -------
    pd.DataFrame
        Market-month level data with average PMPM
    """
    market_df = member_df.groupby(['market', 'date', 'year', 'month', 'time_index', 
                                    'treated_market', 'post', 'did']).agg({
        'cost_pmpm': 'mean',
        'member_id': 'count',
        'risk_score': 'mean'
    }).reset_index()
    
    # Rename columns
    market_df.rename(columns={
        'cost_pmpm': 'avg_cost_pmpm',
        'member_id': 'member_count',
        'risk_score': 'avg_risk_score'
    }, inplace=True)
    
    return market_df


def save_data(member_df, market_df, output_dir='output'):
    """
    Save generated data to CSV files.
    
    Parameters
    ----------
    member_df : pd.DataFrame
        Member-month level data
    market_df : pd.DataFrame
        Market-month level data
    output_dir : str
        Directory to save output files
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    member_df.to_csv(f'{output_dir}/member_month_data.csv', index=False)
    market_df.to_csv(f'{output_dir}/market_month_data.csv', index=False)
    
    print(f"Data saved to {output_dir}/")
    print(f"  - member_month_data.csv: {len(member_df):,} rows")
    print(f"  - market_month_data.csv: {len(market_df):,} rows")


def describe_data(member_df, market_df):
    """
    Print descriptive statistics of generated data.
    
    Parameters
    ----------
    member_df : pd.DataFrame
        Member-month level data
    market_df : pd.DataFrame
        Market-month level data
    """
    print("\n" + "="*70)
    print("SYNTHETIC DATA SUMMARY")
    print("="*70)
    
    print("\nMember-Month Level Data:")
    print(f"  Total observations: {len(member_df):,}")
    print(f"  Unique members: {member_df['member_id'].nunique():,}")
    print(f"  Date range: {member_df['date'].min().date()} to {member_df['date'].max().date()}")
    print(f"  Markets: {member_df['market'].unique().tolist()}")
    
    print("\nMarket-Month Level Data:")
    print(f"  Total observations: {len(market_df):,}")
    print(f"  Observations per market: {len(market_df) // 2}")
    
    print("\nAverage Cost PMPM by Market and Period:")
    summary = market_df.groupby(['market', 'post'])['avg_cost_pmpm'].agg(['mean', 'std', 'count'])
    summary.index = summary.index.set_levels([['Control', 'Treated'], ['Pre-Period', 'Post-Period']])
    print(summary.round(2))
    
    print("\nSimple Difference-in-Differences (without controls):")
    control_pre = market_df[(market_df['market'] == 'Control') & (market_df['post'] == 0)]['avg_cost_pmpm'].mean()
    control_post = market_df[(market_df['market'] == 'Control') & (market_df['post'] == 1)]['avg_cost_pmpm'].mean()
    treated_pre = market_df[(market_df['market'] == 'Treated') & (market_df['post'] == 0)]['avg_cost_pmpm'].mean()
    treated_post = market_df[(market_df['market'] == 'Treated') & (market_df['post'] == 1)]['avg_cost_pmpm'].mean()
    
    control_diff = control_post - control_pre
    treated_diff = treated_post - treated_pre
    did_estimate = treated_diff - control_diff
    
    print(f"  Control Market Change: ${control_diff:.2f}")
    print(f"  Treated Market Change: ${treated_diff:.2f}")
    print(f"  DiD Estimate (simple): ${did_estimate:.2f}")
    print(f"  True Treatment Effect: $-35.00")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("Generating synthetic data for DiD analysis...")
    
    # Generate data with default parameters
    member_df, market_df = generate_member_month_data(
        n_members_per_market=1000,
        baseline_pmpm=500,
        market_effect_treated=15,
        time_trend_per_month=1.5,
        treatment_effect=-35,
        risk_score_effect=80,
        noise_std=50,
        seed=42
    )
    
    # Print descriptive statistics
    describe_data(member_df, market_df)
    
    # Save data
    save_data(member_df, market_df)
    
    print("\nData generation complete!")

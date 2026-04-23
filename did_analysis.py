"""
Difference-in-Differences Analysis Module

Estimates the causal effect of healthcare intervention using two-way fixed effects
and event study specifications.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col


def estimate_did_model(market_df, verbose=True):
    """
    Estimate main Difference-in-Differences model with two-way fixed effects.
    
    Model specification:
        avg_cost_pmpm ~ did + C(market) + C(month)
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    verbose : bool
        Whether to print results
        
    Returns
    -------
    statsmodels RegressionResults
        Fitted model results
    """
    # Ensure month is treated as categorical
    market_df = market_df.copy()
    market_df['month_cat'] = market_df['month'].astype(str)
    
    # Estimate model with market and month fixed effects
    formula = 'avg_cost_pmpm ~ did + C(market) + C(month_cat)'
    model = smf.ols(formula=formula, data=market_df)
    results = model.fit()
    
    if verbose:
        print("\n" + "="*70)
        print("MAIN DIFFERENCE-IN-DIFFERENCES RESULTS")
        print("="*70)
        print("\nModel Specification:")
        print("  avg_cost_pmpm ~ did + C(market) + C(month)")
        print("\nFixed Effects:")
        print("  - Market fixed effects: YES")
        print("  - Month fixed effects: YES")
        print("\n" + "-"*70)
        print(results.summary())
        print("\n" + "-"*70)
        
        # Extract and highlight DiD coefficient
        did_coef = results.params['did']
        did_se = results.bse['did']
        did_pval = results.pvalues['did']
        did_ci = results.conf_int().loc['did']
        
        print("\nKEY RESULT - Treatment Effect Estimate:")
        print(f"  DiD Coefficient (β): ${did_coef:.2f}")
        print(f"  Standard Error: ${did_se:.2f}")
        print(f"  95% Confidence Interval: [${did_ci[0]:.2f}, ${did_ci[1]:.2f}]")
        print(f"  P-value: {did_pval:.4f}")
        print(f"  Significance: {'***' if did_pval < 0.01 else '**' if did_pval < 0.05 else '*' if did_pval < 0.1 else 'NS'}")
        
        print("\nInterpretation:")
        if did_coef < 0:
            print(f"  The intervention REDUCED costs by approximately ${abs(did_coef):.2f} PMPM")
            print(f"  in the treated market relative to the control market.")
        else:
            print(f"  The intervention INCREASED costs by approximately ${did_coef:.2f} PMPM")
            print(f"  in the treated market relative to the control market.")
        
        print(f"\n  True Simulated Effect: $-35.00 PMPM")
        print(f"  Estimation Error: ${abs(did_coef - (-35)):.2f}")
        
        print("\n" + "="*70)
    
    return results


def estimate_member_level_did(member_df, verbose=True):
    """
    Estimate DiD model at member-month level with risk adjustment.
    
    Model specification:
        cost_pmpm ~ did + risk_score + C(market) + C(month)
    
    Parameters
    ----------
    member_df : pd.DataFrame
        Member-month level data
    verbose : bool
        Whether to print results
        
    Returns
    -------
    statsmodels RegressionResults
        Fitted model results
    """
    # Prepare data
    member_df = member_df.copy()
    member_df['month_cat'] = member_df['month'].astype(str)
    
    # Estimate model with risk adjustment
    formula = 'cost_pmpm ~ did + risk_score + C(market) + C(month_cat)'
    model = smf.ols(formula=formula, data=member_df)
    results = model.fit()
    
    if verbose:
        print("\n" + "="*70)
        print("MEMBER-LEVEL DiD RESULTS (with Risk Adjustment)")
        print("="*70)
        print("\nModel Specification:")
        print("  cost_pmpm ~ did + risk_score + C(market) + C(month)")
        print("\n" + "-"*70)
        
        # Print abbreviated summary (too large otherwise)
        print("\nKey Coefficients:")
        key_vars = ['did', 'risk_score']
        for var in key_vars:
            if var in results.params:
                coef = results.params[var]
                se = results.bse[var]
                pval = results.pvalues[var]
                print(f"  {var:15s}: {coef:8.2f}  (SE: {se:.2f}, p={pval:.4f})")
        
        print(f"\nR-squared: {results.rsquared:.4f}")
        print(f"Observations: {int(results.nobs):,}")
        
        print("\n" + "="*70)
    
    return results


def event_study_analysis(market_df, verbose=True):
    """
    Estimate event study specification with dynamic treatment effects.
    
    Creates event time relative to January 2025 and estimates treatment effects
    for each month relative to intervention start.
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    verbose : bool
        Whether to print results
        
    Returns
    -------
    tuple of (results, event_study_df)
        results: statsmodels RegressionResults
        event_study_df: DataFrame with event time coefficients and CIs
    """
    # Create event time variable (months relative to intervention)
    market_df = market_df.copy()
    intervention_time = 24  # January 2025 is month index 24
    market_df['event_time'] = market_df['time_index'] - intervention_time
    
    # Create interaction terms for each event time (omit t=-1 as reference)
    event_times = sorted(market_df['event_time'].unique())
    
    # Build formula with event time interactions
    # Omit event_time = -1 as reference period
    interaction_terms = []
    for t in event_times:
        if t != -1:  # Omit t=-1 as reference
            # Use 'tn' for negative, 'tp' for positive to avoid minus sign in variable name
            if t < 0:
                var_name = f'treated_x_tn{abs(t)}'  # tn24 for t=-24
            else:
                var_name = f'treated_x_tp{t}'       # tp0 for t=0, tp1 for t=1
            market_df[var_name] = market_df['treated_market'] * (market_df['event_time'] == t)
            interaction_terms.append(var_name)
    
    # Build formula
    formula = 'avg_cost_pmpm ~ ' + ' + '.join(interaction_terms) + ' + C(market) + C(time_index)'
    
    # Estimate model
    model = smf.ols(formula=formula, data=market_df)
    results = model.fit()
    
    # Extract event study coefficients
    event_study_coefs = []
    for t in event_times:
        if t == -1:
            # Reference period
            event_study_coefs.append({
                'event_time': t,
                'coef': 0.0,
                'se': 0.0,
                'ci_lower': 0.0,
                'ci_upper': 0.0,
                'pvalue': np.nan
            })
        else:
            # Use same naming convention as above
            if t < 0:
                var_name = f'treated_x_tn{abs(t)}'
            else:
                var_name = f'treated_x_tp{t}'
            coef = results.params[var_name]
            se = results.bse[var_name]
            ci = results.conf_int().loc[var_name]
            pval = results.pvalues[var_name]
            
            event_study_coefs.append({
                'event_time': t,
                'coef': coef,
                'se': se,
                'ci_lower': ci[0],
                'ci_upper': ci[1],
                'pvalue': pval
            })
    
    event_study_df = pd.DataFrame(event_study_coefs)
    
    if verbose:
        print("\n" + "="*70)
        print("EVENT STUDY ANALYSIS")
        print("="*70)
        print("\nDynamic Treatment Effects (relative to t=-1):")
        print("\nPre-Period Effects (should be near zero):")
        pre_period = event_study_df[event_study_df['event_time'] < 0]
        for _, row in pre_period.tail(5).iterrows():
            t = int(row['event_time'])
            coef = row['coef']
            se = row['se']
            print(f"  t={t:3d}: {coef:7.2f}  (SE: {se:.2f})")
        
        print("\nPost-Period Effects (should be negative if intervention works):")
        post_period = event_study_df[event_study_df['event_time'] >= 0]
        for _, row in post_period.iterrows():
            t = int(row['event_time'])
            coef = row['coef']
            se = row['se']
            sig = '***' if row['pvalue'] < 0.01 else '**' if row['pvalue'] < 0.05 else '*' if row['pvalue'] < 0.1 else ''
            print(f"  t={t:3d}: {coef:7.2f}  (SE: {se:.2f}) {sig}")
        
        # Test for pre-trends
        print("\nPre-Trend Test:")
        pre_coeffs = pre_period['coef'].values
        if len(pre_coeffs) > 0:
            mean_pre_effect = np.mean(pre_coeffs)
            print(f"  Average pre-period coefficient: ${mean_pre_effect:.2f}")
            if abs(mean_pre_effect) < 5:
                print("  ✓ Pre-trends appear minimal (parallel trends likely satisfied)")
            else:
                print("  ✗ Warning: Non-trivial pre-trends detected")
        
        print("\n" + "="*70)
    
    return results, event_study_df


def parallel_trends_test(market_df, verbose=True):
    """
    Test for differential pre-trends between treated and control markets.
    
    Uses pre-period data only and tests whether treated market has different
    time trend than control market.
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    verbose : bool
        Whether to print results
        
    Returns
    -------
    statsmodels RegressionResults
        Fitted model results for pre-period
    """
    # Filter to pre-period only
    pre_df = market_df[market_df['post'] == 0].copy()
    
    # Create interaction between treated market and time index
    pre_df['treated_x_time'] = pre_df['treated_market'] * pre_df['time_index']
    
    # Estimate model
    formula = 'avg_cost_pmpm ~ treated_market + time_index + treated_x_time + C(month)'
    model = smf.ols(formula=formula, data=pre_df)
    results = model.fit()
    
    if verbose:
        print("\n" + "="*70)
        print("PRE-PERIOD PARALLEL TRENDS TEST")
        print("="*70)
        print("\nModel: avg_cost_pmpm ~ treated_market + time_index + treated_market × time_index + C(month)")
        print("Sample: Pre-period only (Jan 2023 - Dec 2024)")
        
        coef = results.params['treated_x_time']
        se = results.bse['treated_x_time']
        pval = results.pvalues['treated_x_time']
        ci = results.conf_int().loc['treated_x_time']
        
        print("\nTreated × Time Interaction:")
        print(f"  Coefficient: {coef:.4f}")
        print(f"  Standard Error: {se:.4f}")
        print(f"  P-value: {pval:.4f}")
        print(f"  95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
        
        print("\nInterpretation:")
        if pval > 0.05:
            print("  ✓ No significant differential pre-trend detected (p > 0.05)")
            print("  ✓ Parallel trends assumption appears plausible")
        else:
            print("  ✗ Warning: Significant differential pre-trend detected (p < 0.05)")
            print("  ✗ Parallel trends assumption may be violated")
        
        print("\n" + "="*70)
    
    return results


def compare_models(market_results, member_results):
    """
    Compare market-level and member-level DiD estimates side by side.
    
    Parameters
    ----------
    market_results : statsmodels RegressionResults
        Results from market-month model
    member_results : statsmodels RegressionResults
        Results from member-month model
    """
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    
    comparison = summary_col(
        [market_results, member_results],
        stars=True,
        float_format='%.2f',
        model_names=['Market-Month', 'Member-Month'],
        info_dict={
            'N': lambda x: f"{int(x.nobs):,}",
            'R-squared': lambda x: f"{x.rsquared:.4f}"
        }
    )
    
    print(comparison)
    print("\n" + "="*70)


def save_results(market_results, event_study_df, output_dir='output'):
    """
    Save regression results and event study estimates to files.
    
    Parameters
    ----------
    market_results : statsmodels RegressionResults
        Main DiD model results
    event_study_df : pd.DataFrame
        Event study coefficients
    output_dir : str
        Directory to save results
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main results summary
    with open(f'{output_dir}/did_results.txt', 'w') as f:
        f.write(market_results.summary().as_text())
    
    # Save event study coefficients
    event_study_df.to_csv(f'{output_dir}/event_study_results.csv', index=False)
    
    print(f"\nResults saved to {output_dir}/")


if __name__ == "__main__":
    # Load data (assumes data_simulation.py has been run)
    import os
    
    if not os.path.exists('output/market_month_data.csv'):
        print("Error: Data files not found. Please run data_simulation.py first.")
    else:
        print("Loading data for analysis...")
        market_df = pd.read_csv('output/market_month_data.csv')
        market_df['date'] = pd.to_datetime(market_df['date'])
        
        member_df = pd.read_csv('output/member_month_data.csv')
        member_df['date'] = pd.to_datetime(member_df['date'])
        
        # Run main DiD analysis
        print("\n" + "="*70)
        print("RUNNING DIFFERENCE-IN-DIFFERENCES ANALYSIS")
        print("="*70)
        
        # 1. Main market-level DiD
        market_results = estimate_did_model(market_df)
        
        # 2. Parallel trends test
        parallel_trends_test(market_df)
        
        # 3. Event study
        event_results, event_study_df = event_study_analysis(market_df)
        
        # 4. Member-level DiD (optional)
        print("\n\nRunning member-level analysis...")
        member_results = estimate_member_level_did(member_df)
        
        # 5. Compare models
        compare_models(market_results, member_results)
        
        # Save results
        save_results(market_results, event_study_df)
        
        print("\nAnalysis complete!")

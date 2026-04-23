"""
Main Execution Script for Difference-in-Differences Analysis

This script runs the complete analysis pipeline:
1. Generate synthetic data
2. Estimate DiD models
3. Create visualizations
4. Save all outputs

Usage:
    python main.py
"""

import sys
import os
from datetime import datetime

# Import our modules
from data_simulation import generate_member_month_data, describe_data, save_data
from did_analysis import (
    estimate_did_model, 
    estimate_member_level_did,
    event_study_analysis, 
    parallel_trends_test,
    compare_models,
    save_results
)
from visualization import create_all_plots


def print_header(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def main():
    """Run complete DiD analysis pipeline."""
    
    print_header("DIFFERENCE-IN-DIFFERENCES ANALYSIS PIPELINE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # =========================================================================
    # STEP 1: Generate Synthetic Data
    # =========================================================================
    print_header("STEP 1: GENERATING SYNTHETIC DATA")
    
    print("\nSimulation parameters:")
    print("  - Members per market: 1,000")
    print("  - Time period: January 2023 - December 2025 (36 months)")
    print("  - Intervention start: January 2025")
    print("  - True treatment effect: -$35 PMPM")
    print("  - Baseline PMPM: $500")
    
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
    save_data(member_df, market_df, output_dir='output')
    
    # =========================================================================
    # STEP 2: Run DiD Analysis
    # =========================================================================
    print_header("STEP 2: ESTIMATING DiD MODELS")
    
    # 2a. Main market-level DiD with two-way fixed effects
    print("\n[2a] Market-Level DiD Model...")
    market_results = estimate_did_model(market_df, verbose=True)
    
    # 2b. Parallel trends test
    print("\n[2b] Testing Parallel Trends Assumption...")
    parallel_trends_test(market_df, verbose=True)
    
    # 2c. Event study analysis
    print("\n[2c] Event Study Analysis...")
    event_results, event_study_df = event_study_analysis(market_df, verbose=True)
    
    # 2d. Member-level DiD (optional robustness check)
    print("\n[2d] Member-Level DiD Model (with Risk Adjustment)...")
    print("     (This may take a moment with 72,000 observations...)")
    member_results = estimate_member_level_did(member_df, verbose=True)
    
    # 2e. Compare models
    print("\n[2e] Comparing Market-Level vs Member-Level Estimates...")
    compare_models(market_results, member_results)
    
    # Save regression results
    save_results(market_results, event_study_df, output_dir='output')
    
    # =========================================================================
    # STEP 3: Create Visualizations
    # =========================================================================
    print_header("STEP 3: GENERATING VISUALIZATIONS")
    
    create_all_plots(market_df, event_study_df, output_dir='output', show_plots=False)
    
    # =========================================================================
    # STEP 4: Summary
    # =========================================================================
    print_header("ANALYSIS COMPLETE")
    
    print("\n✓ Data Generation: Complete")
    print("✓ DiD Estimation: Complete")
    print("✓ Visualizations: Complete")
    
    print("\nOutput files created in 'output/' directory:")
    print("  Data:")
    print("    - member_month_data.csv")
    print("    - market_month_data.csv")
    print("  Results:")
    print("    - did_results.txt")
    print("    - event_study_results.csv")
    print("  Plots:")
    print("    - pmpm_trends.png")
    print("    - parallel_trends_check.png")
    print("    - event_study.png")
    print("    - did_illustration.png")
    
    # Extract key result
    did_coef = market_results.params['did']
    did_se = market_results.bse['did']
    did_pval = market_results.pvalues['did']
    
    print("\n" + "-"*70)
    print("KEY FINDING:")
    print(f"  Estimated Treatment Effect: ${did_coef:.2f} PMPM")
    print(f"  Standard Error: ${did_se:.2f}")
    print(f"  P-value: {did_pval:.4f}")
    print(f"  True Simulated Effect: $-35.00 PMPM")
    print(f"  Estimation Error: ${abs(did_coef - (-35)):.2f}")
    print("-"*70)
    
    if abs(did_coef - (-35)) < 5:
        print("\n✓ DiD model successfully recovered the true treatment effect!")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*70)
    
    return market_df, member_df, market_results, event_study_df


if __name__ == "__main__":
    try:
        # Run the full pipeline
        results = main()
        
        print("\n✓ All steps completed successfully!")
        print("\nTo re-run individual components:")
        print("  - python data_simulation.py")
        print("  - python did_analysis.py")
        print("  - python visualization.py")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("\nPlease check:")
        print("  1. All required packages are installed (pip install -r requirements.txt)")
        print("  2. You have write permissions to the output directory")
        import traceback
        traceback.print_exc()
        sys.exit(1)

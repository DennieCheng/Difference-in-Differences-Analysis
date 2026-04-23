"""
Visualization Module for Difference-in-Differences Analysis

Creates publication-quality plots for PMPM trends, parallel trends checks,
and event study results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_pmpm_trends(market_df, output_dir='output', show_plot=False):
    """
    Plot average Cost PMPM over time for both markets.
    
    Shows full time series with vertical line at intervention start.
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    output_dir : str
        Directory to save plot
    show_plot : bool
        Whether to display plot interactively
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot each market
    for market in ['Control', 'Treated']:
        market_data = market_df[market_df['market'] == market].sort_values('date')
        
        # Use different styles
        if market == 'Control':
            ax.plot(market_data['date'], market_data['avg_cost_pmpm'], 
                   marker='o', linewidth=2.5, markersize=6,
                   label='Control Market', color='#2E86AB', alpha=0.8)
        else:
            ax.plot(market_data['date'], market_data['avg_cost_pmpm'], 
                   marker='s', linewidth=2.5, markersize=6,
                   label='Treated Market', color='#A23B72', alpha=0.8)
    
    # Add vertical line at intervention start
    intervention_date = datetime(2025, 1, 1)
    ax.axvline(x=intervention_date, color='red', linestyle='--', 
               linewidth=2, alpha=0.7, label='Intervention Start')
    
    # Shade pre and post periods
    pre_end = datetime(2024, 12, 31)
    ax.axvspan(market_df['date'].min(), pre_end, alpha=0.1, color='gray', label='Pre-Period')
    ax.axvspan(intervention_date, market_df['date'].max(), alpha=0.1, color='yellow', label='Post-Period')
    
    # Labels and formatting
    ax.set_xlabel('Date', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Cost PMPM ($)', fontsize=13, fontweight='bold')
    ax.set_title('Cost PMPM Trends: Treatment vs Control Market\n(January 2023 - December 2025)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    # Save
    filepath = f'{output_dir}/pmpm_trends.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved: {filepath}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_parallel_trends(market_df, output_dir='output', show_plot=False):
    """
    Plot pre-period trends to assess parallel trends assumption.
    
    Shows only pre-intervention period (Jan 2023 - Dec 2024).
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    output_dir : str
        Directory to save plot
    show_plot : bool
        Whether to display plot interactively
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter to pre-period
    pre_df = market_df[market_df['post'] == 0].copy()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot each market
    for market in ['Control', 'Treated']:
        market_data = pre_df[pre_df['market'] == market].sort_values('date')
        
        if market == 'Control':
            ax.plot(market_data['date'], market_data['avg_cost_pmpm'], 
                   marker='o', linewidth=2.5, markersize=7,
                   label='Control Market', color='#2E86AB', alpha=0.8)
        else:
            ax.plot(market_data['date'], market_data['avg_cost_pmpm'], 
                   marker='s', linewidth=2.5, markersize=7,
                   label='Treated Market', color='#A23B72', alpha=0.8)
    
    # Labels and formatting
    ax.set_xlabel('Date', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Cost PMPM ($)', fontsize=13, fontweight='bold')
    ax.set_title('Pre-Period Parallel Trends Check\n(January 2023 - December 2024)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add note
    ax.text(0.02, 0.98, 
            'Parallel trends assumption: Both markets should follow similar trajectories\nbefore intervention',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save
    filepath = f'{output_dir}/parallel_trends_check.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved: {filepath}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_event_study(event_study_df, output_dir='output', show_plot=False):
    """
    Plot event study coefficients with confidence intervals.
    
    Shows dynamic treatment effects relative to intervention start (t=0).
    
    Parameters
    ----------
    event_study_df : pd.DataFrame
        Event study results with columns: event_time, coef, ci_lower, ci_upper
    output_dir : str
        Directory to save plot
    show_plot : bool
        Whether to display plot interactively
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Sort by event time
    event_study_df = event_study_df.sort_values('event_time')
    
    # Separate pre and post periods
    pre_period = event_study_df[event_study_df['event_time'] < 0]
    post_period = event_study_df[event_study_df['event_time'] >= 0]
    
    # Plot pre-period coefficients (blue)
    ax.plot(pre_period['event_time'], pre_period['coef'], 
           marker='o', linewidth=2, markersize=8, color='#2E86AB', 
           label='Pre-Period', alpha=0.8)
    ax.fill_between(pre_period['event_time'], 
                    pre_period['ci_lower'], pre_period['ci_upper'],
                    alpha=0.2, color='#2E86AB')
    
    # Plot post-period coefficients (red)
    ax.plot(post_period['event_time'], post_period['coef'], 
           marker='s', linewidth=2, markersize=8, color='#A23B72', 
           label='Post-Period', alpha=0.8)
    ax.fill_between(post_period['event_time'], 
                    post_period['ci_lower'], post_period['ci_upper'],
                    alpha=0.2, color='#A23B72')
    
    # Add reference line at zero
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    
    # Add vertical line at intervention (t=0)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2, 
              alpha=0.7, label='Intervention Start (t=0)')
    
    # Shade reference period (t=-1)
    ax.axvspan(-1.5, -0.5, alpha=0.15, color='gray', 
              label='Reference Period (t=-1)')
    
    # Labels and formatting
    ax.set_xlabel('Event Time (Months Relative to Intervention)', 
                 fontsize=13, fontweight='bold')
    ax.set_ylabel('Treatment Effect on Cost PMPM ($)', 
                 fontsize=13, fontweight='bold')
    ax.set_title('Event Study: Dynamic Treatment Effects\n(with 95% Confidence Intervals)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='lower left', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    # Add interpretation note
    note_text = ('Pre-period coefficients near zero → Parallel trends likely hold\n'
                'Post-period coefficients negative → Intervention reduced costs')
    ax.text(0.98, 0.02, note_text,
            transform=ax.transAxes, fontsize=10, 
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save
    filepath = f'{output_dir}/event_study.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved: {filepath}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_did_illustration(market_df, output_dir='output', show_plot=False):
    """
    Create a simple visual illustration of the DiD concept.
    
    Shows average PMPM by period and market with difference calculations.
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    output_dir : str
        Directory to save plot
    show_plot : bool
        Whether to display plot interactively
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate averages by period and market
    summary = market_df.groupby(['market', 'post'])['avg_cost_pmpm'].mean().reset_index()
    summary['period'] = summary['post'].map({0: 'Pre', 1: 'Post'})
    
    # Pivot for easier plotting
    pivot = summary.pivot(index='period', columns='market', values='avg_cost_pmpm')
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Bar plot
    x = np.arange(len(pivot.index))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pivot['Control'], width, 
                   label='Control Market', color='#2E86AB', alpha=0.8)
    bars2 = ax.bar(x + width/2, pivot['Treated'], width, 
                   label='Treated Market', color='#A23B72', alpha=0.8)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height:.0f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Calculate and display differences
    control_pre = pivot.loc['Pre', 'Control']
    control_post = pivot.loc['Post', 'Control']
    treated_pre = pivot.loc['Pre', 'Treated']
    treated_post = pivot.loc['Post', 'Treated']
    
    control_diff = control_post - control_pre
    treated_diff = treated_post - treated_pre
    did_estimate = treated_diff - control_diff
    
    # Add annotations
    info_text = (f'Control Market Change: ${control_diff:.2f}\n'
                f'Treated Market Change: ${treated_diff:.2f}\n'
                f'─────────────────────────────\n'
                f'DiD Estimate: ${did_estimate:.2f}')
    
    ax.text(0.98, 0.98, info_text,
            transform=ax.transAxes, fontsize=12, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', 
                     alpha=0.8, edgecolor='black', linewidth=2),
            family='monospace')
    
    # Labels and formatting
    ax.set_ylabel('Average Cost PMPM ($)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Period', fontsize=13, fontweight='bold')
    ax.set_title('Difference-in-Differences Concept\n(2×2 Design)', 
                fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(['Pre-Period\n(Jan 2023 - Dec 2024)', 
                       'Post-Period\n(Jan 2025 - Dec 2025)'])
    ax.legend(fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    # Save
    filepath = f'{output_dir}/did_illustration.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"Saved: {filepath}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def create_all_plots(market_df, event_study_df, output_dir='output', show_plots=False):
    """
    Generate all visualization plots.
    
    Parameters
    ----------
    market_df : pd.DataFrame
        Market-month level data
    event_study_df : pd.DataFrame
        Event study results
    output_dir : str
        Directory to save plots
    show_plots : bool
        Whether to display plots interactively
    """
    print("\n" + "="*70)
    print("GENERATING VISUALIZATIONS")
    print("="*70)
    
    print("\nCreating plots...")
    
    # 1. PMPM trends over full period
    plot_pmpm_trends(market_df, output_dir, show_plots)
    
    # 2. Pre-period parallel trends check
    plot_parallel_trends(market_df, output_dir, show_plots)
    
    # 3. Event study plot
    plot_event_study(event_study_df, output_dir, show_plots)
    
    # 4. Simple DiD illustration
    plot_did_illustration(market_df, output_dir, show_plots)
    
    print(f"\n✓ All visualizations saved to {output_dir}/")
    print("="*70)


if __name__ == "__main__":
    # Load data (assumes analysis has been run)
    import os
    
    if not os.path.exists('output/market_month_data.csv'):
        print("Error: Data files not found. Please run data_simulation.py first.")
    elif not os.path.exists('output/event_study_results.csv'):
        print("Error: Event study results not found. Please run did_analysis.py first.")
    else:
        print("Loading data for visualization...")
        
        market_df = pd.read_csv('output/market_month_data.csv')
        market_df['date'] = pd.to_datetime(market_df['date'])
        
        event_study_df = pd.read_csv('output/event_study_results.csv')
        
        # Create all plots
        create_all_plots(market_df, event_study_df, show_plots=False)
        
        print("\nVisualization complete!")

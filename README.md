# Difference-in-Differences Analysis: Healthcare Intervention Impact on Cost PMPM

## Overview

This repository demonstrates a **Difference-in-Differences (DiD)** analysis to estimate the causal effect of an extra care intervention on monthly healthcare **Cost Per Member Per Month (PMPM)** using synthetic data.

### Problem Statement

A healthcare organization implements an extra care intervention in one market starting in January 2025. We want to estimate whether this intervention reduced monthly Cost PMPM compared to a similar control market that did not receive the intervention.

### Study Design

- **Treatment Market**: Receives extra care intervention starting January 2025
- **Control Market**: Does not receive intervention
- **Time Period**: January 2023 - December 2025 (36 months)
- **Pre-Period**: January 2023 - December 2024 (24 months)
- **Post-Period**: January 2025 - December 2025 (12 months)
- **Outcome**: Cost PMPM (Per Member Per Month)

### Data Structure

The analysis uses two levels of aggregation:
1. **Member-Month Level**: Individual member costs by month (more realistic)
2. **Market-Month Level**: Aggregated average PMPM by market and month (primary analysis unit)

## Methodology

### Difference-in-Differences Model

The core DiD specification with two-way fixed effects:

```
Cost_PMPM_mt = α_m + δ_t + β × (Treated_Market_m × Post_t) + ε_mt
```

Where:
- `α_m`: Market fixed effects (control for time-invariant market differences)
- `δ_t`: Month fixed effects (control for common time trends and seasonality)
- `β`: **DiD treatment effect** (our parameter of interest)
- `Treated_Market × Post`: Interaction term indicating treatment market in post-period

### Identifying Assumption

**Parallel Trends**: In the absence of the intervention, the treated and control markets would have followed parallel trends in Cost PMPM.

## Synthetic Data Design

The data generation process includes realistic healthcare cost components:

| Component | Value | Purpose |
|-----------|-------|---------|
| Baseline PMPM | $500 | Common starting cost level |
| Market Effect | +$15 (treated) | Persistent baseline difference |
| Time Trend | +$1.5/month | Secular cost growth |
| Seasonality | Higher in Jan, Feb, Dec | Within-year cost variation |
| Risk Score Effect | +$80 × risk_score | Member-level heterogeneity |
| Random Noise | Normal error | Realistic variation |
| **Treatment Effect** | **-$35** | True intervention effect to recover |

## Repository Structure

```
.
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # Run complete analysis pipeline
├── data_simulation.py        # Generate synthetic data
├── did_analysis.py           # Estimate DiD models
├── visualization.py          # Create plots and visualizations
└── output/                   # Generated outputs (plots, results)
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/did-healthcare-analysis.git
cd did-healthcare-analysis
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Run Complete Analysis

Execute the entire pipeline with a single command:

```bash
python main.py
```

This will:
1. Generate synthetic member-month and market-month data
2. Create descriptive statistics
3. Estimate the main DiD model
4. Generate PMPM trend plots and event study graphs
5. Save all outputs to the `output/` directory

### Run Individual Components

**Generate Data Only:**
```python
from data_simulation import generate_member_month_data, aggregate_to_market_month

member_df, market_df = generate_member_month_data()
```

**Run DiD Analysis:**
```python
from did_analysis import estimate_did_model, event_study_analysis

results = estimate_did_model(market_df)
print(results.summary())
```

**Create Visualizations:**
```python
from visualization import plot_pmpm_trends, plot_event_study

plot_pmpm_trends(market_df)
plot_event_study(event_study_results)
```

## Key Results

### Main DiD Estimate

The analysis estimates the **treatment effect** (β coefficient on the DiD interaction term):

- **True Simulated Effect**: -$35 PMPM
- **Estimated Effect**: ~-$35 PMPM (with standard errors)
- **Interpretation**: The extra care intervention reduced monthly costs by approximately $35 per member per month in the treated market relative to the control market

### Parallel Trends Check

Visual inspection of pre-period trends (Jan 2023 - Dec 2024) confirms that both markets followed similar trajectories before the intervention, supporting the parallel trends assumption.

### Event Study

The dynamic event study shows:
- Pre-intervention coefficients cluster around zero (no pre-trends)
- Post-intervention coefficients are consistently negative (sustained treatment effect)

## Visualizations

The package generates three key plots:

1. **PMPM Trend Plot**: Full time series showing both markets with vertical line at intervention start
2. **Pre-Period Parallel Trends**: Focused view of pre-intervention period to assess parallel trends assumption
3. **Event Study Plot**: Dynamic treatment effects with 95% confidence intervals relative to intervention timing

## Limitations

1. **Illustrative Inference**: Only two markets are included, limiting statistical power and generalizability
2. **Parallel Trends Assumption**: Cannot be tested definitively; we can only assess pre-period trends
3. **Synthetic Data**: Real healthcare claims data involve additional complexities:
   - Enrollment changes and attrition
   - More sophisticated risk adjustment
   - Spillover effects and contamination
   - Clustered standard errors for multiple markets
4. **Simple Seasonality**: Real healthcare costs have more complex seasonal patterns
5. **No Covariates**: Production analyses would include market-level characteristics and time-varying controls

## Extensions

Potential enhancements for real-world applications:

- **Multiple Markets**: Expand to 10+ markets for more robust inference
- **Member-Level Analysis**: Run models on member-month data with member fixed effects
- **Heterogeneous Effects**: Test for differential effects by risk score, age, or disease category
- **Robustness Checks**: 
  - Alternative control groups
  - Different pre/post period definitions
  - Placebo tests with fake intervention dates
- **Clustered Standard Errors**: Account for serial correlation within markets
- **Synthetic Control**: Use weighted combination of control markets

## References

- Angrist, J. D., & Pischke, J. S. (2009). *Mostly Harmless Econometrics*. Princeton University Press.
- Cunningham, S. (2021). *Causal Inference: The Mixtape*. Yale University Press.
- Goodman-Bacon, A. (2021). "Difference-in-differences with variation in treatment timing." *Journal of Econometrics*.

## License

MIT License - Feel free to use and modify for your own analyses.

## Contact

For questions or suggestions, please open an issue or submit a pull request.

---

**Note**: This is a synthetic demonstration for educational purposes. Real-world causal inference requires careful consideration of institutional details, data quality, and threats to identification.

# Quick Start Guide

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Analysis

### Option 1: Run Complete Pipeline (Recommended)

Execute the entire analysis with a single command:

```bash
python main.py
```

This will:
- Generate synthetic data (member-month and market-month levels)
- Run all DiD models (market-level, member-level, event study)
- Test parallel trends assumption
- Create all visualizations
- Save results to `output/` directory

**Expected runtime:** ~30-60 seconds

### Option 2: Run Individual Components

If you want to run components separately:

**Step 1: Generate Data**
```bash
python data_simulation.py
```

**Step 2: Run Analysis**
```bash
python did_analysis.py
```

**Step 3: Create Plots**
```bash
python visualization.py
```

## Output Files

After running the analysis, you'll find these files in the `output/` directory:

### Data Files
- `member_month_data.csv` - Member-level monthly cost data
- `market_month_data.csv` - Market-level aggregated data

### Results Files
- `did_results.txt` - Full regression output
- `event_study_results.csv` - Dynamic treatment effects

### Visualizations
- `pmpm_trends.png` - Full time series of both markets
- `parallel_trends_check.png` - Pre-period trend comparison
- `event_study.png` - Dynamic treatment effects plot
- `did_illustration.png` - Simple 2×2 DiD diagram

## Understanding the Results

### Key Output: DiD Coefficient

Look for the `did` coefficient in the regression output. This represents the **causal treatment effect** of the intervention on Cost PMPM.

**Interpretation:**
- **Negative coefficient** = Intervention reduced costs
- **Positive coefficient** = Intervention increased costs

### Example Output
```
DiD Coefficient (β): $-35.12
Standard Error: $2.45
95% Confidence Interval: [-$40.02, -$30.22]
P-value: 0.0000
```

This means the intervention reduced costs by approximately **$35 PMPM** in the treated market compared to the control market.

## Customizing the Analysis

### Modify Data Parameters

Edit the parameters in `main.py`:

```python
member_df, market_df = generate_member_month_data(
    n_members_per_market=1000,      # Number of members per market
    baseline_pmpm=500,               # Baseline cost level
    treatment_effect=-35,            # True treatment effect
    noise_std=50,                    # Random variation
    seed=42                          # Random seed (for reproducibility)
)
```

### Change True Treatment Effect

To test if the DiD model correctly recovers different effect sizes, modify `treatment_effect`:

```python
treatment_effect=-50  # Larger cost reduction
treatment_effect=-20  # Smaller cost reduction
treatment_effect=0    # No effect (null hypothesis)
treatment_effect=30   # Cost increase
```

## Troubleshooting

**Issue: Import errors**
- Solution: Make sure all packages are installed: `pip install -r requirements.txt`

**Issue: "output directory not found" error**
- Solution: The script creates it automatically, but you can manually create it: `mkdir output`

**Issue: Plots not displaying**
- Solution: Plots are saved to `output/` by default. To display them interactively, modify the code to set `show_plots=True` in `visualization.py`

## Next Steps

1. **Examine the plots** in `output/` to visually assess the intervention effect
2. **Review the regression results** in `output/did_results.txt`
3. **Check parallel trends** - Pre-period trends should be similar between markets
4. **Interpret the event study** - Pre-period coefficients should be near zero

## Additional Resources

- See `README.md` for detailed methodology and limitations
- Modify `data_simulation.py` to add more complexity (e.g., different seasonality patterns)
- Extend `did_analysis.py` to add robustness checks or additional models

---

For questions or issues, please refer to the main README.md file.

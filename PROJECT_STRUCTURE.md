# Project Structure

## Overview

This repository contains a complete implementation of a Difference-in-Differences (DiD) analysis for evaluating a healthcare intervention's impact on Cost PMPM.

## Directory Structure

```
Difference in Differences/
│
├── README.md                 # Main project documentation
├── QUICKSTART.md            # Quick start guide for running the analysis
├── PROJECT_STRUCTURE.md     # This file - explains project organization
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python package dependencies
│
├── main.py                 # Main execution script - runs complete pipeline
├── data_simulation.py      # Data generation module
├── did_analysis.py         # Statistical analysis module
├── visualization.py        # Plotting and visualization module
│
└── output/                 # Generated outputs (created when you run main.py)
    ├── .gitkeep           # Ensures directory is tracked by Git
    ├── member_month_data.csv       # (generated)
    ├── market_month_data.csv       # (generated)
    ├── did_results.txt             # (generated)
    ├── event_study_results.csv     # (generated)
    ├── pmpm_trends.png             # (generated)
    ├── parallel_trends_check.png   # (generated)
    ├── event_study.png             # (generated)
    └── did_illustration.png        # (generated)
```

## File Descriptions

### Documentation Files

**README.md**
- Primary project documentation
- Methodology explanation
- Study design details
- Limitations and extensions
- References

**QUICKSTART.md**
- Step-by-step installation guide
- How to run the analysis
- How to interpret results
- Troubleshooting tips
- Customization options

**PROJECT_STRUCTURE.md** (this file)
- Project organization overview
- File descriptions
- Module dependencies

**LICENSE**
- MIT License allowing free use and modification

### Configuration Files

**requirements.txt**
- Python package dependencies
- Versions specified for reproducibility
- Install with: `pip install -r requirements.txt`

**.gitignore**
- Specifies files/folders to exclude from Git
- Excludes generated outputs, Python cache, IDE files

### Core Python Modules

#### main.py
**Purpose:** Master script that orchestrates the entire analysis pipeline

**What it does:**
1. Generates synthetic data
2. Runs all statistical models
3. Creates all visualizations
4. Saves all outputs
5. Prints summary of key results

**Usage:**
```bash
python main.py
```

**Dependencies:** All other modules

---

#### data_simulation.py
**Purpose:** Generate realistic synthetic healthcare cost data

**Key Functions:**
- `generate_member_month_data()` - Creates member-level data with all realistic components
- `get_seasonality()` - Adds healthcare cost seasonality
- `aggregate_to_market_month()` - Aggregates to market-month level
- `describe_data()` - Prints descriptive statistics
- `save_data()` - Saves data to CSV files

**Data Components:**
- Baseline PMPM ($500)
- Market-level fixed effect
- Common time trend
- Seasonal patterns
- Individual risk scores
- Treatment effect (-$35)
- Random noise

**Output:**
- Member-month dataset: ~72,000 rows
- Market-month dataset: 72 rows (36 months × 2 markets)

**Usage:**
```bash
python data_simulation.py
```

---

#### did_analysis.py
**Purpose:** Estimate DiD models and conduct statistical inference

**Key Functions:**
- `estimate_did_model()` - Main market-level two-way fixed effects DiD
- `estimate_member_level_did()` - Member-level DiD with risk adjustment
- `event_study_analysis()` - Dynamic treatment effects estimation
- `parallel_trends_test()` - Test for pre-period differential trends
- `compare_models()` - Side-by-side comparison of results
- `save_results()` - Save regression outputs

**Models Estimated:**
1. **Main DiD**: `avg_cost_pmpm ~ did + C(market) + C(month)`
2. **Member-level DiD**: `cost_pmpm ~ did + risk_score + C(market) + C(month)`
3. **Event Study**: Dynamic effects with monthly interactions
4. **Pre-trend Test**: `avg_cost_pmpm ~ treated × time + controls`

**Output:**
- Regression summary tables
- Treatment effect estimates
- Confidence intervals
- P-values
- Event study coefficients

**Usage:**
```bash
python did_analysis.py
```

---

#### visualization.py
**Purpose:** Create publication-quality plots and visualizations

**Key Functions:**
- `plot_pmpm_trends()` - Full time series plot (both markets)
- `plot_parallel_trends()` - Pre-period trend comparison
- `plot_event_study()` - Dynamic treatment effects with CIs
- `plot_did_illustration()` - Simple 2×2 DiD diagram
- `create_all_plots()` - Generate all visualizations

**Plots Created:**
1. **PMPM Trends** - Time series showing intervention impact
2. **Parallel Trends Check** - Pre-period comparison
3. **Event Study** - Monthly treatment effects with confidence bands
4. **DiD Illustration** - Bar chart showing the DiD concept

**Features:**
- High-resolution PNG output (300 DPI)
- Professional styling with seaborn
- Color-coded markets
- Annotations and interpretive notes
- Currency formatting

**Usage:**
```bash
python visualization.py
```

---

### Output Directory

**output/**

Generated when you run the analysis. Contains:

**Data Files:**
- `member_month_data.csv` - Individual member costs by month
- `market_month_data.csv` - Aggregated market-level data

**Results Files:**
- `did_results.txt` - Full regression output from statsmodels
- `event_study_results.csv` - Event study coefficients and CIs

**Visualization Files:**
- `pmpm_trends.png` - Main time series plot
- `parallel_trends_check.png` - Pre-period trends
- `event_study.png` - Dynamic effects plot
- `did_illustration.png` - Simple DiD concept diagram

## Module Dependencies

```
main.py
  ├── data_simulation.py
  ├── did_analysis.py
  └── visualization.py

data_simulation.py
  ├── numpy
  ├── pandas
  └── datetime

did_analysis.py
  ├── numpy
  ├── pandas
  └── statsmodels

visualization.py
  ├── numpy
  ├── pandas
  ├── matplotlib
  └── seaborn
```

## Execution Flow

1. **Data Generation** (`data_simulation.py`)
   - Generate member-level synthetic data
   - Aggregate to market-month level
   - Save both datasets

2. **Statistical Analysis** (`did_analysis.py`)
   - Load market-month data
   - Estimate main DiD model
   - Test parallel trends
   - Run event study
   - (Optional) Run member-level model
   - Save results

3. **Visualization** (`visualization.py`)
   - Load data and results
   - Create 4 publication-quality plots
   - Save as high-resolution PNGs

4. **Summary** (`main.py`)
   - Orchestrate all steps
   - Print key findings
   - Report estimation accuracy

## Customization Points

### Change Study Parameters

Edit `main.py` or `data_simulation.py`:
```python
generate_member_month_data(
    n_members_per_market=1000,    # Sample size
    baseline_pmpm=500,            # Cost level
    treatment_effect=-35,         # Effect size
    noise_std=50,                 # Variability
    seed=42                       # Reproducibility
)
```

### Add New Analysis

Add functions to `did_analysis.py`:
- Subgroup analysis
- Alternative specifications
- Robustness checks
- Placebo tests

### Modify Visualizations

Edit `visualization.py`:
- Change plot styles
- Add new plot types
- Modify color schemes
- Adjust annotations

## Development Workflow

### For New Users
1. Read `README.md` for methodology
2. Follow `QUICKSTART.md` to run analysis
3. Examine outputs in `output/`

### For Developers
1. Fork/clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Modify relevant modules
4. Test changes: `python main.py`
5. Add new features/analyses as needed

## Testing

Run each module independently to test:
```bash
python data_simulation.py  # Test data generation
python did_analysis.py     # Test models (requires data)
python visualization.py    # Test plots (requires results)
python main.py            # Test full pipeline
```

## Version Control

**Tracked by Git:**
- All Python code
- Documentation
- Configuration files
- Empty output directory structure

**Not tracked (.gitignore):**
- Generated data files
- Results files
- Plot images
- Python cache files

---

Last updated: 2026

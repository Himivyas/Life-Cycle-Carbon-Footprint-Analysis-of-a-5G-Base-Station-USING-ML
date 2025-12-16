# 5G Equipment Life Cycle Assessment (LCA) - CO2 Emissions Analysis

##  Overview

This project provides a comprehensive Life Cycle Assessment (LCA) tool for analyzing CO2 emissions from 5G telecommunications equipment over its entire lifecycle. The analysis covers three main phases:

- **Manufacturing Phase**: Emissions from production and assembly
- **Operational Phase**: Emissions from electricity consumption during use
- **End-of-Life Phase**: Emissions from recycling and disposal

The tool models multiple scenarios including baseline operations, renewable energy integration, sleep mode optimization, and various combinations to identify the most effective carbon reduction strategies.

## Key Features

- **Multi-Scenario Analysis**: Compare baseline, renewable energy, sleep mode, and hybrid scenarios
- **Comprehensive Emissions Tracking**: Track manufacturing, operational, and end-of-life emissions separately
- **Sensitivity Analysis**: Explore the impact of varying renewable energy share (0-100%) and sleep mode efficiency (0-80%)
- **Rich Visualizations**: Generate professional plots including:
  - Annual emissions line charts
  - Cumulative emissions trends
  - Component breakdown bar charts
  - Stacked emissions by lifecycle phase
  - Savings heatmaps
  - Comparative savings bar charts
- **Detailed Reporting**: Export results to multi-sheet Excel workbooks
- **Flexible Configuration**: Easily modify parameters to match your specific equipment and regional conditions

##  Requirements

### Python Version
- Python 3.7 or higher

### Dependencies
```
numpy>=1.19.0
pandas>=1.2.0
matplotlib>=3.3.0
openpyxl>=3.0.0
```

### Installation

1. **Clone or download this repository**

2. **Install required packages:**
```bash
pip install numpy pandas matplotlib openpyxl
```

Or using a requirements.txt file:
```bash
pip install -r requirements.txt
```

##  Project Structure

```
5G-LCA-Analysis/
│
├── igcn_project.py          # Main analysis script
├── README.md                 # This file
├── requirements.txt          # Python dependencies
│
└── outputs/                  # Generated output files (created automatically)
    ├── 5G_LCA_results_YYYYMMDD_HHMMSS.xlsx
    ├── CO2_annual_stacked_YYYYMMDD_HHMMSS.png
    ├── CO2_cumulative_YYYYMMDD_HHMMSS.png
    ├── CO2_components_bars_YYYYMMDD_HHMMSS.png
    ├── CO2_baseline_stacked_YYYYMMDD_HHMMSS.png
    ├── CO2_renewable_stacked_YYYYMMDD_HHMMSS.png
    ├── CO2_mixed_stacked_YYYYMMDD_HHMMSS.png
    ├── CO2_sleep_stacked_YYYYMMDD_HHMMSS.png
    ├── CO2_sleep+renewable_stacked_YYYYMMDD_HHMMSS.png
    ├── CO2_savings_analysis_YYYYMMDD_HHMMSS.png
    └── CO2_savings_simple_YYYYMMDD_HHMMSS.png
```

##  Quick Start

### Basic Usage

Run the script with default parameters:

```bash
python igcn_project.py
```

This will:
1. Calculate emissions for all predefined scenarios
2. Generate visualization plots
3. Create an Excel workbook with detailed results
4. Save all outputs with timestamp-based filenames

### Expected Output

The script will generate:
- **1 Excel file** with 5 sheets containing all numerical results
- **11 PNG image files** with various visualizations

##  Configuration

### Key Parameters

All parameters can be modified at the top of the script:

#### Equipment Lifecycle Parameters
```python
LIFETIME_YEARS = 10              # Equipment operational lifetime (years)
MANUFACTURING_ENERGY_KWH = 30000 # Manufacturing energy consumption (kWh)
EOL_ENERGY_KWH = 2000            # End-of-life processing energy (kWh)
BASE_POWER_KW = 5.0              # Average operational power draw (kW)
```

#### Emission Factors (kg CO2 per kWh)
```python
GRID_EMISSION_FACTOR = 0.55         # Standard grid electricity
RENEWABLE_EMISSION_FACTOR = 0.05    # Renewable energy (with lifecycle)
RECYCLING_EMISSION_FACTOR = 0.30    # Recycling/disposal processes
```

**Note:** These values should be replaced with region-specific or equipment-specific data for accurate analysis. Default values are representative estimates.

#### Optimization Scenarios
```python
DEFAULT_SLEEP_MODE_REDUCTION = 0.30  # 30% energy reduction in sleep mode
DEFAULT_PARTIAL_RENEWABLE = 0.30     # 30% renewable in mixed scenario
```

#### Model Options
```python
manufacturing_spread = False  # True: amortize over lifetime
                              # False: allocate to year 0
save_plots = True             # Save plots as PNG files
```

### Customizing Scenarios

The script includes 5 predefined scenarios:

1. **Baseline**: Standard grid power, no optimizations
2. **Renewable**: 100% renewable energy, no sleep mode
3. **Mixed**: 30% renewable energy, no sleep mode
4. **Sleep**: Grid power with 30% sleep mode reduction
5. **Sleep+Renewable**: 100% renewable with 30% sleep mode

To add or modify scenarios, edit the `scenarios_defs` dictionary:

```python
scenarios_defs = {
    "your_scenario_name": {
        "sleep_frac": 0.40,      # 40% sleep reduction
        "renewable_share": 0.50   # 50% renewable energy
    }
}
```

##  Understanding the Outputs

### Excel Workbook Sheets

The generated Excel file contains multiple sheets:

#### 1. Annual_Results
- Year-by-year emissions for all scenarios
- Columns: `year`, `manufacturing_kgCO2`, `operational_kgCO2`, `eol_kgCO2`, `total_kgCO2`, `scenario`

#### 2. Cumulative_Results
- Running totals of emissions over time
- Includes cumulative values for each emission component

#### 3. Lifetime_Summary
- Total lifetime emissions by scenario
- Breakdown by manufacturing, operational, and end-of-life phases

#### 4. Savings_kgCO2_grid
- Complete sensitivity analysis matrix
- Shows absolute savings (kg CO2) for all combinations of renewable share (0-100%) and sleep mode (0-80%)

#### 5. Savings_Sorted
- Comparative savings analysis
- Scenarios ranked by total CO2 reduction compared to baseline

### Visualization Plots

#### 1. Annual Emissions Line Plot
- Shows yearly total emissions for each scenario
- Useful for identifying emission patterns and spikes

#### 2. Cumulative Emissions Plot
- Tracks total accumulated emissions over equipment lifetime
- Clearly shows long-term emission differences between scenarios

#### 3. Component Breakdown Bar Charts
- Three subplots showing manufacturing, operational, and end-of-life emissions
- Compares all scenarios side-by-side for each year

#### 4. Individual Stacked Bar Charts (per scenario)
- One plot per scenario showing emission composition each year
- Stacked bars reveal the proportion of each emission source

#### 5. Savings Heatmap
- 2D color map showing % savings vs. baseline
- X-axis: Renewable energy share (0-100%)
- Y-axis: Sleep mode reduction (0-80%)
- Contour lines indicate savings percentages

#### 6. Simple Savings Bar Chart
- Direct comparison of total lifetime savings
- Annotated with absolute savings (kg CO2) and percentages

## 🔬 Methodology

### Emissions Calculation

#### Manufacturing Emissions
```
Manufacturing CO2 = Manufacturing Energy (kWh) × Grid Emission Factor (kgCO2/kWh)
```

Options:
- **Year 0 allocation**: All emissions occur at equipment production
- **Amortized allocation**: Spread evenly across lifetime

#### Operational Emissions
```
Effective Emission Factor = (Renewable Share × Renewable EF) + 
                           ((1 - Renewable Share) × Grid EF)

Annual Operational Energy = Base Power (kW) × Hours/Year × (1 - Sleep Reduction)

Annual Operational CO2 = Annual Operational Energy × Effective Emission Factor
```

#### End-of-Life Emissions
```
EoL CO2 = EoL Energy (kWh) × Recycling Emission Factor (kgCO2/kWh)
```
- Occurs only in final year

### Total Lifecycle Emissions
```
Total CO2 = Σ(Manufacturing) + Σ(Operational) + EoL Emissions
```

##  Use Cases

### 1. Equipment Procurement Decisions
Compare different equipment options by adjusting manufacturing energy and operational power parameters.

### 2. Energy Strategy Planning
Identify optimal mix of renewable energy and efficiency improvements using sensitivity analysis.

### 3. Carbon Reduction Targets
Quantify emission reductions achievable through various interventions to set realistic targets.

### 4. Sustainability Reporting
Generate comprehensive data and visualizations for environmental reports and disclosures.

### 5. Policy Impact Assessment
Model the effect of renewable energy mandates or efficiency standards on equipment emissions.

### 6. Research and Publication
Use as a foundation for academic research on telecommunications infrastructure sustainability.

##  Example Analysis Workflow

### Scenario: Evaluating a Carbon Reduction Strategy

**Goal**: Reduce CO2 emissions by 50% compared to baseline operations

**Step 1**: Run baseline analysis
```bash
python igcn_project.py
```

**Step 2**: Review `Lifetime_Summary` sheet in Excel
- Note baseline total: e.g., 250,000 kg CO2
- Target: 125,000 kg CO2 (50% reduction)

**Step 3**: Check `Savings_Sorted` sheet
- Find scenarios meeting the target
- Example: "sleep+renewable" achieves 65% reduction

**Step 4**: Review `Savings_kgCO2_grid` for alternative combinations
- Find minimum renewable share needed with 30% sleep mode
- Or minimum sleep mode needed with 50% renewables

**Step 5**: Customize and re-run if needed
```python
# Test specific combination
scenarios_defs["custom_target"] = {
    "sleep_frac": 0.35,
    "renewable_share": 0.60
}
```

**Step 6**: Present findings using generated visualizations

## Interpreting Results

### Key Metrics

**Absolute Savings (kg CO2)**
- Direct reduction compared to baseline
- Example: 150,000 kg CO2 saved over 10 years

**Percentage Savings (%)**
- Relative reduction from baseline
- Example: 60% reduction in total emissions

**Emission Intensity**
- CO2 per unit of service (if service metrics available)
- Useful for benchmarking against industry standards

### Common Findings

1. **Operational emissions dominate** (typically 80-90% of lifecycle total)
2. **Renewable energy** provides the highest single-intervention savings
3. **Combined strategies** (renewable + efficiency) yield multiplicative benefits
4. **Manufacturing emissions** are significant upfront but amortized over lifetime
5. **Diminishing returns** above 70-80% renewable share or sleep efficiency

##  Limitations and Assumptions

### Model Limitations

1. **Simplified Energy Model**: Assumes constant power draw (doesn't model variable loads)
2. **Static Emission Factors**: Doesn't account for grid decarbonization over time
3. **No Degradation**: Assumes constant efficiency throughout lifetime
4. **Linear Relationships**: Actual savings may be non-linear
5. **Scope 2 Focus**: Primarily covers operational emissions, limited Scope 3 analysis

### Key Assumptions

- Equipment operates continuously (24/7) at rated power
- Sleep mode reduces power proportionally without affecting service
- Renewable energy is available when needed (no intermittency modeling)
- Emission factors remain constant over equipment lifetime
- Manufacturing and EoL energy estimates are accurate
- No consideration of transmission/distribution losses

### Recommended Validation

- Compare emission factors with regional grid data (e.g., IEA, EPA)
- Validate equipment power draw with manufacturer specifications
- Cross-check results with published LCA studies
- Consider seasonal variations in actual deployment
- Account for auxiliary equipment (cooling, backup power, etc.)

##  Extending the Model

### Adding New Scenarios

```python
# Add to scenarios_defs dictionary
scenarios_defs["aggressive_optimization"] = {
    "sleep_frac": 0.50,      # 50% sleep reduction
    "renewable_share": 0.90   # 90% renewable
}
```

### Modifying Emission Components

```python
# Add auxiliary equipment
COOLING_POWER_KW = 2.0
ANNUAL_OPERATIONAL_ENERGY_KWH = (BASE_POWER_KW + COOLING_POWER_KW) * HOURS_PER_YEAR
```

### Including Time-Varying Emission Factors

```python
# Grid decarbonization over time
def get_grid_emission_factor(year):
    initial_ef = 0.55
    annual_reduction = 0.02  # 2% per year
    return initial_ef * (1 - annual_reduction) ** year
```

### Adding Economic Analysis

```python
# Cost per kWh
GRID_COST_PER_KWH = 0.12
RENEWABLE_COST_PER_KWH = 0.10

# Calculate operational costs
operational_cost = operational_energy * cost_per_kwh
```

##  Contributing

Contributions are welcome! Areas for improvement:

- Dynamic energy modeling (variable loads)
- Time-series grid emission factors
- Equipment degradation modeling
- Economic cost-benefit analysis
- Additional visualization types
- Sensitivity analysis for emission factors
- Uncertainty quantification
- Multi-site deployment scenarios

##  References and Further Reading

### Standards and Guidelines
- ISO 14040:2006 - Environmental management — Life cycle assessment — Principles and framework
- ISO 14044:2006 - Environmental management — Life cycle assessment — Requirements and guidelines
- GHG Protocol - Product Life Cycle Accounting and Reporting Standard

### Emission Factor Databases
- IEA (International Energy Agency) - Country-specific grid emission factors
- EPA (Environmental Protection Agency) - eGRID database (US)
- DEFRA (UK) - Government emission conversion factors
- IPCC (Intergovernmental Panel on Climate Change) - Emission factor database

### Related Research
- ITU-T L.1410 - Methodology for environmental life cycle assessments of ICT goods, networks and services
- ETSI ES 203 199 - Environmental Engineering (EE); Life Cycle Assessment (LCA) of ICT equipment, networks and services
- GeSI/GESI reports on ICT carbon footprint

##  Support and Contact

For questions, issues, or suggestions:

- Open an issue on the project repository
- Contact: [Your contact information]
- Documentation: [Link to additional documentation if available]

##  License

[Specify your license here - e.g., MIT, Apache 2.0, GPL, etc.]

##  Acknowledgments

- Based on LCA methodologies from ISO 14040/14044 standards
- Emission factor data sources: [List your sources]
- Inspired by telecommunications industry sustainability initiatives

##  Version History

### Version 1.0.0 (Current)
- Initial release
- Five predefined scenarios
- Comprehensive visualization suite
- Excel export functionality
- Sensitivity analysis for renewable share and sleep mode

---

**Last Updated**: December 2025

**Author**: Himi Vyas



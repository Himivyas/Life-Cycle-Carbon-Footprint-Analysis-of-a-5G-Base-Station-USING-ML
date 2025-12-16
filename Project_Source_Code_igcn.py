# -*- coding: utf-8 -*-
"""
5G Equipment Life Cycle Assessment (LCA) CO2 Emissions Model

This script performs a comprehensive Life Cycle Assessment of 5G telecommunications equipment,
calculating CO2 emissions across manufacturing, operational, and end-of-life phases under
various scenarios (baseline, renewable energy, sleep mode, and combinations).

Original file is located at
    https://colab.research.google.com/drive/16N9_tTb73GKe6Qk3oPYpNGzaXSnsBHsn
"""

# ============================================================================
# IMPORTS
# ============================================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from matplotlib.ticker import MaxNLocator

# ============================================================================
# CONFIGURATION AND CONSTANTS
# ============================================================================

# Set matplotlib figure resolution for better quality plots
plt.rcParams["figure.dpi"] = 120

# Equipment lifecycle parameters
LIFETIME_YEARS = 10  # Total operational lifetime of equipment (years)

# Energy consumption values (kWh)
MANUFACTURING_ENERGY_KWH = 30000  # Total energy consumed during manufacturing phase
EOL_ENERGY_KWH = 2000  # Energy required for end-of-life processing/recycling
BASE_POWER_KW = 5.0  # Average operational power consumption (kW)

# Time calculations
HOURS_PER_YEAR = 24 * 365  # Total hours in one year
ANNUAL_OPERATIONAL_ENERGY_KWH = BASE_POWER_KW * HOURS_PER_YEAR  # Annual energy consumption

# Emission factors (kg CO2 per kWh)
# These values represent the carbon intensity of different energy sources
GRID_EMISSION_FACTOR = 0.55  # Standard grid electricity (kgCO2/kWh)
RENEWABLE_EMISSION_FACTOR = 0.05  # Renewable energy with lifecycle emissions (kgCO2/kWh)
RECYCLING_EMISSION_FACTOR = 0.30  # Emissions from recycling/end-of-life processing (kgCO2/kWh)

# Optimization parameters for scenarios
DEFAULT_SLEEP_MODE_REDUCTION = 0.30  # 30% reduction in energy during sleep/idle mode
DEFAULT_PARTIAL_RENEWABLE = 0.30  # 30% renewable energy in mixed-grid scenario

# Model configuration options
manufacturing_spread = False  # If True: amortize manufacturing emissions over lifetime
                              # If False: allocate all manufacturing emissions to year 0
save_plots = True  # Whether to save generated plots as PNG files

# Output file naming with timestamp for version control
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
out_xlsx = f"5G_LCA_results_{timestamp}.xlsx"
out_plot_annual = f"CO2_annual_stacked_{timestamp}.png"
out_plot_cumulative = f"CO2_cumulative_{timestamp}.png"
out_plot_component = f"CO2_component_year_{timestamp}.png"
out_plot_savings = f"CO2_savings_analysis_{timestamp}.png"

# Display initial configuration
print("Annual operational energy (kWh):", f"{ANNUAL_OPERATIONAL_ENERGY_KWH:,}")
print("Output Excel ->", out_xlsx)

# Create array of years for analysis (0 to LIFETIME_YEARS inclusive)
years = np.arange(0, LIFETIME_YEARS + 1)

# ============================================================================
# CORE CALCULATION FUNCTIONS
# ============================================================================

def emissions_from_energy(energy_kwh, ef):
    """
    Calculate CO2 emissions from energy consumption.
    
    Parameters:
        energy_kwh (float): Energy consumption in kilowatt-hours
        ef (float): Emission factor in kg CO2 per kWh
    
    Returns:
        float: Total CO2 emissions in kilograms
    """
    return energy_kwh * ef


def build_scenario_df(name, sleep_frac=0.0, renewable_share=0.0, 
                      manufacturing_spread_local=manufacturing_spread):
    """
    Build a complete emissions DataFrame for a specific scenario across all years.
    
    This function calculates annual emissions from manufacturing, operations, and
    end-of-life processing, accounting for energy efficiency measures (sleep mode)
    and renewable energy adoption.
    
    Parameters:
        name (str): Descriptive name for the scenario
        sleep_frac (float): Fraction of operational energy reduced by sleep mode (0.0-1.0)
        renewable_share (float): Fraction of operational energy from renewables (0.0-1.0)
        manufacturing_spread_local (bool): Whether to amortize manufacturing emissions
    
    Returns:
        pd.DataFrame: DataFrame with columns:
            - year: Year number (0 to LIFETIME_YEARS)
            - manufacturing_kgCO2: Manufacturing emissions for that year
            - operational_kgCO2: Operational emissions for that year
            - eol_kgCO2: End-of-life emissions for that year
            - total_kgCO2: Sum of all emission sources
            - scenario: Scenario name
    """
    # Initialize emission arrays for each lifecycle phase
    manuf = np.zeros_like(years, dtype=float)
    op = np.zeros_like(years, dtype=float)
    eol = np.zeros_like(years, dtype=float)
    
    # --- Manufacturing Emissions ---
    if manufacturing_spread_local:
        # Amortize manufacturing emissions evenly across lifetime
        annual_manufacturing_kwh = MANUFACTURING_ENERGY_KWH / LIFETIME_YEARS
        manuf[:] = emissions_from_energy(annual_manufacturing_kwh, GRID_EMISSION_FACTOR)
    else:
        # Allocate all manufacturing emissions to year 0 (initial production)
        manuf[0] = emissions_from_energy(MANUFACTURING_ENERGY_KWH, GRID_EMISSION_FACTOR)
    
    # --- Operational Emissions ---
    # Calculate weighted average emission factor based on renewable share
    # Higher renewable share = lower effective emission factor
    ef_operational = (renewable_share * RENEWABLE_EMISSION_FACTOR + 
                      (1.0 - renewable_share) * GRID_EMISSION_FACTOR)
    
    # Calculate operational emissions for each year
    for i, y in enumerate(years):
        # Reduce energy consumption by sleep_frac (energy efficiency improvement)
        op_energy = ANNUAL_OPERATIONAL_ENERGY_KWH * (1.0 - sleep_frac)
        op[i] = emissions_from_energy(op_energy, ef_operational)
    
    # --- End-of-Life Emissions ---
    # All EoL processing occurs in the final year
    eol[-1] = emissions_from_energy(EOL_ENERGY_KWH, RECYCLING_EMISSION_FACTOR)
    
    # Construct DataFrame with all emission components
    df = pd.DataFrame({
        "year": years,
        "manufacturing_kgCO2": manuf,
        "operational_kgCO2": op,
        "eol_kgCO2": eol
    })
    
    # Calculate total annual emissions
    df["total_kgCO2"] = df[["manufacturing_kgCO2", "operational_kgCO2", "eol_kgCO2"]].sum(axis=1)
    df["scenario"] = name
    
    return df


# ============================================================================
# SCENARIO DEFINITIONS
# ============================================================================

# Define all scenarios to be analyzed
# Each scenario represents a different combination of energy efficiency and renewable adoption
scenarios_defs = {
    "baseline": {
        "sleep_frac": 0.0,  # No sleep mode optimization
        "renewable_share": 0.0  # 100% grid electricity
    },
    "renewable": {
        "sleep_frac": 0.0,  # No sleep mode
        "renewable_share": 1.0  # 100% renewable energy
    },
    "mixed": {
        "sleep_frac": 0.0,  # No sleep mode
        "renewable_share": DEFAULT_PARTIAL_RENEWABLE  # 30% renewables
    },
    "sleep": {
        "sleep_frac": DEFAULT_SLEEP_MODE_REDUCTION,  # 30% energy reduction
        "renewable_share": 0.0  # 100% grid electricity
    },
    "sleep+renewable": {
        "sleep_frac": DEFAULT_SLEEP_MODE_REDUCTION,  # 30% energy reduction
        "renewable_share": 1.0  # 100% renewable energy
    }
}

# ============================================================================
# GENERATE ANNUAL AND CUMULATIVE RESULTS
# ============================================================================

# Build DataFrames for all scenarios
list_df = []
for name, params in scenarios_defs.items():
    df_s = build_scenario_df(
        name, 
        sleep_frac=params["sleep_frac"], 
        renewable_share=params["renewable_share"],
        manufacturing_spread_local=manufacturing_spread
    )
    list_df.append(df_s)

# Combine all scenarios into a single DataFrame
annual_results = pd.concat(list_df, ignore_index=True).sort_values(["scenario", "year"])

# Calculate cumulative emissions over time for each scenario
cumulative_results = annual_results.copy()
cumulative_results["cumulative_total_kgCO2"] = cumulative_results.groupby("scenario")["total_kgCO2"].cumsum()
cumulative_results["cumulative_operational_kgCO2"] = cumulative_results.groupby("scenario")["operational_kgCO2"].cumsum()
cumulative_results["cumulative_manufacturing_kgCO2"] = cumulative_results.groupby("scenario")["manufacturing_kgCO2"].cumsum()
cumulative_results["cumulative_eol_kgCO2"] = cumulative_results.groupby("scenario")["eol_kgCO2"].cumsum()

# ============================================================================
# LIFETIME SUMMARY STATISTICS
# ============================================================================

# Calculate total lifetime emissions for each scenario
summary_rows = []
for name in scenarios_defs.keys():
    df_s = annual_results[annual_results["scenario"] == name]
    summary_rows.append({
        "scenario": name,
        "manufacturing_life_kgCO2": df_s["manufacturing_kgCO2"].sum(),
        "operational_life_kgCO2": df_s["operational_kgCO2"].sum(),
        "eol_life_kgCO2": df_s["eol_kgCO2"].sum(),
        "total_life_kgCO2": df_s["total_kgCO2"].sum()
    })

summary_df = pd.DataFrame(summary_rows).set_index("scenario")

# Display lifetime totals sorted by total emissions
print("\nLifetime totals (kgCO2):")
print(summary_df["total_life_kgCO2"].sort_values())

# ============================================================================
# EXPORT RESULTS TO EXCEL
# ============================================================================

# Save all results to a multi-sheet Excel workbook
with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    annual_results.to_excel(writer, sheet_name="Annual_Results", index=False)
    cumulative_results.to_excel(writer, sheet_name="Cumulative_Results", index=False)
    summary_df.to_excel(writer, sheet_name="Lifetime_Summary")

print("Saved Excel:", out_xlsx)

# ============================================================================
# VISUALIZATION 1: ANNUAL EMISSIONS LINE PLOT
# ============================================================================

# Plot annual total emissions for all scenarios over time
plt.figure(figsize=(10, 6))
for name in scenarios_defs.keys():
    df_s = annual_results[annual_results["scenario"] == name]
    plt.plot(df_s["year"], df_s["total_kgCO2"], marker='o', linewidth=2, label=name.capitalize())

plt.xlabel("Year")
plt.ylabel("Annual CO2 emissions (kg CO2)")
plt.title("CO2 Emissions vs Time for Different Scenarios")
plt.grid(alpha=0.3)
plt.legend()

if save_plots:
    plt.savefig(out_plot_annual)
    print("Saved annual line plot:", out_plot_annual)
plt.show()

# ============================================================================
# VISUALIZATION 2: CUMULATIVE EMISSIONS LINE PLOT
# ============================================================================

# Plot cumulative emissions over time for all scenarios
fig, ax = plt.subplots(figsize=(10, 6))
scenario_names = list(scenarios_defs.keys())

for name in scenario_names:
    df_s = cumulative_results[cumulative_results["scenario"] == name]
    ax.plot(df_s["year"], df_s["cumulative_total_kgCO2"], marker='o', label=name.capitalize())

ax.set_xlabel("Year")
ax.set_ylabel("Cumulative CO2 emissions (kg CO2)")
ax.set_title("Cumulative CO2 Emissions vs Time (per scenario)")
ax.legend()
ax.grid(alpha=0.25)

if save_plots:
    plt.savefig(out_plot_cumulative)
    print("Saved cumulative plot:", out_plot_cumulative)
plt.show()

# ============================================================================
# VISUALIZATION 3: COMPONENT BREAKDOWN BAR CHARTS
# ============================================================================

# Create separate bar charts for each emission component (Manufacturing, Operational, EoL)
# Each subplot compares all scenarios side-by-side for each year
fig, axes = plt.subplots(3, 1, figsize=(12, 14), sharex=False)

# Define the emission components to plot
component_cols = [
    ("manufacturing_kgCO2", "Manufacturing CO₂ (kg)"),
    ("operational_kgCO2", "Operational CO₂ (kg)"),
    ("eol_kgCO2", "End-of-Life CO₂ (kg)")
]

n_scenarios = len(scenario_names)
bar_width = 0.14  # Width of each bar
x = np.arange(len(years))  # X-axis positions for years

# Create grouped bar chart for each component
for ax, (col, ylabel) in zip(axes, component_cols):
    for i, name in enumerate(scenario_names):
        # Get data for this scenario
        df_s = annual_results[annual_results["scenario"] == name].set_index("year")
        values = df_s[col].reindex(years).values
        
        # Offset bars horizontally to group by year
        offset = (i - n_scenarios/2) * bar_width + bar_width/2
        ax.bar(x + offset, values, width=bar_width, label=name.capitalize())
    
    # Configure x-axis to show all year labels
    ax.set_xticks(x)
    ax.set_xticklabels(years, rotation=0)
    ax.tick_params(axis='x', which='both', labelbottom=True)
    
    ax.set_ylabel(ylabel)
    ax.grid(axis='y', alpha=0.25)
    ax.legend(loc="upper right")

# Label the bottom subplot's x-axis
axes[-1].set_xlabel("Year")
fig.suptitle("Annual Manufacturing, Operational & End-of-Life Emissions (Bar Charts)", fontsize=15)

# Save the multi-panel figure
out_plot_components_all = f"CO2_components_bars_{timestamp}.png"
if save_plots:
    plt.savefig(out_plot_components_all)
    print("Saved bar-component plot:", out_plot_components_all)
plt.show()

# ============================================================================
# VISUALIZATION 4: STACKED BAR CHARTS PER SCENARIO
# ============================================================================

# Create individual stacked bar charts showing emission breakdown for each scenario
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # Manufacturing, Operational, EoL colors
bar_width = 0.6

for name in scenario_names:
    # Get data for this scenario
    df_s = annual_results[annual_results["scenario"] == name].set_index("year").reindex(years).fillna(0)
    manuf = df_s["manufacturing_kgCO2"].values
    oper = df_s["operational_kgCO2"].values
    eol = df_s["eol_kgCO2"].values
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(years))
    
    # Stack bars: manufacturing at bottom, operational in middle, EoL on top
    p1 = ax.bar(x, manuf, width=bar_width, label="Manufacturing", color=colors[0])
    p2 = ax.bar(x, oper, width=bar_width, bottom=manuf, label="Operational", color=colors[1])
    p3 = ax.bar(x, eol, width=bar_width, bottom=manuf+oper, label="End-of-life", color=colors[2])
    
    # Configure axes
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual CO2 emissions (kg CO2)")
    ax.set_title(f"{name.capitalize()} — Annual Emissions by Component")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    
    # Save individual scenario plot
    out_file = f"CO2_{name}_stacked_{timestamp}.png"
    if save_plots:
        plt.savefig(out_file)
        print("Saved:", out_file)
    plt.show()

# ============================================================================
# SENSITIVITY ANALYSIS: RENEWABLE SHARE vs SLEEP MODE
# ============================================================================

# Perform a grid search to analyze combined effects of renewable energy and sleep mode
# This creates a heatmap showing CO2 savings across different combinations

# Define parameter ranges for sensitivity analysis
renewable_shares = np.linspace(0.0, 1.0, 11)  # 0%, 10%, 20%, ..., 100% renewables
sleep_fracs = np.linspace(0.0, 0.8, 17)  # 0%, 5%, 10%, ..., 80% sleep reduction

# Calculate baseline for comparison (no optimizations)
baseline_df = build_scenario_df("baseline", sleep_frac=0.0, renewable_share=0.0, 
                                manufacturing_spread_local=manufacturing_spread)
baseline_lifetime = baseline_df["total_kgCO2"].sum()

# Initialize grid to store lifetime emissions for each combination
grid_lifetime = np.zeros((len(sleep_fracs), len(renewable_shares)))

# Calculate lifetime emissions for each parameter combination
for i, sf in enumerate(sleep_fracs):
    for j, rs in enumerate(renewable_shares):
        df_temp = build_scenario_df(
            f"temp_sf{sf}_rs{rs}", 
            sleep_frac=sf, 
            renewable_share=rs,
            manufacturing_spread_local=manufacturing_spread
        )
        grid_lifetime[i, j] = df_temp["total_kgCO2"].sum()

# Calculate savings relative to baseline
savings_pct = (baseline_lifetime - grid_lifetime) / baseline_lifetime * 100.0  # Percentage savings
savings_abs = baseline_lifetime - grid_lifetime  # Absolute savings in kg CO2

# ============================================================================
# VISUALIZATION 5: SAVINGS HEATMAP
# ============================================================================

# Create heatmap showing percentage savings across parameter space
fig, ax = plt.subplots(figsize=(10, 6))

# Create colored heatmap
im = ax.imshow(savings_pct, aspect='auto', origin='lower', 
               extent=[renewable_shares[0], renewable_shares[-1], 
                       sleep_fracs[0], sleep_fracs[-1]], 
               cmap='YlGn')

# Add colorbar
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('% Lifetime CO2 savings vs baseline')

# Configure axes
ax.set_xlabel('Renewable share (fraction of operational energy)')
ax.set_ylabel('Sleep-mode reduction fraction')
ax.set_title('Lifetime CO2 Savings (% vs baseline) — varying renewable share & sleep mode')

# Add contour lines for easier reading of values
CS = ax.contour(renewable_shares, sleep_fracs, savings_pct, 
                colors='k', linewidths=0.5, alpha=0.6)
ax.clabel(CS, inline=1, fontsize=8, fmt="%.0f%%")

if save_plots:
    plt.savefig(out_plot_savings)
    print("Saved savings heatmap:", out_plot_savings)
plt.show()

# ============================================================================
# EXTRACT KEY INSIGHTS FROM SENSITIVITY ANALYSIS
# ============================================================================

# Find and display savings at default parameter values
default_sf = DEFAULT_SLEEP_MODE_REDUCTION
default_rs = DEFAULT_PARTIAL_RENEWABLE

# Find nearest grid points to default values
idx_sf = np.abs(sleep_fracs - default_sf).argmin()
idx_rs = np.abs(renewable_shares - default_rs).argmin()

# Display key statistics
print(f"\nBaseline lifetime CO2 (kg): {baseline_lifetime:,.0f}")
print(f"Lifetime CO2 at default sleep={sleep_fracs[idx_sf]:.2f}, renewables={renewable_shares[idx_rs]:.2f}: {grid_lifetime[idx_sf, idx_rs]:,.0f}")
print(f"Absolute savings (kg): {savings_abs[idx_sf, idx_rs]:,.0f} --> {savings_pct[idx_sf, idx_rs]:.1f}%")

# Create DataFrame with absolute savings for all combinations
savings_df = pd.DataFrame(savings_abs, 
                          index=np.round(sleep_fracs, 3), 
                          columns=np.round(renewable_shares, 3))
savings_df.index.name = "sleep_frac"
savings_df.columns.name = "renewable_share"

# Append savings grid to Excel file
with pd.ExcelWriter(out_xlsx, engine="openpyxl", mode="a") as writer:
    savings_df.to_excel(writer, sheet_name="Savings_kgCO2_grid")
print("Appended savings grid to Excel:", out_xlsx)

# ============================================================================
# COMPARATIVE SAVINGS ANALYSIS
# ============================================================================

# Compare key scenarios directly to baseline to quantify savings potential
compare_keys = ["baseline", "mixed", "renewable", "sleep", "sleep+renewable"]

# Calculate lifetime totals for comparison scenarios
lifetime_totals = {}
for key in compare_keys:
    params = scenarios_defs.get(key)
    df_key = build_scenario_df(
        key, 
        sleep_frac=params["sleep_frac"],
        renewable_share=params["renewable_share"],
        manufacturing_spread_local=manufacturing_spread
    )
    lifetime_totals[key] = df_key["total_kgCO2"].sum()

baseline_total = lifetime_totals["baseline"]

# Calculate absolute and percentage savings for each scenario
summary_rows = []
for k, val in lifetime_totals.items():
    savings_kg = baseline_total - val
    savings_pct = (savings_kg / baseline_total) * 100.0
    summary_rows.append({
        "scenario": k,
        "lifetime_total_kgCO2": val,
        "savings_kgCO2": savings_kg,
        "savings_pct": savings_pct
    })

savings_df = pd.DataFrame(summary_rows).set_index("scenario")

# Sort by savings (highest savings first)
savings_df = savings_df.sort_values("savings_kgCO2", ascending=False)

# ============================================================================
# VISUALIZATION 6: SAVINGS BAR CHART
# ============================================================================

# Create bar chart showing absolute savings compared to baseline
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(savings_df.index, savings_df["savings_kgCO2"], color="seagreen")

# Annotate each bar with absolute and percentage savings
for rect, scen in zip(bars, savings_df.index):
    height = rect.get_height()
    pct = savings_df.loc[scen, "savings_pct"]
    ax.annotate(f"{height:,.0f} kg\n({pct:.1f}%)",
                xy=(rect.get_x() + rect.get_width()/2, height),
                xytext=(0, 5),  # 5 points vertical offset
                textcoords="offset points",
                ha="center", va="bottom", fontsize=9)

ax.set_ylabel("CO₂ Savings (kg)")
ax.set_title("CO₂ Savings Compared to Baseline (Higher = More Savings)")
ax.grid(axis="y", alpha=0.25)

# Save savings comparison plot
out_plot_savings_simple = f"CO2_savings_simple_{timestamp}.png"
if save_plots:
    plt.savefig(out_plot_savings_simple)
    print("Saved savings plot:", out_plot_savings_simple)
plt.show()

# ============================================================================
# FINAL EXCEL EXPORT
# ============================================================================

# Add sorted savings comparison to Excel workbook
with pd.ExcelWriter(out_xlsx, engine="openpyxl", mode="a") as writer:
    savings_df.to_excel(writer, sheet_name="Savings_Sorted")
print("Added sorted savings table to Excel:", out_xlsx)

# ============================================================================
# SUMMARY OF OUTPUT FILES
# ============================================================================

print("\nFiles created in current working directory:")
print(" - Excel:", out_xlsx)
print(" - Annual stacked plot:", out_plot_annual)
print(" - Cumulative plot:", out_plot_cumulative)
print(" - Component mix plot:", out_plot_component)
print(" - Savings heatmap:", out_plot_savings)

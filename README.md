# Global Energy Trends

## Project Overview

This project explores how the global energy landscape has evolved over the last 20 years through comprehensive data analysis and time series analysis. The goal is to uncover trends in energy consumption, generation, and transition patterns across countries and regions.

## Current Status

**Phase 1: Data Exploration** ✓ Completed

- Explored data from multiple sources (IMF, Ember)
- Evaluated data comprehensiveness and quality
- Selected **Ember CSV dataset** as the primary data source for its superior coverage
- Developed an Ember API client library for future use (API data expected to expand)

## Planned Phases

- **Time Series Analysis**: Analyze energy trends and patterns over 20-year period
- **Demand Prediction**: Build forecasting model for energy demand

## Project Structure

```
notebooks/
├── 01_explore_imf_data.ipynb           # IMF data exploration
├── 02_explore_ember_data.ipynb         # Ember API exploration
└── 03_EDA_Ember_Full_Release_Data.ipynb # Full Ember dataset analysis

src/
├── data/
│   ├── ember_api_client.py  # Ember API client library
│   └── get_data.py          # Data fetching utilities
├── my_project/
│   └── paths.py             # Project path configurations
└── utils/
    └── plots.py             # Visualization utilities
```

## Data Source

**[Ember Energy](https://ember-energy.org/data/yearly-electricity-data/)**: Comprehensive global electricity data with extensive historical coverage and country-level granularity.


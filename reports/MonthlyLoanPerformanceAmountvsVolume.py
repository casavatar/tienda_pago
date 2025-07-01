# reports/visual_2.py
#------------------------------------------------------------------------------------
# This script generates a dual-axis time series plot showing the monthly performance of loans
# in terms of total loan amount and number of transactions.
# It uses data from the processed data directory and visualizes it using Matplotlib and Seaborn.
#
# Author: ekastel
# Date: 2025-06-27
#------------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import matplotlib.ticker as mticker

# Path configuration
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Ensure the processed data directory exists
try:
    fact_transactions = pd.read_csv(PROCESSED_DATA_DIR / "fact_transactions.csv")
    dim_time = pd.read_csv(PROCESSED_DATA_DIR / "dim_time.csv")
except FileNotFoundError as e:
    print(f"Error: File not found {e.filename}. Please run the ETL script first.")
    exit()

# Merge facts with the time dimension
time_series_data = pd.merge(fact_transactions, dim_time, on='IDTiempo')

# Create a 'YearMonth' column for proper monthly aggregation and sorting
time_series_data['YearMonth'] = pd.to_datetime(time_series_data['FechaCompleta']).dt.to_period('M')

# Group by month and calculate aggregates
monthly_performance = time_series_data.groupby('YearMonth').agg(
    TotalLoanAmount=('MontoPrestamo', 'sum'),
    NumberOfTransactions=('CantidadTransacciones', 'sum')
).reset_index()

# Convert 'YearMonth' to string for plotting
monthly_performance['YearMonth'] = monthly_performance['YearMonth'].astype(str)

# Set a professional plot style
sns.set_style("whitegrid")
fig, ax1 = plt.subplots(figsize=(14, 7))

# Plot 1: Bar chart for Total Loan Amount (left Y-axis)
color_bars = 'skyblue'
ax1.set_xlabel('Month')
ax1.set_ylabel('Total Loan Amount ($)', color=color_bars, fontsize=12, fontweight='bold')
ax1.bar(monthly_performance['YearMonth'], monthly_performance['TotalLoanAmount'], color=color_bars, label='Total Loan Amount')
ax1.tick_params(axis='y', labelcolor=color_bars)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
plt.xticks(rotation=45)

# Create the second Y-axis that shares the same X-axis
ax2 = ax1.twinx()

# Plot 2: Line chart for Number of Transactions (right Y-axis)
color_line = 'darkorange'
ax2.set_ylabel('Number of Transactions', color=color_line, fontsize=12, fontweight='bold')
ax2.plot(monthly_performance['YearMonth'], monthly_performance['NumberOfTransactions'], color=color_line, marker='o', linestyle='-', linewidth=2, label='Number of Transactions')
ax2.tick_params(axis='y', labelcolor=color_line)

# Final customizations
plt.title('Monthly Loan Performance: Amount vs. Volume', fontsize=16, fontweight='bold')
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
plt.tight_layout() # Adjust layout to make room for labels
plt.show()
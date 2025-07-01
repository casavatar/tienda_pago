# reports/visual_1.py
#------------------------------------------------------------------------
# This script generates an interactive scatter plot to visualize the performance of distributors
# based on the number of active recommended clients and their conversion rates.
#
# Author: ekastel
# Date: 2025-06-27
#------------------------------------------------------------------------

import pandas as pd
import plotly.express as px
from pathlib import Path

# Ensure the script is run from the correct directory
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Load the processed data files
try:
    dim_client = pd.read_csv(PROCESSED_DATA_DIR / "dim_client.csv")
    dim_distributor = pd.read_csv(PROCESSED_DATA_DIR / "dim_distributor.csv")
    fact_transactions = pd.read_csv(PROCESSED_DATA_DIR / "fact_transactions.csv")
except FileNotFoundError as e:
    print(f"Error: File not found {e.filename}. Please run the ETL script first.")
    exit()

# Filter for recommended clients only
recommended_clients = dim_client[dim_client['EsRecomendado'] == True]

# Total number of recommended clients for each distributor
total_recommended_per_distributor = recommended_clients.groupby('IDDISTRIBUIDOR').size().reset_index(name='TotalRecommended')

# Join transactions with client info to filter by recommended status
recommended_transactions = pd.merge(fact_transactions, recommended_clients, on='IDCLIENTE')

# Group by distributor to calculate performance metrics
distributor_performance = recommended_transactions.groupby('IDDISTRIBUIDOR').agg(
    RecommendedAmount=('MontoPrestamo', 'sum'),
    ActiveRecommendedClients=('IDCLIENTE', 'nunique')
).reset_index()

# Join all metrics into a final performance table
final_performance = pd.merge(distributor_performance, total_recommended_per_distributor, on='IDDISTRIBUIDOR', how='left')
final_performance = pd.merge(final_performance, dim_distributor, on='IDDISTRIBUIDOR')

# Safely calculate the conversion rate
final_performance['ConversionRate'] = (final_performance['ActiveRecommendedClients'] / final_performance['TotalRecommended']).fillna(0)

# Ensure the conversion rate is a percentage
fig = px.scatter(
    final_performance,
    x="ActiveRecommendedClients",
    y="ConversionRate",
    size="RecommendedAmount",
    color="NombreDistribuidor",
    hover_name="NombreDistribuidor",
    text="NombreDistribuidor",  # Display the name on the bubble
    size_max=60, # Adjust the max size of the bubbles
    template="plotly_white" # A clean, professional theme
)

# Customize the plot for better readability
fig.update_traces(textposition='top center') # Set text position
fig.update_layout(
    title_text="<b>Strategic Distributor Performance</b>",
    xaxis_title="<b>Active Recommended Clients</b> (Volume)",
    yaxis_title="<b>Conversion Rate</b> (Effectiveness)",
    yaxis_tickformat=".0%", # Format Y-axis as percentage
    legend_title="<b>Distributors</b>",
    showlegend=False # Hide legend since names are on the bubbles
)

print("Showing interactive plot...")
fig.show()
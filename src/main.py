# src/main.py
#--------------------------------------------------------------------------------
# Main ETL pipeline for processing client recommendations and transactions.
# This script orchestrates the entire ETL process, including data extraction,
# transformation, and loading into the appropriate data structures.
#
# author: ekastel
# date: 2025-06-27
#--------------------------------------------------------------------------------

import os
import pandas as pd
from config import (
    RECOMMENDATIONS_JSON_FILE, CLIENTS_EXCEL_FILE,
    DIM_CLIENT_FILE, DIM_DISTRIBUTOR_FILE, DIM_TIME_FILE, FACT_TRANSACTIONS_FILE
)
import loader
import transformer
import writer

def main():
    """Main ETL pipeline function."""
    print("--- Starting ETL Process ---")

    # --- EXTRACT ---
    reco_df = loader.load_recommendations_data(RECOMMENDATIONS_JSON_FILE)
    if reco_df.empty:
        print("ETL process halted due to missing recommendations data.")
        return

    # Check for mock data creation
    if not os.path.exists(CLIENTS_EXCEL_FILE):
        unique_client_ids = reco_df['IDCLIENTE'].unique().tolist()
        loader.create_mock_excel_data(CLIENTS_EXCEL_FILE, unique_client_ids)
    
    clients_df, transactions_df = loader.load_clients_and_transactions(CLIENTS_EXCEL_FILE)
    if clients_df.empty or transactions_df.empty:
        print("ETL process halted due to missing client/transaction data.")
        return

    # --- TRANSFORM ---
    cleaned_reco_df = transformer.clean_recommendations_data(reco_df)
    
    # Create Dimensions
    dim_distributor = transformer.create_distributor_dimension(cleaned_reco_df)
    dim_client = transformer.create_client_dimension(clients_df, cleaned_reco_df)
    dim_time = transformer.create_time_dimension(transactions_df['FECHA'])
    
    # Create Fact Table
    fact_transactions = transformer.create_fact_table(transactions_df, dim_client, dim_time)
    
    # For the final client dimension, we only need the client attributes, not the distributor FK
    dim_client_final = dim_client[['IDCLIENTE', 'CategoriaCliente', 'EsRecomendado']]

    # --- LOAD ---
    writer.save_to_csv(dim_client_final, DIM_CLIENT_FILE)
    writer.save_to_csv(dim_distributor, DIM_DISTRIBUTOR_FILE)
    writer.save_to_csv(dim_time, DIM_TIME_FILE)
    writer.save_to_csv(fact_transactions, FACT_TRANSACTIONS_FILE)

    print("--- ETL Process Completed Successfully ---")


if __name__ == "__main__":
    main()
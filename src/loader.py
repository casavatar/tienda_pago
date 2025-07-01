# src/loader.py
#--------------------------------------------------------------------------------------------------------
# This module provides functions to load client recommendation data from a JSON file
# and client/transaction data from an Excel file. It also includes a function to create mock
# data for demonstration purposes.
#
# author: ekastel
# date: 2025-06-27
#--------------------------------------------------------------------------------------------------------

import pandas as pd
import numpy as np

# Function to load recommendations data
def load_recommendations_data(file_path):
    """Loads client recommendation data from a JSON file."""
    print(f"Loading recommendations from {file_path}...")
    try:
        df = pd.read_json(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: Recommendations JSON file not found at {file_path}")
        return pd.DataFrame()

# Function to load clients and transactions data
def load_clients_and_transactions(file_path):
    """Loads clients and transactions data from an Excel file."""
    print(f"Loading clients and transactions from {file_path}...")
    try:
        clients_df = pd.read_excel(file_path, sheet_name="CLIENTES")
        transactions_df = pd.read_excel(file_path, sheet_name="TRANSACCIONES")
        return clients_df, transactions_df
    except FileNotFoundError:
        print(f"Error: Excel file not found at {file_path}")
        # Return empty dataframes with expected columns to avoid downstream errors
        return pd.DataFrame(columns=['IDCLIENTE']), pd.DataFrame(columns=['IDCLIENTE', 'FECHA', 'MONTO_PRESTAMO'])
    except ValueError as e:
        print(f"Error loading sheets from Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Function to create mock Excel data
def create_mock_excel_data(file_path, client_ids_from_json):
    """Creates a mock Excel file for demonstration purposes."""
    print("Creating mock Excel data as source file was not provided...")
    
    # Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Create Mock Clients Data ---
    client_categories = {
        'IDCLIENTE': client_ids_from_json,
        'categoría': np.random.choice(['Oro', 'Platino', 'Cobre'], size=len(client_ids_from_json))
    }
    mock_clients_df = pd.DataFrame(client_categories)
    
    # --- Create Mock Transactions Data ---
    num_transactions = 500
    mock_transactions = {
        'IDCLIENTE': np.random.choice(client_ids_from_json, size=num_transactions),
        'FECHA': pd.to_datetime(pd.to_datetime('2024-01-01') + pd.to_timedelta(np.random.randint(0, 365, size=num_transactions), unit='d')),
        'MONTO_PRESTAMO': np.random.uniform(500, 10000, size=num_transactions).round(2)
    }
    mock_transactions_df = pd.DataFrame(mock_transactions)

    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        mock_clients_df.to_excel(writer, sheet_name='CLIENTES', index=False)
        mock_transactions_df.to_excel(writer, sheet_name='TRANSACCIONES', index=False)
    
    print(f"Mock Excel file created at {file_path}")
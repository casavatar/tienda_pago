# src/transformer.py
#-------------------------------------------------------------------------------
# description: This module contains functions to transform raw data into structured 
# dimensions and fact tables.
#
# author: ekastel
# date: 2025-06-27
#-------------------------------------------------------------------------------

import pandas as pd

# Function to clean and transform the raw data into structured dimensions and fact tables
def clean_recommendations_data(df):
    """Cleans the recommendations dataframe by handling duplicates and types."""
    print("Cleaning recommendations data...")
    # Drop records with duplicated IDCLIENTE, keeping the first entry
    df.drop_duplicates(subset='IDCLIENTE', keep='first', inplace=True)
    df['recomendados'] = df['recomendados'].astype(bool)
    return df

# Function to clean and transform the clients data
def create_distributor_dimension(recommendations_df):
    """Creates the distributor dimension table."""
    print("Creating Distributor Dimension...")
    dist_df = recommendations_df[['IDDISTRIBUIDOR', 'NOMBRE DISTRIBUIDOR', 'TELEFONO']].copy()
    dist_df.drop_duplicates(subset='IDDISTRIBUIDOR', keep='first', inplace=True)
    dist_df.rename(columns={'NOMBRE DISTRIBUIDOR': 'NombreDistribuidor', 'TELEFONO': 'Telefono'}, inplace=True)
    return dist_df

# Function to clean and transform the clients data
def create_client_dimension(clients_df, recommendations_df):
    """Creates the client dimension table by merging client and recommendation data."""
    print("Creating Client Dimension...")
    # Merge to add recommendation status to each client
    merged_df = pd.merge(clients_df, recommendations_df[['IDCLIENTE', 'recomendados', 'IDDISTRIBUIDOR']], on='IDCLIENTE', how='left')
    # Fill NaN for clients that were not in the recommendations file
    merged_df['recomendados'] = merged_df['recomendados'].fillna(False)
    merged_df.rename(columns={'categoría': 'CategoriaCliente', 'recomendados': 'EsRecomendado'}, inplace=True)
    return merged_df[['IDCLIENTE', 'IDDISTRIBUIDOR', 'CategoriaCliente', 'EsRecomendado']]

# Function to create the time dimension from a series of dates
def create_time_dimension(date_series):
    """Creates the time dimension from a series of dates."""
    print("Creating Time Dimension...")
    df = pd.DataFrame({'FechaCompleta': date_series.unique()})
    df['FechaCompleta'] = pd.to_datetime(df['FechaCompleta'])
    df['IDTiempo'] = df['FechaCompleta'].dt.strftime('%Y%m%d').astype(int)
    df['Año'] = df['FechaCompleta'].dt.year
    df['Mes'] = df['FechaCompleta'].dt.month
    df['Dia'] = df['FechaCompleta'].dt.day
    df.drop_duplicates(inplace=True)
    return df

# Function to create the main fact table for transactions
def create_fact_table(transactions_df, client_dim_df, time_dim_df):
    """Creates the main fact table for transactions."""
    print("Creating Transactions Fact Table...")
    # Merge with client dimension to get foreign keys
    fact_df = pd.merge(transactions_df, client_dim_df, on='IDCLIENTE')
    
    # Ensure transaction dates are clean datetime objects for merging
    fact_df['FECHA'] = pd.to_datetime(fact_df['FECHA'])
    
    # Merge with time dimension to get the time key
    fact_df = pd.merge(fact_df, time_dim_df[['FechaCompleta', 'IDTiempo']], left_on='FECHA', right_on='FechaCompleta')
    
    # Select and rename columns for the final fact table
    fact_df = fact_df[['IDTiempo', 'IDCLIENTE', 'IDDISTRIBUIDOR', 'MONTO_PRESTAMO']].copy()
    fact_df.rename(columns={'MONTO_PRESTAMO': 'MontoPrestamo'}, inplace=True)
    
    # Add a transaction count for easy aggregation
    fact_df['CantidadTransacciones'] = 1
    
    return fact_df
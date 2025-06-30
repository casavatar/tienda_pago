# src/config.py
#--------------------------------------------------------------------------------------
# Configuration file for data processing paths and filenames.
# This file defines the base directory and paths for raw and processed data,
# as well as the input and output filenames used in the data processing pipeline.
#
# Author: ekastel
# Date: 2025-06-27
#---------------------------------------------------------------------------------------

from pathlib import Path

# Project Base Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Data Directories
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Input Filenames
RECOMMENDATIONS_JSON_FILE = RAW_DATA_DIR / "RecomendadosMarca.json"
CLIENTS_EXCEL_FILE = RAW_DATA_DIR / "ClientesMarca.xls"

# Output Filenames
DIM_CLIENT_FILE = PROCESSED_DATA_DIR / "dim_client.csv"
DIM_DISTRIBUTOR_FILE = PROCESSED_DATA_DIR / "dim_distributor.csv"
DIM_TIME_FILE = PROCESSED_DATA_DIR / "dim_time.csv"
FACT_TRANSACTIONS_FILE = PROCESSED_DATA_DIR / "fact_transactions.csv"
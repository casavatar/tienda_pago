# reports/GenerateExcelReport.py
#-----------------------------------------------------------------------------------
# This script generates an Excel report summarizing the performance of distributors
# based on recommended clients and their transactions.
# It includes a detailed transaction report and a summary with a bar chart.
#
# Author: ekastel
# Date: 2025-06-27
#-----------------------------------------------------------------------------------

import pandas as pd
from pathlib import Path


print("Loading processed data...")
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

try:
    dim_client = pd.read_csv(PROCESSED_DATA_DIR / "dim_client.csv")
    dim_distributor = pd.read_csv(PROCESSED_DATA_DIR / "dim_distributor.csv")
    dim_time = pd.read_csv(PROCESSED_DATA_DIR / "dim_time.csv")
    fact_transactions = pd.read_csv(PROCESSED_DATA_DIR / "fact_transactions.csv")
except FileNotFoundError as e:
    print(f"Error: File not found {e.filename}. Please run the ETL script first.")
    exit()

print("Preparing detailed transaction data for recommended clients...")

# Filter for recommended clients only
recommended_clients = dim_client[dim_client['EsRecomendado'] == True]

# Merge all tables to create a comprehensive dataset
report_data = pd.merge(fact_transactions, recommended_clients, on='IDCLIENTE')
report_data = pd.merge(report_data, dim_distributor, on='IDDISTRIBUIDOR')
report_data = pd.merge(report_data, dim_time, on='IDTiempo')

# Select and rename columns for the final detailed report
detailed_report = report_data[[
    'NombreDistribuidor',
    'IDCLIENTE',
    'CategoriaCliente',
    'FechaCompleta',
    'MontoPrestamo'
]].rename(columns={
    'NombreDistribuidor': 'Distributor Name',
    'IDCLIENTE': 'Client ID',
    'CategoriaCliente': 'Client Category',
    'FechaCompleta': 'Transaction Date',
    'MontoPrestamo': 'Loan Amount'
})

print("Creating summary data by distributor...")

summary_report = detailed_report.groupby('Distributor Name').agg(
    TotalLoanAmount=('Loan Amount', 'sum'),
    NumberOfTransactions=('Loan Amount', 'count'),
    UniqueClients=('Client ID', 'nunique')
).sort_values(by='TotalLoanAmount', ascending=False)

summary_report['AverageLoanAmount'] = summary_report['TotalLoanAmount'] / summary_report['NumberOfTransactions']


# Reset index to make 'Distributor Name' a column
output_filename = 'Distributor_Recommendation_Report.xlsx'
print(f"Writing data to Excel file: {output_filename}...")

with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
    # Write dataframes to different sheets
    summary_report.to_excel(writer, sheet_name='Summary')
    detailed_report.to_excel(writer, sheet_name='Detailed Transactions', index=False)

    # Get the xlsxwriter workbook and worksheet objects
    workbook  = writer.book
    summary_sheet = writer.sheets['Summary']
    details_sheet = writer.sheets['Detailed Transactions']

    # Define formats
    currency_format = workbook.add_format({'num_format': '$#,##0.00'})
    integer_format = workbook.add_format({'num_format': '#,##0'})
    header_format = workbook.add_format({'bold': True, 'bg_color': '#DDEBF7', 'border': 1})

    # Format headers
    for col_num, value in enumerate(summary_report.columns.values):
        summary_sheet.write(0, col_num + 1, value, header_format)
    
    # Format columns in Summary sheet
    summary_sheet.set_column('A:A', 25) # Distributor Name
    summary_sheet.set_column('B:B', 20, currency_format) # TotalLoanAmount
    summary_sheet.set_column('C:C', 22, integer_format) # NumberOfTransactions
    summary_sheet.set_column('D:D', 15, integer_format) # UniqueClients
    summary_sheet.set_column('E:E', 22, currency_format) # AverageLoanAmount

    # Format columns in Details sheet
    for col_num, value in enumerate(detailed_report.columns.values):
        details_sheet.write(0, col_num, value, header_format)
    details_sheet.set_column('A:A', 25) # Distributor Name
    details_sheet.set_column('E:E', 15, currency_format) # Loan Amount


    # --- Create a Bar Chart ---
    chart = workbook.add_chart({'type': 'bar'})
    
    # Configure the series. Note: The ranges are 1-based [sheet, row_start, col_start, row_end, col_end]
    num_distributors = len(summary_report)
    chart.add_series({
        'name':       'Total Loan Amount',
        'categories': ['Summary', 1, 0, num_distributors, 0], # Column A for names
        'values':     ['Summary', 1, 1, num_distributors, 1], # Column B for values
    })

    chart.set_title({'name': 'Total Loan Amount by Distributor'})
    chart.set_x_axis({'name': 'Distributor'})
    chart.set_y_axis({'name': 'Total Loan Amount ($)'})
    chart.get_legend().set_position('none')
    
    # Insert the chart into the worksheet.
    summary_sheet.insert_chart('G3', chart)

print(f"\nReport '{output_filename}' generated successfully.")
print("It contains a summary with a chart and a detailed transaction list.")
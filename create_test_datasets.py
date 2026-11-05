"""
create_test_datasets.py

Generates realistic test datasets for Crystallytics across multiple file formats
(.csv, .xlsx, .xls) and distinct business/scientific domains.

Datasets:
  1. messy_customer_churn.csv   - Dirty data with duplicates, missing cells, outliers, whitespace
  2. healthcare_vitals.xlsx     - Modern Excel file in Healthcare/Clinical domain
  3. employee_workforce.xls     - Legacy Excel 97-2004 (.xls) format in HR domain
  4. ecommerce_transactions.csv - Multi-month retail transactions with discounts & dates
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

print("Creating test datasets in:", DATA_DIR)

# ── 1. MESSY CUSTOMER CHURN (CSV) ─────────────────────────────────────────────
# Purpose: Specifically crafted to showcase 1-Click Data Cleaning (dupes, missing, outliers, whitespace)
messy_data = {
    "CustomerID": [
        "CUST-101", "CUST-102", "CUST-103", "CUST-104", "CUST-105",
        "CUST-106", "CUST-107", "CUST-108", "CUST-109", "CUST-110",
        "CUST-111", "CUST-112", "CUST-113", "CUST-114", "CUST-115",
        "CUST-116", "CUST-117", "CUST-118", "CUST-119", "CUST-120",
        # Deliberate duplicates to test deduplication
        "CUST-102", "CUST-107", "CUST-115",
        "CUST-121", "CUST-122", "CUST-123", "CUST-124", "CUST-125",
        "CUST-126", "CUST-127"
    ],
    "ContractType": [
        "Month-to-Month", " One Year ", "Two Year", "Month-to-Month", "Two Year",
        "Month-to-Month", " One Year ", "Month-to-Month", "Two Year", "Month-to-Month",
        " One Year ", "Two Year", "Month-to-Month", "Two Year", "Month-to-Month",
        " One Year ", "Month-to-Month", "Two Year", "Month-to-Month", " One Year ",
        # dupes
        " One Year ", " One Year ", "Month-to-Month",
        "Two Year", "Month-to-Month", " One Year ", "Two Year", "Month-to-Month",
        "Two Year", "Month-to-Month"
    ],
    "TenureMonths": [
        1, 12, 24, 2, 36,
        6, 18, 3, 48, 4,
        14, np.nan, 2, 60, 5,  # missing value at index 11
        22, 1, 30, 8, 16,
        # dupes
        12, 18, 5,
        42, 3, 20, 55, np.nan,  # missing value at index 27
        38, 9
    ],
    "MonthlyCharges": [
        65.50, 45.00, 85.20, 70.00, 95.00,
        55.40, 60.10, 75.80, 110.00, 40.50,
        72.00, 88.50, np.nan, 99.00, 65.00,  # missing value at index 12
        58.20, 69.40, 82.00, 50.00, 64.50,
        # dupes
        45.00, 60.10, 65.00,
        105.00, 49.50, 78.00, 92.50, 62.00,
        12500.00,  # EXTREME OUTLIER to test 1.5xIQR winsorization!
        68.00
    ],
    "SupportTickets": [
        3, 0, 1, 4, 0,
        2, 1, 5, 0, 1,
        2, 0, 4, 1, 3,
        1, 6, 0, 2, 1,
        # dupes
        0, 1, 3,
        0, 3, 1, 0, 2,
        1, 2
    ],
    "SatisfactionScore": [
        3.2, 4.5, 4.8, 2.1, 4.9,
        3.8, 4.2, 1.9, 4.7, 3.5,
        4.0, 4.6, 2.4, 4.9, 3.1,
        4.3, 1.8, 4.5, 3.6, 4.1,
        # dupes
        4.5, 4.2, 3.1,
        4.8, 3.0, 4.2, 4.9, np.nan,  # missing
        4.4, 3.7
    ],
    "Churn": [
        "Yes", "No", "No", "Yes", "No",
        "Yes", "No", "Yes", "No", "No",
        "No", "No", "Yes", "No", "Yes",
        "No", "Yes", "No", "No", "No",
        # dupes
        "No", "No", "Yes",
        "No", "Yes", "No", "No", "No",
        "No", "No"
    ]
}

df_messy = pd.DataFrame(messy_data)
csv_path = os.path.join(DATA_DIR, "messy_customer_churn.csv")
df_messy.to_csv(csv_path, index=False)
print(f"  [OK] Created: {csv_path} ({len(df_messy)} rows, 7 cols - contains dupes, nulls & outliers)")


# ── 2. HEALTHCARE PATIENT VITALS (XLSX) ─────────────────────────────────────────
# Purpose: High quality multi-column modern Excel dataset triggering Healthcare domain
healthcare_data = {
    "PatientID": [f"PT-{2000 + i}" for i in range(1, 31)],
    "Age": [
        45, 52, 29, 61, 38, 70, 55, 42, 33, 67,
        48, 59, 25, 73, 51, 36, 64, 41, 57, 30,
        68, 47, 53, 39, 62, 28, 75, 44, 58, 35
    ],
    "Gender": [
        "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male",
        "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male",
        "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male", "Female", "Male"
    ],
    "BloodPressure_Systolic": [
        122, 138, 115, 145, 120, 150, 132, 124, 118, 142,
        128, 136, 112, 155, 130, 121, 140, 125, 135, 116,
        148, 126, 134, 122, 144, 114, 158, 127, 137, 119
    ],
    "HeartRate_BPM": [
        72, 80, 68, 85, 74, 88, 76, 70, 65, 82,
        75, 79, 66, 90, 77, 71, 83, 73, 78, 67,
        86, 74, 78, 72, 84, 69, 92, 75, 81, 70
    ],
    "Cholesterol_mgDL": [
        195, 220, 175, 240, 185, 255, 210, 190, 168, 230,
        205, 215, 160, 260, 200, 180, 235, 192, 218, 172,
        245, 198, 212, 188, 238, 165, 265, 202, 225, 178
    ],
    "Diagnosis": [
        "Normal", "Hypertension", "Normal", "Hypertension", "Normal",
        "Cardiovascular", "Hypertension", "Normal", "Normal", "Hypertension",
        "Normal", "Hypertension", "Normal", "Cardiovascular", "Hypertension",
        "Normal", "Hypertension", "Normal", "Hypertension", "Normal",
        "Cardiovascular", "Normal", "Hypertension", "Normal", "Hypertension",
        "Normal", "Cardiovascular", "Normal", "Hypertension", "Normal"
    ],
    "HospitalStayDays": [
        1, 3, 1, 4, 2, 7, 3, 2, 1, 5,
        2, 3, 1, 8, 3, 2, 4, 2, 3, 1,
        6, 2, 3, 2, 4, 1, 9, 2, 4, 1
    ]
}

df_health = pd.DataFrame(healthcare_data)
xlsx_path = os.path.join(DATA_DIR, "healthcare_vitals.xlsx")
with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    df_health.to_excel(writer, sheet_name="PatientRecords", index=False)
print(f"  [OK] Created: {xlsx_path} ({len(df_health)} rows, 8 cols - Modern Excel format)")


# ── 3. EMPLOYEE WORKFORCE (XLS - Legacy BIFF8 format) ──────────────────────────
# Purpose: Validates legacy Excel 97-2004 (.xls) file loading and HR domain inference
hr_data = {
    "EmployeeID": [f"EMP-{100 + i}" for i in range(1, 26)],
    "Department": [
        "Engineering", "Sales", "Marketing", "Engineering", "Human Resources",
        "Finance", "Engineering", "Sales", "Marketing", "Finance",
        "Engineering", "Sales", "Human Resources", "Engineering", "Marketing",
        "Finance", "Engineering", "Sales", "Engineering", "Finance",
        "Marketing", "Human Resources", "Engineering", "Sales", "Engineering"
    ],
    "JobRole": [
        "Senior Developer", "Account Exec", "Content Strategist", "Lead Architect", "HR Generalist",
        "Financial Analyst", "DevOps Engineer", "Sales Director", "SEO Specialist", "Controller",
        "Frontend Dev", "Sales Rep", "HR Business Partner", "Backend Dev", "Brand Manager",
        "Auditor", "Staff Engineer", "BDR Specialist", "QA Automation", "Senior Accountant",
        "Growth Manager", "Talent Recruiter", "Cloud Architect", "Account Exec", "VP Engineering"
    ],
    "YearsExperience": [
        6, 4, 3, 10, 4,
        5, 7, 12, 3, 8,
        2, 1, 7, 5, 6,
        4, 9, 2, 4, 6,
        5, 3, 11, 4, 15
    ],
    "SalaryUSD": [
        115000, 85000, 72000, 160000, 68000,
        92000, 125000, 155000, 70000, 130000,
        82000, 58000, 95000, 110000, 98000,
        88000, 145000, 62000, 86000, 105000,
        96000, 75000, 165000, 88000, 210000
    ],
    "PerformanceRating": [
        4.6, 4.1, 4.3, 4.9, 4.2,
        4.4, 4.7, 4.8, 4.0, 4.5,
        3.9, 3.8, 4.4, 4.5, 4.3,
        4.2, 4.8, 3.9, 4.1, 4.4,
        4.3, 4.2, 4.9, 4.2, 5.0
    ],
    "ProjectsCompleted": [
        14, 22, 11, 28, 8,
        15, 19, 35, 12, 18,
        6, 8, 14, 16, 17,
        13, 25, 9, 12, 16,
        15, 10, 31, 18, 40
    ],
    "RemoteStatus": [
        "Remote", "Hybrid", "Hybrid", "Remote", "On-Site",
        "Hybrid", "Remote", "Remote", "Hybrid", "On-Site",
        "Hybrid", "On-Site", "Hybrid", "Remote", "Hybrid",
        "On-Site", "Remote", "On-Site", "Remote", "Hybrid",
        "Hybrid", "Hybrid", "Remote", "Hybrid", "Remote"
    ]
}

df_hr = pd.DataFrame(hr_data)
xls_path = os.path.join(DATA_DIR, "employee_workforce.xls")

# Use xlwt to write genuine legacy BIFF8 format .xls file
import xlwt
wb = xlwt.Workbook(encoding="utf-8")
ws = wb.add_sheet("WorkforceData")

# Write headers with styling
header_style = xlwt.easyxf('font: bold on, color blue; borders: bottom thin')
for col_idx, col_name in enumerate(df_hr.columns):
    ws.write(0, col_idx, col_name, header_style)

# Write data rows
for row_idx, row in df_hr.iterrows():
    for col_idx, val in enumerate(row):
        ws.write(row_idx + 1, col_idx, val)

wb.save(xls_path)
print(f"  [OK] Created: {xls_path} ({len(df_hr)} rows, 8 cols - Legacy BIFF8 .xls format)")


# ── 4. E-COMMERCE TRANSACTIONS (CSV) ──────────────────────────────────────────
# Purpose: High volume retail sales over time, ideal for time series and aggregations
np.random.seed(42)
categories = {
    "Electronics": [("Noise Cancelling Headphones", 149.99), ("UltraWide Monitor", 349.99), ("Mechanical Keyboard", 89.99)],
    "Office Furniture": [("Ergonomic Mesh Chair", 229.00), ("Standing Desk Pro", 489.00), ("Desk Lamp LED", 39.50)],
    "Accessories": [("Wireless Mouse", 29.99), ("USB-C Docking Station", 79.99), ("Webcam 1080p", 59.99)]
}

dates = pd.date_range(start="2024-01-01", end="2024-04-15", periods=36)
ecom_rows = []
for i, date in enumerate(dates):
    cat = np.random.choice(list(categories.keys()))
    prod, price = categories[cat][np.random.choice(len(categories[cat]))]
    qty = int(np.random.randint(1, 8))
    discount = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20]))
    total = round(qty * price * (1 - discount), 2)
    region = np.random.choice(["North America", "Europe", "Asia-Pacific", "Latin America"])
    payment = np.random.choice(["Credit Card", "PayPal", "Apple Pay", "Wire Transfer"])
    
    ecom_rows.append({
        "TransactionID": f"TRX-{5000 + i}",
        "Date": date.strftime("%Y-%m-%d"),
        "Category": cat,
        "Product": prod,
        "UnitPrice": price,
        "Quantity": qty,
        "Discount": discount,
        "TotalAmount": total,
        "Region": region,
        "PaymentMethod": payment
    })

df_ecom = pd.DataFrame(ecom_rows)
ecom_path = os.path.join(DATA_DIR, "ecommerce_transactions.csv")
df_ecom.to_csv(ecom_path, index=False)
print(f"  [OK] Created: {ecom_path} ({len(df_ecom)} rows, 10 cols - Retail & Time-Series)")

print("\nAll 4 test datasets created successfully!")

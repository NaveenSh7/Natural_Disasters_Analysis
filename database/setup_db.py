import pandas as pd
import sqlite3

# Load CSV

df = pd.read_csv("../data/disasters_2010_2025.csv")

# --- Basic Cleaning ---
# Ensure dates are parsed
df["Start_Date"] = pd.to_datetime(df["Start_Date"], errors="coerce")
df["End_Date"] = pd.to_datetime(df["End_Date"], errors="coerce")

# Fill missing values where needed
df["Fatalities"] = df["Fatalities"].fillna(0).astype(int)
df["Affected"] = df["Affected"].fillna(0).astype(int)

# --- Keep Top 10 Disaster Types ---
top10 = df["Disaster_Type"].value_counts().nlargest(10).index
df["Disaster_Type"] = df["Disaster_Type"].apply(lambda x: x if x in top10 else "Others")

# --- Save cleaned dataset back to SQLite ---
conn = sqlite3.connect("disasters.db")
df.to_sql("disasters", conn, if_exists="replace", index=False)
conn.close()

print("✅ Cleaning complete. Saved to SQLite with Top 10 Disaster Types + Others.")


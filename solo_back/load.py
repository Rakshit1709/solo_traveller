import pandas as pd
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user=("root"),
            password=("admin@123"),
            database=("solo"),
            ssl_disabled =True
        )
        return conn
    except Error as e:
        print("Error connecting to MySQL", e)
        return None

df = pd.read_excel("places.xlsx")

# Basic cleanup
df = df.rename(columns=lambda c: c.strip())
df['tags'] = df['tags'].fillna('').astype(str)
df['description'] = df['description'].fillna('')
df['google_rating'] = pd.to_numeric(df['Google Rating'], errors='coerce').fillna(0)
df['entrance_fee_inr'] = pd.to_numeric(df['Entrance Fee (INR)'], errors='coerce').fillna(0)
df['time_needed_hours'] = pd.to_numeric(df['Time Needed (hrs)'], errors='coerce').fillna(1)

# Normalize boolean-like fields
df['airport_within_50km'] = df['Airport within 50km'].astype(str).str.lower().isin(['yes','y','true','1'])
df['dslr_allowed'] = df['DSLR Allowed'].astype(str).str.lower().isin(['yes','y','true','1'])

insert_sql = """
INSERT INTO places
(name, state, city, type, establishment_year, time_needed_hours,
 google_rating, entrance_fee_inr, airport_within_50km, weekly_off,
 significance, dslr_allowed, reviews_lakhs, best_time_to_visit, description, tags)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

conn = get_db_connection()
cursor = conn.cursor()

for _, row in df.iterrows():
    vals = (
        row.get('Name'),
        row.get('State'),
        row.get('City'),
        row.get('Type'),
        int(row.get('Establishment Year')) if not pd.isna(row.get('Establishment Year')) else None,
        float(row['time_needed_hours']),
        float(row['google_rating']),
        float(row['entrance_fee_inr']),
        int(row['airport_within_50km']),
        row.get('Weekly Off'),
        row.get('Significance'),
        int(row['dslr_allowed']),
        float(row.get('Reviews (lakhs)') if not pd.isna(row.get('Reviews (lakhs)')) else 0),
        row.get('Best Time to Visit'),
        row.get('description'),
        row.get('tags')
    )
    cursor.execute(insert_sql, vals)

conn.commit()
cursor.close()
conn.close()
print("Loaded", len(df), "rows into places")

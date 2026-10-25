import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# ---------------------------------------------------------
# 1. LOAD CREDENTIALS FROM .env (never hardcode these)
# ---------------------------------------------------------
load_dotenv('../.env')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# ---------------------------------------------------------
# 2. LOAD CLEANED CSVs
# ---------------------------------------------------------
campaign = pd.read_csv('../data/processed/campaign_clean.csv')
touchpoints = pd.read_csv('../data/processed/touchpoints_clean.csv')

print("Loaded from CSV -> campaign:", campaign.shape, "| touchpoints:", touchpoints.shape)

# ---------------------------------------------------------
# STANDARDIZE COLUMN NAMES (lowercase, snake_case, no spaces)
# ---------------------------------------------------------
campaign.columns = campaign.columns.str.strip().str.lower().str.replace(' ', '_')
touchpoints.columns = touchpoints.columns.str.strip().str.lower().str.replace(' ', '_')

# rename reserved-word-ish columns to avoid SQL confusion
campaign = campaign.rename(columns={'date': 'campaign_date'})
touchpoints = touchpoints.rename(columns={'timestamp': 'touch_time'})

print("Campaign columns:", list(campaign.columns))
print("Touchpoint columns:", list(touchpoints.columns))

# ---------------------------------------------------------
# 3. PUSH TO POSTGRES (replace tables if they already exist)
# ---------------------------------------------------------
campaign.to_sql('campaigns', engine, if_exists='replace', index=False)
touchpoints.to_sql('touchpoints', engine, if_exists='replace', index=False)

print("Tables written to PostgreSQL.")

# ---------------------------------------------------------
# 4. VERIFY: row counts straight from the database
# ---------------------------------------------------------
with engine.connect() as conn:
    from sqlalchemy import text
    campaign_count = conn.execute(text("SELECT COUNT(*) FROM campaigns")).scalar()
    touchpoint_count = conn.execute(text("SELECT COUNT(*) FROM touchpoints")).scalar()

print(f"campaigns table row count: {campaign_count}")
print(f"touchpoints table row count: {touchpoint_count}")
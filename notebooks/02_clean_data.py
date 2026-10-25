import pandas as pd
import numpy as np

# ---------------------------------------------------------
# 1. LOAD RAW DATA
# ---------------------------------------------------------
campaign = pd.read_csv('../data/raw/marketing_campaign_dataset.csv')
touchpoints = pd.read_csv('../data/raw/multi_touch_attribution_data.csv')

print("Raw shapes -> campaign:", campaign.shape, "| touchpoints:", touchpoints.shape)

# ---------------------------------------------------------
# 2. CHANNEL MAPPING (documented assumption)
# ---------------------------------------------------------
channel_map = {
    'Facebook': 'Social Media',
    'Instagram': 'Social Media',
    'YouTube': 'Display Ads',
    'Google Ads': 'Search Ads',
    'Website': 'Direct Traffic',
    'Email': 'Email'
}
campaign['Channel_Standardized'] = campaign['Channel_Used'].map(channel_map)

# touchpoint channels already use the target taxonomy, but pass through
# a mapping dict too so both sides are built the same way (defensive coding)
touchpoint_channel_map = {
    'Direct Traffic': 'Direct Traffic',
    'Display Ads': 'Display Ads',
    'Email': 'Email',
    'Referral': 'Referral',
    'Search Ads': 'Search Ads',
    'Social Media': 'Social Media'
}
touchpoints['Channel_Standardized'] = touchpoints['Channel'].map(touchpoint_channel_map)

# sanity check: did anything fail to map?
assert campaign['Channel_Standardized'].isnull().sum() == 0, "Unmapped channel in campaign data!"
assert touchpoints['Channel_Standardized'].isnull().sum() == 0, "Unmapped channel in touchpoint data!"

# ---------------------------------------------------------
# 3. CLEAN CAMPAIGN DATASET
# ---------------------------------------------------------
# Acquisition_Cost is text like "$16,174.00" -> convert to float
campaign['Spend'] = (
    campaign['Acquisition_Cost']
    .str.replace('$', '', regex=False)
    .str.replace(',', '', regex=False)
    .astype(float)
)

# Revenue = Cost * (1 + ROI)  -- documented assumption, see README
campaign['Revenue'] = campaign['Spend'] * (1 + campaign['ROI'])

# Estimated conversions = conversion rate * clicks
campaign['Conversions'] = (campaign['Conversion_Rate'] * campaign['Clicks']).round().astype(int)

# Standard KPIs
campaign['CTR'] = campaign['Clicks'] / campaign['Impressions']
campaign['CPC'] = campaign['Spend'] / campaign['Clicks']
campaign['CPM'] = (campaign['Spend'] / campaign['Impressions']) * 1000
campaign['CAC'] = campaign['Spend'] / campaign['Conversions'].replace(0, np.nan)

# Parse date, extract useful parts
campaign['Date'] = pd.to_datetime(campaign['Date'])
campaign['Month'] = campaign['Date'].dt.to_period('M').astype(str)

# Duplicate check
dupe_count = campaign.duplicated(subset='Campaign_ID').sum()
print(f"Duplicate Campaign_IDs: {dupe_count}")
campaign = campaign.drop_duplicates(subset='Campaign_ID')

# Outlier flag on Spend (basic IQR method) - flagged, not removed
Q1, Q3 = campaign['Spend'].quantile([0.25, 0.75])
IQR = Q3 - Q1
campaign['Spend_Outlier'] = (
    (campaign['Spend'] < Q1 - 1.5*IQR) | (campaign['Spend'] > Q3 + 1.5*IQR)
)
print(f"Spend outliers flagged: {campaign['Spend_Outlier'].sum()} rows (kept, just flagged)")

# ---------------------------------------------------------
# 4. CLEAN TOUCHPOINT DATASET
# ---------------------------------------------------------
touchpoints['Timestamp'] = pd.to_datetime(touchpoints['Timestamp'])
touchpoints['Converted'] = (touchpoints['Conversion'] == 'Yes').astype(int)
touchpoints['Campaign'] = touchpoints['Campaign'].replace('-', np.nan)

# sort by user + time -> required for journey/attribution reconstruction
touchpoints = touchpoints.sort_values(['User ID', 'Timestamp']).reset_index(drop=True)

dupe_tp = touchpoints.duplicated(subset=['User ID', 'Timestamp', 'Channel']).sum()
print(f"Duplicate touchpoint rows: {dupe_tp}")
touchpoints = touchpoints.drop_duplicates(subset=['User ID', 'Timestamp', 'Channel'])


# ---------------------------------------------------------
# 4b. STANDARDIZE COLUMN NAMES (lowercase, snake_case, no spaces)
# ---------------------------------------------------------
campaign.columns = campaign.columns.str.strip().str.lower().str.replace(' ', '_')
touchpoints.columns = touchpoints.columns.str.strip().str.lower().str.replace(' ', '_')

campaign = campaign.rename(columns={'date': 'campaign_date'})
touchpoints = touchpoints.rename(columns={'timestamp': 'touch_time'})


# ---------------------------------------------------------
# 5. SAVE CLEANED OUTPUTS
# ---------------------------------------------------------
campaign.to_csv('../data/processed/campaign_clean.csv', index=False)
touchpoints.to_csv('../data/processed/touchpoints_clean.csv', index=False)

print("\nSaved cleaned files to data/processed/")
print("\nCampaign clean shape:", campaign.shape)
print("Touchpoints clean shape:", touchpoints.shape)
print("\nCampaign sample:\n", campaign[['campaign_id','channel_used','channel_standardized','spend','revenue','conversions','ctr','cac']].head())
print("\nTouchpoints sample:\n", touchpoints[['user_id','touch_time','channel_standardized','campaign','converted']].head())

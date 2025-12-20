import pandas as pd
import requests
import os
from io import StringIO

def fetch_iso_codes(url, iso_output_path) -> pd.DataFrame:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # parse HTML table (wrap in StringIO to avoid deprecation warning)
        tables = pd.read_html(StringIO(response.text))
        
        # assume the first table is the one we want
        if not tables or len(tables) == 0:
            raise ValueError("No tables found on the page.")
        
        iso_df = tables[0]
        
        # validate dataset
        if iso_df.empty:
            raise ValueError("Table is empty.")
        elif "Alpha-3 code" not in iso_df.columns:
            raise ValueError("Expected column 'Alpha-3 code' not found in the dataset.")
        elif iso_df.shape[0] == 0 or iso_df['Alpha-3 code'].nunique() != iso_df.shape[0]:
            raise ValueError("Invalid ISO codes dataset.")
        else:
            iso_df.to_csv(iso_output_path, index=False)
            return iso_df
    except Exception as e:
        print(f"Error fetching or processing ISO codes: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Define paths (adjust as needed)
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(proj_dir, 'data', 'raw')
    url = "https://www.iban.com/country-codes"
    iso_output_path = os.path.join(raw_data_dir, 'iso_country_codes.csv')
    
    iso_df = fetch_iso_codes(url, iso_output_path)
    if not iso_df.empty:
        print("ISO codes dataset fetched and saved successfully.")
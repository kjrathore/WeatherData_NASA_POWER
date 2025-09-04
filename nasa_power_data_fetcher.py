#!/usr/bin/env python3
"""
NASA POWER Weather Data Fetcher
Fetches daily weather data from NASA POWER API for specified locations and time periods.
Uses YAML configuration file for easy customization and documentation.
"""

import yaml
import requests
import pandas as pd
import os
import time
import logging
from datetime import datetime, date
from typing import Dict, List, Optional
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nasa_power_fetch.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NASAPowerDataFetcher:
    """Fetches weather data from NASA POWER API."""
    
    def __init__(self, config_file: str = 'config.yaml'):
        """Initialize with YAML configuration file."""
        self.config = self._load_config(config_file)
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.session = requests.Session()
        
        # Create output directory
        os.makedirs(self.config.get('output_directory', 'nasa_power_data'), exist_ok=True)
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found!")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration file: {e}")
            sys.exit(1)
    
    def _build_api_url(self, site_info: Dict, year: int) -> str:
        """Build NASA POWER API URL for a specific site and year."""
        params = {
            'parameters': ','.join(self.config['api_settings']['parameters']),
            'community': self.config['api_settings']['community'],
            'longitude': site_info['long'],
            'latitude': site_info['lat'],
            'start': f"{year}0101",
            'end': f"{year}1231",
            'format': 'json'
        }
        
        # Build query string
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{query_string}"
    
    def _fetch_data(self, site_code: str, year: int) -> Optional[Dict]:
        """Fetch data from NASA POWER API for a specific site and year."""
        site_info = self.config[site_code]
        url = self._build_api_url(site_info, year)
        
        logger.info(f"Fetching data for {site_code} ({year}): {site_info['lat']}, {site_info['long']}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' not in data or 'parameter' not in data['properties']:
                logger.error(f"Invalid response structure for {site_code} {year}")
                return None
                
            logger.info(f"Successfully fetched data for {site_code} {year}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {site_code} {year}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing JSON response for {site_code} {year}: {e}")
            return None
    
    def _process_site_data(self, site_code: str) -> pd.DataFrame:
        """Process all years of data for a single site."""
        all_data = []
        site_info = self.config[site_code]
        
        for year in self.config['years']:
            # Add delay to respect API rate limits
            time.sleep(1)
            
            raw_data = self._fetch_data(site_code, year)
            if raw_data is None:
                logger.warning(f"Skipping {site_code} {year} due to fetch error")
                continue
            
            # Extract parameter data
            parameters = raw_data['properties']['parameter']
            
            # Get all dates from the first parameter
            first_param = list(parameters.keys())[0]
            dates = list(parameters[first_param].keys())
            
            # Process each date
            for date_str in dates:
                row = {
                    'site_code': site_code,
                    'points': site_info['POINTS'],
                    'latitude': site_info['lat'],
                    'longitude': site_info['long'],
                    'date': date_str,
                    'year': int(date_str[:4]),
                    'month': int(date_str[4:6]),
                    'day': int(date_str[6:8])
                }
                
                # Add weather parameters with descriptive names: Update as required
                param_mapping = {
                    'T2M': 'air_temp_c',
                    'T2M_MAX': 'air_temp_max_c',
                    'T2MDEW': 'dewpoint_temp_c',
                    'ALLSKY_SFC_SW_DWN': 'solar_radiation_kwh_m2',
                    'WS2M': 'wind_speed_ms',
                    'WS2M_MAX': 'wind_speed_max_ms',
                    'WD2M': 'wind_direction_deg',
                    'WD2M_MAX': 'wind_direction_max_deg',
                    'CLOUD_AMT_DAY': 'cloud_cover_pct',
                    'PRECTOTCORR': 'precipitation_mm',
                }
                
                for nasa_param, col_name in param_mapping.items():
                    if nasa_param in parameters:
                        value = parameters[nasa_param].get(date_str)
                        # Handle NASA POWER missing data values (-999)
                        row[col_name] = None if value == -999 else value
                    else:
                        row[col_name] = None
                
                all_data.append(row)
        
        if not all_data:
            logger.warning(f"No data collected for site {site_code}")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.sort_values(['date']).reset_index(drop=True)
        
        logger.info(f"Processed {len(df)} records for site {site_code}")
        return df
    
    def fetch_all_data(self) -> None:
        """Fetch data for all sites and save to CSV files."""
        logger.info("Starting data collection process")
        
        for site_code in self.config['sites']:
            logger.info(f"Processing site: {site_code}")
            
            site_df = self._process_site_data(site_code)
            
            if site_df.empty:
                logger.warning(f"No data to save for site {site_code}")
                continue
            
            # Save individual site data
            output_dir = self.config.get('output_directory', 'nasa_power_data')
            filename = f"{site_code}_daily_weather_{min(self.config['years'])}-{max(self.config['years'])}.csv"
            filepath = os.path.join(output_dir, filename)
            
            site_df.to_csv(filepath, index=False)
            logger.info(f"Saved {len(site_df)} records to {filepath}")
        
        logger.info("Data collection complete!")
    
    def create_combined_file(self) -> None:
        """Create a combined CSV file with all sites."""
        logger.info("Creating combined dataset")
        
        all_sites_data = []
        
        for site_code in self.config['sites']:
            site_df = self._process_site_data(site_code)
            if not site_df.empty:
                all_sites_data.append(site_df)
        
        if all_sites_data:
            combined_df = pd.concat(all_sites_data, ignore_index=True)
            combined_df = combined_df.sort_values(['site_code', 'date']).reset_index(drop=True)
            
            output_dir = self.config.get('output_directory', 'nasa_power_data')
            filename = f"all_sites_daily_weather_{min(self.config['years'])}-{max(self.config['years'])}.csv"
            filepath = os.path.join(output_dir, filename)
            
            combined_df.to_csv(filepath, index=False)
            logger.info(f"Saved combined dataset with {len(combined_df)} records to {filepath}")
        else:
            logger.warning("No data available to create combined file")
    
    def print_config_summary(self) -> None:
        """Print a summary of the current configuration."""
        logger.info("Configuration Summary:")
        logger.info(f"  Sites: {', '.join(self.config['sites'])}")
        logger.info(f"  Years: {self.config['years'][0]} to {self.config['years'][-1]} ({len(self.config['years'])} years)")
        logger.info(f"  Parameters: {len(self.config['api_settings']['parameters'])} weather variables")
        logger.info(f"  Output directory: {self.config.get('output_directory', 'nasa_power_data')}")
        
        # Show site coordinates
        for site_code in self.config['sites']:
            site_info = self.config[site_code]
            logger.info(f"  {site_code}: {site_info['lat']}, {site_info['long']}")

def main():
    """Main execution function."""
    try:
        # Initialize fetcher
        fetcher = NASAPowerDataFetcher()
        
        # Print configuration summary
        fetcher.print_config_summary()
        
        # Fetch data for individual sites
        fetcher.fetch_all_data()
        
        # Create combined file
        fetcher.create_combined_file()
        
        logger.info("All operations completed successfully!")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
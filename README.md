# WeatherData_NASA_POWER
## REF:
- https://power.larc.nasa.gov/
- https://power.larc.nasa.gov/parameters/

This Python script fetches daily weather data from NASA's POWER (Prediction of Worldwide Energy Resources) API for multiple point locations and time periods.

## Features

- Uses YAML configuration file with comment support for better documentation
- Fetches daily weather data for multiple sites and years
- Includes both average and daily maximum values for each parameter
- Handles API rate limiting with automatic delays
- Comprehensive error handling and logging
- Outputs individual CSV files per site and a combined file
- Handles missing data values appropriately

## Weather Parameters Collected

The script collects the following daily weather parameters:

| Parameter | Description | Unit | Daily Max Available |
|-----------|-------------|------|-------------------|
| Air Temperature | Temperature at 2 meters | °C | Yes |
| Dewpoint Temperature | Dew point temperature at 2 meters | °C | Yes |
| Solar Radiation (GHI) | All sky surface shortwave downward irradiance | kWh/m²/day | Yes |
| Wind Speed | Wind speed at 10 meters | m/s | Yes |
| Wind Direction | Wind direction at 10 meters | degrees | Yes |
| Cloud Cover | Cloud amount | % (0-100) | Yes |
| Precipitation | Precipitation (corrected) | mm/day | Yes |

## Installation

1. Clone or download this repository
2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit the `config.json` file to specify:

- **Site locations**: Add your sites with latitude, longitude, and point identifiers
- **Years**: Specify which years to download data for
- **Sites list**: List which sites to process
- **Output directory**: Where to save the CSV files

Example configuration:
```json
{
    "DET": {
        "POINTS": "140065",
        "lat": 44.69,
        "long": -122.22
    },
    "years": [2016, 2017, 2018, 2019, 2020],
    "sites": ["DET", "JPP", "OOLO"]
}
```

## Usage

Run the script:
```bash
python nasa_power_data_fetcher.py
```

The script will:
1. Read the configuration file
2. Fetch data for each site and year combination
3. Create individual CSV files for each site
4. Create a combined CSV file with all sites
5. Log all operations to `nasa_power_fetch.log`

## Output Files

The script creates:

### Individual Site Files
- Format: `{SITE_CODE}_daily_weather_{START_YEAR}-{END_YEAR}.csv`
- Contains all weather data for that specific site

### Combined File
- Format: `all_sites_daily_weather_{START_YEAR}-{END_YEAR}.csv`
- Contains data from all sites in one file

### CSV Columns

| Column | Description |
|--------|-------------|
| site_code | Site identifier |
| points | NASA POWER point identifier |
| latitude | Site latitude |
| longitude | Site longitude |
| date | Date (YYYY-MM-DD) |
| year | Year |
| month | Month |
| day | Day |
| air_temp_c | Daily average air temperature (°C) |
| air_temp_max_c | Daily maximum air temperature (°C) |
| dewpoint_temp_c | Daily average dewpoint temperature (°C) |
| dewpoint_temp_max_c | Daily maximum dewpoint temperature (°C) |
| solar_radiation_kwh_m2 | Daily solar radiation (kWh/m²) |
| solar_radiation_max_kwh_m2 | Daily maximum solar radiation (kWh/m²) |
| wind_speed_ms | Daily average wind speed (m/s) |
| wind_speed_max_ms | Daily maximum wind speed (m/s) |
| wind_direction_deg | Daily average wind direction (degrees) |
| wind_direction_max_deg | Daily maximum wind direction (degrees) |
| cloud_cover_pct | Daily average cloud cover (%) |
| cloud_cover_max_pct | Daily maximum cloud cover (%) |
| precipitation_mm | Daily precipitation (mm) |
| precipitation_max_mm | Daily maximum precipitation (mm) |

## Error Handling

- Network errors are logged and the script continues with remaining sites/years
- Missing data values (-999 from NASA POWER) are converted to NULL/NaN
- API rate limiting is handled with 1-second delays between requests
- All operations are logged to both console and log file

## NASA POWER API Information

This script uses NASA's POWER API:
- **URL**: https://power.larc.nasa.gov/api/
- **Documentation**: https://power.larc.nasa.gov/docs/
- **Data Source**: NASA Langley Research Center (LaRC)
- **Temporal Resolution**: Daily
- **Spatial Resolution**: 0.5° x 0.625° globally

## Notes

- The script respects API rate limits with built-in delays
- Large date ranges may take considerable time to download
- Internet connection is required during execution
- Data availability varies by parameter and location

## Troubleshooting

1. **Network Issues**: Check internet connection and NASA POWER API status
2. **Missing Data**: Some parameters may not be available for all locations/dates
3. **Rate Limiting**: If you encounter rate limit errors, increase the delay in `time.sleep(1)`
4. **Configuration Errors**: Verify JSON syntax in config.json

## License

This script is provided as-is for educational and research purposes. NASA POWER data usage is subject to NASA's data policy.
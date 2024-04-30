# SolarMetrics: SunPower Data Collection Script

This Python script retrieves solar power data from the SunPower API and writes it to InfluxDB.

## Functionality

This script performs the following actions:

1. **Retrieves Data:** Fetches solar power data for the last 10 minutes at 5-minute intervals using the SunPower API.
2. **Parses Data:** Parses the retrieved JSON data into a structured format.
3. **Writes to InfluxDB:** Writes production and consumption data points to InfluxDB with timestamps in MST (GMT-7).
4. **Error Handling:** Handles exceptions during token retrieval and data processing. If the token file is unavailable, a new token is acquired using `sunpowerauth.sunpowerauth.SunPowerAuth.gettoken()`.

## Setup

1. **Configuration:** Edit the `config.py` file to include:
    * `sunpower_api_url`: URL of your SunPower API endpoint.
    * `sunpower_site_id`: Your SunPower site ID.
    * `db_url`: InfluxDB connection URL.
    * `db_bucket`: InfluxDB bucket name to store data.
    * `db_org`: InfluxDB organization name.
    * `db_token`: InfluxDB token for write access.
    * `sunpower_token_file`: Path to a file containing your SunPower API token (optional, retrieved on first run if not provided).
2. **Libraries:** Install required Python libraries:
    * `sunpowermetrics`
    * `influxdb`
    * `sunpowerauth`
    * `configparser` (usually included by default)
    * `datetime` (usually included by default)

## Usage

1. Save the script as `solarmetrics.py`.
2. Run the script using `python solarmetrics.py`.

The script will continuously run, fetching and storing data at 10-minute intervals.

## Data Model

The script writes data to InfluxDB with the following measurement names and tags:

* Measurement:
    * `production`
    * `consumption`
* Tags:
    * `system`: "solar"

Data points include:

* `timestamp`: Time of data collection (MST, GMT-7).
* `value`: Power consumption/production in kWh.
* `type`: "production" or "consumption".

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

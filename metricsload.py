from sunpowermetrics.apimetrics import SunPowerAPI
import datetime as datetime
from datastores.influxdb import InfluxDb
import config
import argparse


def main(time=None):
    fh = open(config.sunpower_token_file, 'r')
    token = fh.read()
    starttime = datetime.datetime.now() - datetime.timedelta(hours=time)
    endtime = datetime.datetime.now()
    influx = InfluxDb(influxdb=config.db_url,
                      bucket=config.db_bucket,
                      org=config.db_org,
                      token=config.db_token)
    power = SunPowerAPI(fqdn=config.sunpower_api_url,
                        token=token)
    solarquery = {"operationName": "FetchPowerData",
                  "variables": {"siteKey": config.sunpower_site_id,
                                "interval": "five_minute",
                                "end": "{}".format(endtime.strftime("%Y-%m-%dT%H:%M:%S")),
                                "start": "{}".format(starttime.strftime("%Y-%m-%dT%H:%M:%S"))
                                },
                  "query": "query FetchPowerData($interval: String!, $end: String!, $start: String!, $siteKey: String!) {\n  energy(interval: $interval, end: $end, start: $start, siteKey: $siteKey) {\n    energyDataSeries {\n      production\n      consumption\n      storage\n      grid\n      __typename\n    }\n    totalProduction\n    totalConsumption\n    energyMixPercentage\n    totalGridImport\n    totalGridExport\n    netGridImportExport\n    totalStorageCharged\n    totalStorageDischarged\n    netStorageChargedDischarged\n    __typename\n  }\n}\n"
                  }
    energydata = power.getmetrics(query=solarquery)
    results = power.parsedata(data=energydata)
    production = []
    consumption = []
    for line in results['production']:
        time1 = datetime.datetime.strptime(line, "%Y-%m-%dT%H:%M:%S")
        timestamp = time1.strftime("%Y-%m-%dT%H:%M:%S-07:00")
        production.append({"timestamp": timestamp, "value": results['production'][line]['kwh'], "type": "production"})
        metric = float(results['production'][line]['kwh'])
        influx.writedata(measurement_name="production",
                         tag='"system" , "solar"',
                         metric=metric,
                         timestamp=timestamp)
    for line in results['consumption']:
        time1 = datetime.datetime.strptime(line, "%Y-%m-%dT%H:%M:%S")
        timestamp = time1.strftime("%Y-%m-%dT%H:%M:%S-07:00")
        consumption.append({"timestamp": timestamp, "value": results['consumption'][line]['kwh'], "type": "consumption"})
        cmetric = float(results['consumption'][line]['kwh'])
        influx.writedata(measurement_name="consumption",
                         tag='"system" , "solar"',
                         metric=cmetric,
                         timestamp=timestamp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load missing data from the Sunpower API")
    parser.add_argument('--time',
                        type=int,
                        required=True)
    args = parser.parse_args()
    main(time=args.time)

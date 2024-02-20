from sunpowermetrics.apimetrics import SunPowerAPI
import datetime as datetime
from datastores.influxdb import InfluxDb
import json


def main():
    fh = open('/opt/sunpowerapi/.token', 'r')
    token = fh.read()
    starttime = datetime.datetime.now() - datetime.timedelta(hours=1)
    endtime = datetime.datetime.now()
    influx = InfluxDb(influxdb="http://192.168.1.4:8086",
                      bucket="solarmetrics",
                      org="digital-domain",
                      token="VjI-pp2b8M2D9JTEqZUwzOLvgcNmMX0TOYe9tF6AdpoPoAAxyt_wpM53bNwEVW5htU8e-cOv19jMaueif0iYyw==")
    lg = open('/var/log/sunpower/metrics.log', 'a')
    power = SunPowerAPI(fqdn="https://edp-api-graphql.edp.sunpower.com",
                        token=token)
    solarquery = {"operationName": "FetchPowerData",
                  "variables": {"siteKey": "A_311367",
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
        lg.writelines(json.dumps({"timestamp": timestamp, "value": results['production'][line]['kwh'], "type": "production"}) + "\n")
        metric = float(results['production'][line]['kwh'])
        influx.writedata(measurement_name="production",
                         tag='"system" , "solar"',
                         metric=metric,
                         timestamp=timestamp)
    for line in results['consumption']:
        time1 = datetime.datetime.strptime(line, "%Y-%m-%dT%H:%M:%S")
        timestamp = time1.strftime("%Y-%m-%dT%H:%M:%S-07:00")
        consumption.append({"timestamp": timestamp, "value": results['consumption'][line]['kwh'], "type": "consumption"})
        lg.writelines(json.dumps({"timestamp": timestamp, "value": results['consumption'][line]['kwh'], "type": "consumption"}) + "\n")
        cmetric = float(results['consumption'][line]['kwh'])
        influx.writedata(measurement_name="consumption",
                         tag='"system" , "solar"',
                         metric=cmetric,
                         timestamp=timestamp)
    lg.close()


if __name__ == "__main__":
    main()
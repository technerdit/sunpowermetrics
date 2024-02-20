import datetime as datetime
import requests
import json
import sys


class SunPowerAPI(object):
    def __init__(self, **kwargs):
        self.baseUrl = kwargs['fqdn']
        self.headers = {"content-type": "application/json",
                        "authorization": "Bearer {}".format(kwargs['token'])}
        self.session = requests.Session()

    def getmetrics(self, query=None):
        url = self.baseUrl + "/graphql"
        results = self.session.post(url, headers=self.headers, data=json.dumps(query))
        if results.status_code == 200:
            return results.json()

    def parsedata(self, data=None):
        metricsdict = {}
        metricsdict['production'] = {}
        for line in data['data']['energy']['energyDataSeries']['production']:
            metricsdict['production'][line[0]] = {"kwh": line[1]}
        metricsdict['consumption'] = {}
        for line in data['data']['energy']['energyDataSeries']['consumption']:
            metricsdict['consumption'][line[0]] = {"kwh": line[1]}
        metricsdict['totals'] = {"totalProduction": data['data']['energy']['totalProduction'],
                                 "totalConsumption": data['data']['energy']['totalConsumption'],
                                 "totalGridImport": data['data']['energy']['totalGridImport'],
                                 "totalGridExport": data['data']['energy']['totalGridExport']}
        return metricsdict


if __name__ == "__main__":
    fh = open(".token", "r")
    data = fh.read()
    fh.close()
    print(data)
    starttime = datetime.datetime.now() - datetime.timedelta(hours=1)
    endtime = datetime.datetime.now()
    power = SunPowerAPI(fqdn="https://edp-api-graphql.edp.sunpower.com",
                        username="dayhkr@gmail.com",
                        password="PL98et7117u25!",
                        token=data)

    solarquery = {"operationName": "FetchPowerData",
                  "variables": {"siteKey": "A_311367",
                                "interval": "five_minute",
                                "end": "{}".format(endtime.strftime("%Y-%m-%dT%H:%M:%S")),
                                "start": "{}".format(starttime.strftime("%Y-%m-%dT%H:%M:%S"))
                                },
                  "query": "query FetchPowerData($interval: String!, $end: String!, $start: String!, $siteKey: String!) {\n  energy(interval: $interval, end: $end, start: $start, siteKey: $siteKey) {\n    energyDataSeries {\n      production\n      consumption\n      storage\n      grid\n      __typename\n    }\n    totalProduction\n    totalConsumption\n    energyMixPercentage\n    totalGridImport\n    totalGridExport\n    netGridImportExport\n    totalStorageCharged\n    totalStorageDischarged\n    netStorageChargedDischarged\n    __typename\n  }\n}\n"
                  }
    energydata = power.getmetrics(query=solarquery)
    print(energydata)
    results = power.parsedata(data=energydata)
    print(results)
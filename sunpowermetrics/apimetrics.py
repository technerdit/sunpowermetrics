import datetime as datetime
import requests
import json
from sunpowerauth.sunpowerauth import SunPowerAuth


class SunPowerAPI(object):
    def __init__(self, **kwargs):
        self.baseUrl = kwargs['fqdn']
        self.headers = {"content-type": "application/json",
                        "authorization": "Bearer {}".format("")}
        self.session = requests.Session()
        self.spa = SunPowerAuth()

    def getmetrics(self, query=None, token=None):
        self.headers['authorization'] = "Bearer {}".format(token)
        url = self.baseUrl + "/graphql"
        results = self.session.post(url, headers=self.headers, data=json.dumps(query))
        jsondata = results.json()
        if 'errors' in jsondata:
            for error in jsondata['errors']:
                if error['extensions']['code'] == "UNAUTHENTICATED":
                    print("Bad Token getting a new one")
                    token = self.spa.gettoken()
                    self.headers['authorization'] = "Bearer {}".format(token)
                    print("Updating headers {}".format(self.headers))
                    print("Trying again for metrics")
                    results = self.session.post(url, headers=self.headers, data=json.dumps(query))
                    return results.json()
        else:
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
    data = "bad"
    starttime = datetime.datetime.now() - datetime.timedelta(hours=1)
    endtime = datetime.datetime.now()
    power = SunPowerAPI(fqdn="https://edp-api-graphql.edp.sunpower.com",
                        username="",
                        password="",
                        token=data)

    solarquery = {"operationName": "FetchPowerData",
                  "variables": {"siteKey": "x_xxxxxx",
                                "interval": "five_minute",
                                "end": "{}".format(endtime.strftime("%Y-%m-%dT%H:%M:%S")),
                                "start": "{}".format(starttime.strftime("%Y-%m-%dT%H:%M:%S"))
                                },
                  "query": "query FetchPowerData($interval: String!, $end: String!, $start: String!, $siteKey: String!) {\n  energy(interval: $interval, end: $end, start: $start, siteKey: $siteKey) {\n    energyDataSeries {\n      production\n      consumption\n      storage\n      grid\n      __typename\n    }\n    totalProduction\n    totalConsumption\n    energyMixPercentage\n    totalGridImport\n    totalGridExport\n    netGridImportExport\n    totalStorageCharged\n    totalStorageDischarged\n    netStorageChargedDischarged\n    __typename\n  }\n}\n"
                  }
    energydata = power.getmetrics(query=solarquery)
    results = power.parsedata(data=energydata)

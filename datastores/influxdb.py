import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDb(object):
    def __init__(self, **influx):
        self.bucket = influx['bucket']
        self.org = influx['org']
        self.client = influxdb_client.InfluxDBClient(url=influx['influxdb'],
                                                     token=influx['token'],
                                                     org=influx['org'])

    def writedata(self, **data):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        p = influxdb_client.Point("{}".format(data['measurement_name'])).tag("system", "{}".format(data['tag'])).field("kwh", float(data['metric'])).time(data['timestamp'])
        res = write_api.write(bucket=self.bucket, org=self.org, record=p)
        return res

# Added a read data function may update this later to be more usable
    def readdata(self, **query):
        query_api = self.client.query_api()
        query = 'from(bucket:"{}")\
        |> range(start: {})\
        |> filter(fn:(r) => r._measurement == "{}")'.format(query['bucket'],
                                                                    query['range'],
                                                                    query['measurement'])
        result = query_api.query(org=self.org,
                                 query=query)
        results = []

        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))
        print(results)

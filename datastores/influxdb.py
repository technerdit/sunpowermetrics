import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDb(object):
    def __init__(self, **influx):
        # self.dbuser = influx['dbuser']
        # self.dbpass = influx['dbpass']
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

    def readdata(self, query=None):
        query_api = self.client.query_api()
        query = 'from(bucket:"solarmetrics")\
        |> range(start: -1d)\
        |> filter(fn:(r) => r._measurement == "production")'
        result = query_api.query(org=self.org,
                                 query=query)
        results = []

        for table in result:
            for record in table.records:
                results.append((record.get_field(), record.get_value()))
        print(results)


if __name__ == "__main__":
    influx = InfluxDb(influxdb="http://192.168.1.4:8086",
                      bucket="solarmetrics",
                      org="digital-domain",
                      token="VjI-pp2b8M2D9JTEqZUwzOLvgcNmMX0TOYe9tF6AdpoPoAAxyt_wpM53bNwEVW5htU8e-cOv19jMaueif0iYyw==")
    res = influx.writedata(measurement_name="production",
                           tag='"system" , "solar"',
                           metric=0.10,
                           timestamp="2024-02-20T14:19:00-07:00")
    print(res)

    #influx.readdata()
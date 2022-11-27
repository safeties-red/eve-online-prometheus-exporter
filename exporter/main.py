import json
import gzip
import logging

import requests
from prometheus_client.core import REGISTRY, GaugeMetricFamily
from prometheus_client import make_wsgi_app, start_wsgi_server
from wsgiref.simple_server import make_server

ESI_URL = "https://esi.evetech.net"
DATASOURCE = "tranquility"

logger = logging.getLogger('eve-exporter')
logger.debug('logger initialized')


class CustomCollector(object):
    """Promtheus Custom Collector"""

    def __init__(self) -> None:

        self.session = requests.Session()
        self.system_names = load_systems()

    def collect(self):
        """Creates all metrics for prometheus"""
        yield self.collect_players()
        yield self.get_system_kills()
        yield self.get_system_jumps()

    def collect_players(self):
        """Get the number of players"""
        request = self.call_esi("/v2/status/")
        count = request['players']
        return GaugeMetricFamily('players', 'Number of eve online players', value=count)

    def get_system_kills(self):
        """Get All eveonline system kills"""
        system_kills = GaugeMetricFamily('system_kills', "Number of kills in a system",
                                        labels=['system_id', 'system_name', 'region', 'constellation', 'security', 'type'])

        systems = self.call_esi("/v2/universe/system_kills")

        for system in systems:
            system_info = self.system_names[str(system['system_id'])]
            tags = [
                str(system['system_id']), 
                system_info['name'],
                system_info['region'],
                system_info['constellation'],
                str(system_info['security']),
            ]
            system_kills.add_metric(tags + ['npc_kills'], system['npc_kills'])
            system_kills.add_metric(tags + ['pod_kills'], system['pod_kills'])
            system_kills.add_metric(tags + ['ship_kills'], system['ship_kills'])

        return system_kills

    def get_system_jumps(self):
        """Get All eveonline system kills"""
        system_jumps = GaugeMetricFamily('system_jumps', "Number of ship jumps in a system",
                                        labels=['system_id'])
        systems = self.call_esi("/latest/universe/system_jumps")
        for system in systems:
            system_jumps.add_metric(
                [str(system['system_id'])], system['ship_jumps'])

        return system_jumps

    def call_esi(self, endpoint: str):
        """Make a ESI API Call"""
        params = {
            "datasource": DATASOURCE
        }

        try:
            response = self.session.get(
                f"{ESI_URL}{endpoint}", params=params, timeout=30)
            response.raise_for_status()
        except (requests.ConnectionError, requests.ConnectTimeout, requests.ReadTimeout) as ex:
            logger.error("An connection error occured: %s", ex)
            return None
        except requests.HTTPError as ex:
            logger.error("An HTTP error occured: %s", ex)
            return None

        return response.json()


def load_systems():
    """load systems from file"""
    with gzip.open("./data/systems.json.gz", "rb") as stream:
        return json.load(stream)


if __name__ == "__main__":
    REGISTRY.register(CustomCollector())
    app = make_wsgi_app()
    httpd = make_server('', 8000, app)
    httpd.serve_forever()
    start_wsgi_server(8000)

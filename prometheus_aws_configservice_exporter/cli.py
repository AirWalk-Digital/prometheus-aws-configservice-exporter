import argparse
import logging
import time
import sys
import signal
from typing import List
from pythonjsonlogger import jsonlogger
from prometheus_client import start_http_server, Gauge
from prometheus_client.core import REGISTRY
from .collector import ConfigServiceMetricsCollector


def parseArguments(argv: List[str]):
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", metavar="REGION", required=True, nargs="+", help="AWS Config region (can specify multiple space separated regions)")
    parser.add_argument("--exporter-host", required=False, default="127.0.0.1", help="The host at which the Prometheus exporter should listen to")
    parser.add_argument("--exporter-port", required=False, default="9100", type=int, help="The port at which the Prometheus exporter should listen to")
    parser.add_argument("--throttle", required=False, default="1.0", type=float, help="The number of seconds to wait between each AWS Config API request")
    parser.add_argument("--log-level", help="Minimum log level. Accepted values are: DEBUG, INFO, WARNING, ERROR, CRITICAL", default="INFO")

    return parser.parse_args(argv)


def main(args):
    shutdown = False

    # Init logger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("(asctime) (levelname) (message)", datefmt="%Y-%m-%d %H:%M:%S")
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)
    logger.setLevel(args.log_level)

    # Register signal handler
    def _on_sigterm(signal, frame):
        logging.getLogger().info("Exporter is shutting down")
        nonlocal shutdown
        shutdown = True

    signal.signal(signal.SIGINT, _on_sigterm)
    signal.signal(signal.SIGTERM, _on_sigterm)

    # Register our custom collector
    logger.info("Collecting initial metrics")
    REGISTRY.register(ConfigServiceMetricsCollector(args.region, args.throttle))

    # Set the up metric value, which will be steady to 1 for the entire app lifecycle
    upMetric = Gauge(
        "aws_config_exporter_up",
        "Always 1 - can by used to check if it's running")

    upMetric.set(1)

    # Start server
    start_http_server(args.exporter_port, args.exporter_host)
    logger.info("Throttling %s seconds between each API request", args.throttle)
    logger.info("Exporter listening on {host}:{port}".format(host=args.exporter_host, port=args.exporter_port))

    while not shutdown:
        time.sleep(1)

    logger.info("Exporter has shutdown")


def run():
    main(parseArguments(sys.argv[1:]))


if __name__ == '__main__':
    run()

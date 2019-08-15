import logging
import boto3
import botocore
import time
from typing import List
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily


class ConfigServiceMetricsCollector():
    def __init__(self, regions: List[str]):
        self.regions = regions
        self.scrapeErrors = {region: 0 for region in regions}

    def collect(self):
        # Init metrics
        currentResourcesMetric = GaugeMetricFamily(
            "aws_config_current_resources",
            "The total number of resources recorded by AWS Config",
            labels=["region", "resource_type"])

        compliantResourcesMetric = GaugeMetricFamily(
            "aws_config_compliant_resources",
            "The number of compliant resources recorded by AWS Config",
            labels=["region", "resource_type"])

        noncompliantResourcesMetric = GaugeMetricFamily(
            "aws_config_noncompliant_resources",
            "The number of non-compliant resources recorded by AWS Config",
            labels=["region", "resource_type"])

        scrapeErrorsMetric = CounterMetricFamily(
            "aws_config_scrape_errors_total",
            "The total number of scrape errors",
            labels=["region"])

        # Customize the boto client config
        botoConfig = botocore.client.Config(connect_timeout=2, read_timeout=10, retries={"max_attempts": 2})

        for region in self.regions:
            try:
                # Scrape Config statistics from the region
                regionStats = self._collectMetricsByRegion(region, botoConfig)
                # Add the findings to the exporterd metric
                for resource_type, stats in regionStats.items():
                    currentResourcesMetric.add_metric(value=stats[0], labels=[region, resource_type])
                    compliantResourcesMetric.add_metric(value=stats[1], labels=[region, resource_type])
                    noncompliantResourcesMetric.add_metric(value=stats[2], labels=[region, resource_type])
            except Exception as error:
                logging.getLogger().error(f"Unable to scrape AWS Config statistics from {region} because of error: {str(error)}")

                # Increase the errors count
                self.scrapeErrors[region] += 1

        # Update the scrape errors metric
        for region, errorsCount in self.scrapeErrors.items():
            scrapeErrorsMetric.add_metric(value=errorsCount, labels=[region])

        return [currentResourcesMetric, compliantResourcesMetric, noncompliantResourcesMetric, scrapeErrorsMetric]

    def _collectMetricsByRegion(self, region, botoConfig):
        client = boto3.client("config", config=botoConfig, region_name=region)
        regionStats = {}

        # List resources recorded by AWS Config
        resourceCounts = []
        resp = client.get_discovered_resource_counts()
        while resp:
            resourceCounts.extend(resp['resourceCounts'])
            resp = client.get_discovered_resource_counts(NextToken=resp['NextToken']) if 'NextToken' in resp else None

        for resource in resourceCounts:

            compliantCount = 0
            noncompliantCount = 0
            resp = client.get_compliance_summary_by_resource_type(ResourceTypes=[resource['resourceType']])
            while resp:
                time.sleep(1)  # Rate limit
                compliantCount += (resp['ComplianceSummariesByResourceType'][0]['ComplianceSummary']['CompliantResourceCount']['CappedCount'])
                noncompliantCount += (resp['ComplianceSummariesByResourceType'][0]['ComplianceSummary']['NonCompliantResourceCount']['CappedCount'])
                resp = client.get_compliance_summary_by_resource_type(ResourceTypes=[resource['resourceType']], NextToken=resp['NextToken']) if 'NextToken' in resp else None

            regionStats[resource['resourceType']] = (resource['count'], compliantCount, noncompliantCount)
        return regionStats

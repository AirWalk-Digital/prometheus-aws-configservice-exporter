import boto3
import unittest
from botocore.stub import Stubber
from unittest.mock import MagicMock, patch
from prometheus_aws_configservice_exporter.collector import ConfigServiceMetricsCollector


class TestConfigServiceMetricsCollector(unittest.TestCase):
    def setUp(self):
        self.gdClient = boto3.client("config")
        self.gdStubber = Stubber(self.gdClient)
        self.gdStubber.activate()

        self.botoSessionMock = MagicMock()
        self.botoSessionMock.client.return_value = self.gdClient

    def testCollectShouldReturnCurrentFindingsMetricFromSingleRegionWithSingleDetectorOnSuccess(self):
        # Mock Config Service
        self.gdStubber.add_response(
            "get_discovered_resource_counts",
            {"totalDiscoveredResources": 0, "resourceCounts": []},
            {})

        self.gdStubber.add_response(
            "get_compliance_summary_by_resource_type",
            {
                "ComplianceSummariesByResourceType": [
                    {
                        "ComplianceSummary": {
                            "CompliantResourceCount": {
                                "CappedCount": 2,
                                "CapExceeded": False
                            },
                            "NonCompliantResourceCount": {
                                "CappedCount": 11,
                                "CapExceeded": False
                            },
                            "ComplianceSummaryTimestamp": 1565880614.85
                        }
                    }
                ]
            },
            {})

        # Collect metrics
        with patch("boto3.session.Session", return_value=self.botoSessionMock):
            collector = ConfigServiceMetricsCollector(regions=["eu-west-1"])
            metrics = collector.collect()

        currentResourcesMetric = metrics[0]
        self.assertEqual(currentResourcesMetric.name, "aws_config_current_resources")
        self.assertEqual(currentResourcesMetric.type, "gauge")
        self.assertEqual(len(currentResourcesMetric.samples), 3)

        self.assertEqual(currentResourcesMetric.samples[0].value, 1)
        self.assertEqual(currentResourcesMetric.samples[0].labels, {"region": "eu-west-1", "severity": "low"})
        self.assertEqual(currentResourcesMetric.samples[1].value, 2)
        self.assertEqual(currentResourcesMetric.samples[1].labels, {"region": "eu-west-1", "severity": "medium"})
        self.assertEqual(currentResourcesMetric.samples[2].value, 3)
        self.assertEqual(currentResourcesMetric.samples[2].labels, {"region": "eu-west-1", "severity": "high"})

        scrapeErrorsMetric = metrics[1]
        self.assertEqual(scrapeErrorsMetric.name, "aws_configservice_scrape_errors")
        self.assertEqual(scrapeErrorsMetric.type, "counter")
        self.assertEqual(len(scrapeErrorsMetric.samples), 1)

        self.assertEqual(scrapeErrorsMetric.samples[0].value, 0)
        self.assertEqual(scrapeErrorsMetric.samples[0].labels, {"region": "eu-west-1"})

        self.gdStubber.assert_no_pending_responses()

#    def testCollectShouldReturnCurrentFindingsMetricFromSingleRegionWithMultipleDetectorsOnSuccess(self):
#        # Mock Config Service
#        self.gdStubber.add_response(
#            "list_detectors",
#            {"DetectorIds": ["eu-detector-1", "eu-detector-2"]},
#            {})
#
#        self.gdStubber.add_response(
#            "get_findings_statistics",
#            {"FindingStatistics": {
#                "CountBySeverity": {
#                    "2.0": 1,
#                    "4.0": 2,
#                    "7.0": 3,
#                }
#            }},
#            {"DetectorId": "eu-detector-1", "FindingCriteria": {"Criterion": {"service.archived": {"Eq": ["false"]}}}, "FindingStatisticTypes": ["COUNT_BY_SEVERITY"]})
#
#        self.gdStubber.add_response(
#            "get_findings_statistics",
#            {"FindingStatistics": {
#                "CountBySeverity": {
#                    "2.5": 4,
#                    "5.2": 5,
#                    "8.1": 6,
#                }
#            }},
#            {"DetectorId": "eu-detector-2", "FindingCriteria": {"Criterion": {"service.archived": {"Eq": ["false"]}}}, "FindingStatisticTypes": ["COUNT_BY_SEVERITY"]})
#
#        # Collect metrics
#        with patch("boto3.session.Session", return_value=self.botoSessionMock):
#            collector = ConfigServiceMetricsCollector(regions=["eu-west-1"])
#            metrics = collector.collect()
#
#        findingsMetric = metrics[0]
#        self.assertEqual(findingsMetric.name, "aws_configservice_current_findings")
#        self.assertEqual(findingsMetric.type, "gauge")
#        self.assertEqual(len(findingsMetric.samples), 3)
#
#        self.assertEqual(findingsMetric.samples[0].value, 5)
#        self.assertEqual(findingsMetric.samples[0].labels, {"region": "eu-west-1", "severity": "low"})
#        self.assertEqual(findingsMetric.samples[1].value, 7)
#        self.assertEqual(findingsMetric.samples[1].labels, {"region": "eu-west-1", "severity": "medium"})
#        self.assertEqual(findingsMetric.samples[2].value, 9)
#        self.assertEqual(findingsMetric.samples[2].labels, {"region": "eu-west-1", "severity": "high"})
#
#        scrapeErrorsMetric = metrics[1]
#        self.assertEqual(scrapeErrorsMetric.name, "aws_configservice_scrape_errors")
#        self.assertEqual(scrapeErrorsMetric.type, "counter")
#        self.assertEqual(len(scrapeErrorsMetric.samples), 1)
#
#        self.assertEqual(scrapeErrorsMetric.samples[0].value, 0)
#        self.assertEqual(scrapeErrorsMetric.samples[0].labels, {"region": "eu-west-1"})
#
#        self.gdStubber.assert_no_pending_responses()
#
#    def testCollectShouldReturnCurrentFindingsMetricFromMultipleRegionsOnSuccess(self):
#        # Mock ConfigService
#        self.gdStubber.add_response(
#            "list_detectors",
#            {"DetectorIds": ["eu-detector-1"]},
#            {})
#
#        self.gdStubber.add_response(
#            "get_findings_statistics",
#            {"FindingStatistics": {
#                "CountBySeverity": {
#                    "2.0": 1,
#                    "4.0": 2,
#                    "7.0": 3,
#                }
#            }},
#            {"DetectorId": "eu-detector-1", "FindingCriteria": {"Criterion": {"service.archived": {"Eq": ["false"]}}}, "FindingStatisticTypes": ["COUNT_BY_SEVERITY"]})
#
#        self.gdStubber.add_response(
#            "list_detectors",
#            {"DetectorIds": ["us-detector-1"]},
#            {})
#
#        self.gdStubber.add_response(
#            "get_findings_statistics",
#            {"FindingStatistics": {
#                "CountBySeverity": {
#                    "2.5": 4,
#                    "5.2": 5,
#                    "8.1": 6,
#                }
#            }},
#            {"DetectorId": "us-detector-1", "FindingCriteria": {"Criterion": {"service.archived": {"Eq": ["false"]}}}, "FindingStatisticTypes": ["COUNT_BY_SEVERITY"]})
#
#        # Collect metrics
#        with patch("boto3.session.Session", return_value=self.botoSessionMock):
#            collector = ConfigServiceMetricsCollector(regions=["eu-west-1", "us-east-1"])
#            metrics = collector.collect()
#
#        findingsMetric = metrics[0]
#        self.assertEqual(findingsMetric.name, "aws_configservice_current_findings")
#        self.assertEqual(findingsMetric.type, "gauge")
#        self.assertEqual(len(findingsMetric.samples), 6)
#
#        self.assertEqual(findingsMetric.samples[0].value, 1)
#        self.assertEqual(findingsMetric.samples[0].labels, {"region": "eu-west-1", "severity": "low"})
#        self.assertEqual(findingsMetric.samples[1].value, 2)
#        self.assertEqual(findingsMetric.samples[1].labels, {"region": "eu-west-1", "severity": "medium"})
#        self.assertEqual(findingsMetric.samples[2].value, 3)
#        self.assertEqual(findingsMetric.samples[2].labels, {"region": "eu-west-1", "severity": "high"})
#        self.assertEqual(findingsMetric.samples[3].value, 4)
#        self.assertEqual(findingsMetric.samples[3].labels, {"region": "us-east-1", "severity": "low"})
#        self.assertEqual(findingsMetric.samples[4].value, 5)
#        self.assertEqual(findingsMetric.samples[4].labels, {"region": "us-east-1", "severity": "medium"})
#        self.assertEqual(findingsMetric.samples[5].value, 6)
#        self.assertEqual(findingsMetric.samples[5].labels, {"region": "us-east-1", "severity": "high"})
#
#        scrapeErrorsMetric = metrics[1]
#        self.assertEqual(scrapeErrorsMetric.name, "aws_configservice_scrape_errors")
#        self.assertEqual(scrapeErrorsMetric.type, "counter")
#        self.assertEqual(len(scrapeErrorsMetric.samples), 2)
#
#        self.assertEqual(scrapeErrorsMetric.samples[0].value, 0)
#        self.assertEqual(scrapeErrorsMetric.samples[0].labels, {"region": "eu-west-1"})
#        self.assertEqual(scrapeErrorsMetric.samples[1].value, 0)
#        self.assertEqual(scrapeErrorsMetric.samples[1].labels, {"region": "us-east-1"})
#
#        self.gdStubber.assert_no_pending_responses()
#
#    def testCollectShouldSkipCurrentFindingsMetricOnFailingFetchingStatisticsFromARegionOutOfMultipleRegions(self):
#        # Mock ConfigService
#        self.gdStubber.add_response(
#            "list_detectors",
#            {"DetectorIds": ["eu-detector-1"]},
#            {})
#
#        self.gdStubber.add_client_error("get_findings_statistics")
#
#        self.gdStubber.add_response(
#            "list_detectors",
#            {"DetectorIds": ["us-detector-1"]},
#            {})
#
#        self.gdStubber.add_response(
#            "get_findings_statistics",
#            {"FindingStatistics": {
#                "CountBySeverity": {
#                    "2.5": 4,
#                    "5.2": 5,
#                    "8.1": 6,
#                }
#            }},
#            {"DetectorId": "us-detector-1", "FindingCriteria": {"Criterion": {"service.archived": {"Eq": ["false"]}}}, "FindingStatisticTypes": ["COUNT_BY_SEVERITY"]})
#
#        # Collect metrics
#        with patch("boto3.session.Session", return_value=self.botoSessionMock):
#            collector = ConfigServiceMetricsCollector(regions=["eu-west-1", "us-east-1"])
#            metrics = collector.collect()
#
#        findingsMetric = metrics[0]
#        self.assertEqual(findingsMetric.name, "aws_configservice_current_findings")
#        self.assertEqual(findingsMetric.type, "gauge")
#        self.assertEqual(len(findingsMetric.samples), 3)
#
#        self.assertEqual(findingsMetric.samples[0].value, 4)
#        self.assertEqual(findingsMetric.samples[0].labels, {"region": "us-east-1", "severity": "low"})
#        self.assertEqual(findingsMetric.samples[1].value, 5)
#        self.assertEqual(findingsMetric.samples[1].labels, {"region": "us-east-1", "severity": "medium"})
#        self.assertEqual(findingsMetric.samples[2].value, 6)
#        self.assertEqual(findingsMetric.samples[2].labels, {"region": "us-east-1", "severity": "high"})
#
#        scrapeErrorsMetric = metrics[1]
#        self.assertEqual(scrapeErrorsMetric.name, "aws_configservice_scrape_errors")
#        self.assertEqual(scrapeErrorsMetric.type, "counter")
#        self.assertEqual(len(scrapeErrorsMetric.samples), 2)
#
#        self.assertEqual(scrapeErrorsMetric.samples[0].value, 1)
#        self.assertEqual(scrapeErrorsMetric.samples[0].labels, {"region": "eu-west-1"})
#        self.assertEqual(scrapeErrorsMetric.samples[1].value, 0)
#        self.assertEqual(scrapeErrorsMetric.samples[1].labels, {"region": "us-east-1"})
#
#        self.gdStubber.assert_no_pending_responses()
#
#    def testCollectShouldNeverDecreaseScrapeErrorsOnSubsequentCalls(self):
#        # Mock ConfigService
#        self.gdStubber.add_response(
#            "list_detectors",
#            {"DetectorIds": ["us-detector-1"]},
#            {})
#
#        self.gdStubber.add_client_error("get_findings_statistics")
#
#        # Collect metrics
#        with patch("boto3.session.Session", return_value=self.botoSessionMock):
#            collector = ConfigServiceMetricsCollector(regions=["us-east-1"])
#            metrics = collector.collect()
#
#        findingsMetric = metrics[0]
#        self.assertEqual(findingsMetric.name, "aws_configservice_current_findings")
#        self.assertEqual(findingsMetric.type, "gauge")
#        self.assertEqual(len(findingsMetric.samples), 0)
#
#        scrapeErrorsMetric = metrics[1]
#        self.assertEqual(scrapeErrorsMetric.name, "aws_configservice_scrape_errors")
#        self.assertEqual(scrapeErrorsMetric.type, "counter")
#        self.assertEqual(len(scrapeErrorsMetric.samples), 1)
#
#        self.assertEqual(scrapeErrorsMetric.samples[0].value, 1)
#        self.assertEqual(scrapeErrorsMetric.samples[0].labels, {"region": "us-east-1"})
#
#        with patch("boto3.session.Session", return_value=self.botoSessionMock):
#            metrics = collector.collect()
#
#        findingsMetric = metrics[0]
#        self.assertEqual(findingsMetric.name, "aws_configservice_current_findings")
#        self.assertEqual(findingsMetric.type, "gauge")
#        self.assertEqual(len(findingsMetric.samples), 0)
#
#        scrapeErrorsMetric = metrics[1]
#        self.assertEqual(scrapeErrorsMetric.name, "aws_configservice_scrape_errors")
#        self.assertEqual(scrapeErrorsMetric.type, "counter")
#        self.assertEqual(len(scrapeErrorsMetric.samples), 1)
#
#        self.assertEqual(scrapeErrorsMetric.samples[0].value, 2)
#        self.assertEqual(scrapeErrorsMetric.samples[0].labels, {"region": "us-east-1"})
#
#        self.gdStubber.assert_no_pending_responses()

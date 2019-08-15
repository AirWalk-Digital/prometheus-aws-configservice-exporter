import sys
from setuptools import setup

# Version
version = "1.0.0"

# Requires Python 3
if sys.version_info.major < 3:
    raise RuntimeError('Installing requires Python 3 or newer')

# Read the long description from README.md
with open('README.md') as file:
    long_description = file.read()

setup(
  name                          = 'prometheus-aws-configservice-exporter',
  packages                      = ['prometheus_aws_configservice_exporter'],
  version                       = version,
  description                   = 'Prometheus exporter for AWS Config',
  long_description              = long_description,
  long_description_content_type = 'text/markdown',
  author                        = 'Jim Lamb',
  author_email                  = 'jim.lamb@airwalkconsulting.com',
  url                           = 'https://github.com/AirWalk-Digital/prometheus-aws-configservice-exporter',
  download_url                  = f'https://github.com/AirWalk-Digital/prometheus-aws-configservice-exporter/archive/{version}.tar.gz',
  keywords                      = ['prometheus', 'aws', 'config', 'configservice'],
  classifiers                   = [],
  python_requires               = ' >= 3',
  install_requires              = ["boto3==1.9.148", "python-json-logger==0.1.11", "prometheus_client==0.6.0"],
  extras_require = {
    'dev': [
      'flake8==3.7.7',
      'twine==1.13.0'
    ]
  },
  entry_points = {
    'console_scripts': [
        'prometheus-aws-configservice-exporter=prometheus_aws_configservice_exporter.cli:run',
    ]
  }
)

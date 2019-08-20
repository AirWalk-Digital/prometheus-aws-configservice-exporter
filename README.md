# Prometheus exporter for AWS Config

## Credits

Heavily based upon [Spreaker's Guard Duty exporter]( https://github.com/spreaker/prometheus-aws-guardduty-exporter)

## Features

- Exports the number of compliant and non-compliant resources from AWS Config, labelled by region and resource type
- Supports multiple AWS regions


## Exported metrics

The exporter exports the following metrics:

| Metric name                         | Type     | Labels                   | Description                                                  |
| ----------------------------------- | -------- | ------------------------ |------------------------------------------------------------- |
| `aws_config_exporter_up`            | gauge    | _None_                   | Always `1`: can be used to check if the exporter is running  |
| `aws_config_current_resources`      | guage    | `region`,`resource_type` | The total number of resources recorded by AWS Config         |
| `aws_config_compliant_resources`    | guage    | `region`,`resource_type` | The number of compliant resources recorded by AWS Config     |
| `aws_config_noncompliant_resources` | guage    | `region`,`resource_type` | The number of non-compliant resources recorded by AWS Config |
| `aws_config_scrape_errors_total`    | counter  | `region`                 | The total number of scrape errors                            |

## How to run it

You have two options to run it:

1. Manually install and run the [`prometheus-aws-configservice-exporter` Python package](https://pypi.org/project/prometheus-aws-configservice-exporter/)
   ```
   pip3 install prometheus-aws-configservice-exporter

   prometheus-aws-configservice-exporter --region us-east-1
   ```

2. Use the [Docker image available on Docker hub](https://hub.docker.com/r/airwalkconsulting/prometheus-aws-configservice-exporter/)
   ```
   docker run --env AWS_ACCESS_KEY_ID="id" --env AWS_SECRET_ACCESS_KEY="secret" airwalkconsulting/prometheus-aws-configservice-exporter --region us-east-1
   ```

The cli supports the following arguments:

| Argument                       | Required | Description |
| ------------------------------ | -------- | ----------- |
| `--region REGION [REGION ...]` | yes      | AWS Config region (can specify multiple space separated regions) |
| `--throttle SECONDS`           |          | The number of seconds to wait between AWS Config API requests. Float, eg `0.5`. Defaults to `1.0` |
| `--exporter-host`              |          | The host at which the Prometheus exporter should listen to. Defaults to `127.0.0.1` |
| `--exporter-port`              |          | The port at which the Prometheus exporter should listen to. Defaults to `9100` |
| `--log-level LOG_LEVEL`        |          | Minimum log level. Accepted values are: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Defaults to `INFO` |


## Required IAM privileges

In order to successfully run, this application requires the following IAM privileges:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid":    "ConfigServiceGetOnly",
      "Effect": "Allow",
      "Action": [
        "config:Get*",
      ],
      "Resource": "*"
    }
  ]
}
```


## Development

Run the development environment:

```
docker-compose build dev && docker-compose run --rm dev
```

Run tests in the dev environment (Warning: See TODO.md):

```
python3 -m unittest
```


## License

This software is released under the [MIT license](LICENSE.txt).

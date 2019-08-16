# How to publish a new version

**Release python package**:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. [Release new version on GitHub](https://github.com/AirWalk-Digital/prometheus-aws-configservice-exporter/releases)
4. Build package `rm -f dist/* && python3 setup.py sdist`
5. Publish package `twine upload dist/*`

**Release Docker image**:

1. Update package version in `Dockerfile`
2. Build image
   ```
   docker rmi -f prometheus-aws-configservice-exporter && \
   docker build -t prometheus-aws-configservice-exporter .
   ```
3. Tag the image and push it to Docker Hub
   ```
   docker tag prometheus-aws-configservice-exporter airwalkconsulting/prometheus-aws-configservice-exporter:latest && 
   docker push airwalkconsulting/prometheus-aws-configservice-exporter:latest
   ```
   ```
   VERSION=__PUT_VERSION_HERE__
   ```
   ```
   docker tag prometheus-aws-configservice-exporter airwalkconsulting/prometheus-aws-configservice-exporter:$VERSION && 
   docker push airwalkconsulting/prometheus-aws-configservice-exporter:$VERSION
   ```

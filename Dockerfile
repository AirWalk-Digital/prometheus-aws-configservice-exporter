FROM alpine:3.9

RUN apk add --update --no-cache python3~=3.6 && \
    python3 -m pip install prometheus-aws-configservice-exporter==1.0.4 --no-cache-dir

# Run as non-root
RUN adduser app -S -u 1000
USER app

ENTRYPOINT ["prometheus-aws-configservice-exporter"]

# aptly-mirror-metrics
Produce prometheus metrics about aptly mirrors

## Usage

Pipe the json format of aptly mirrors to `aptly_mirror_metrics.py`:
```shell-session
$ aptly miror list -json | ./aptly_mirror_metrics.py | tee /var/lib/prometheus/node-exporter/aptly-mirror.prom
# HELP aptly_mirror_update_success_timestamp_seconds Unix timestamp of last successful mirror update
# TYPE aptly_mirror_update_success_timestamp_seconds gauge
aptly_mirror_update_success_timestamp_seconds{archive_root="http://ftp.halifax.rwth-aachen.de/ubuntu/",mirror="ubuntu_jammy-updates_restricted"} 1682083060
aptly_mirror_update_success_timestamp_seconds{archive_root="http://ftp.tu-chemnitz.de/pub/linux/ubuntu-ports/",mirror="ubuntu_jammy-updates_restricted-arm64"} 1682083208
# HELP aptly_mirror_source_timestamp_seconds Date: field from the Release file of the mirror source as a unix timestamp
# TYPE aptly_mirror_source_timestamp_seconds gauge
aptly_mirror_source_timestamp_seconds{archive_root="http://ftp.halifax.rwth-aachen.de/ubuntu/",mirror="ubuntu_jammy-updates_restricted"} 1682062067
aptly_mirror_source_timestamp_seconds{archive_root="http://ftp.tu-chemnitz.de/pub/linux/ubuntu-ports/",mirror="ubuntu_jammy-updates_restricted-arm64"} 1682062067
# HELP aptly_metric_collection_failed Number of errors in the last run of aptly metric collection script
# TYPE aptly_metric_collection_failed gauge
aptly_metric_collection_failed 0
```
It will produce the prometheus text format which is suitable for consuption with node-exporter's textfile collector:
```shell-session
$ node-exporter --collector.textfile.directory /var/lib/prometheus/node-exporter &
$ curl -s localhost:9100/metrics | grep aptly_mirror
<your metrics>
```

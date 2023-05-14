#!/usr/bin/env python3

import json
import re
import sys
import traceback
from datetime import datetime


def labels_for_mirror(mirror):
    labels = dict(
        mirror=mirror['Name'],
        archive_root=mirror['ArchiveRoot']
    )
    labels = ','.join('%s="%s"' % pair for pair in sorted(labels.items()))
    labels = '{%s}' % labels
    return labels


def parse_date(d, formats):
    for fmt in formats:
        try:
            return datetime.strptime(d, fmt)
        except ValueError:
            pass
    raise ValueError("No date format could parse %s" % d)


FRACTIONAL_SECONDS_RE = re.compile(r'\.[0-9]+')

def add_metrics(mirror, metrics):
    labels = labels_for_mirror(mirror)
    mirror_updated = mirror['LastDownloadDate']
    mirror_updated = FRACTIONAL_SECONDS_RE.sub('', mirror_updated)
    mirror_updated = datetime.strptime(mirror_updated, "%Y-%m-%dT%H:%M:%S%z")
    mirror_updated = mirror_updated.timestamp()
    metrics['aptly_mirror_update_success_timestamp_seconds'][labels] = int(mirror_updated)

    source_date = mirror['Meta']['Date']
    source_date = parse_date(source_date, ("%a, %d %b %Y %H:%M:%S %Z",  "%a, %d %b %Y %H:%M:%S %z"))
    source_date = source_date.timestamp()
    metrics['aptly_mirror_source_timestamp_seconds'][labels] = int(source_date)


def main(argv):
    mirrors = json.load(sys.stdin)

    metrics: dict[str, dict[str, int]] = {
        "aptly_mirror_update_success_timestamp_seconds": {},
        "aptly_mirror_source_timestamp_seconds": {},
        "aptly_metric_collection_failed": {"": 0}
    }

    for mirror in mirrors:
        try:
            add_metrics(mirror, metrics)
        except Exception as e:
            print("error in %s" % mirror['Name'], file=sys.stderr)
            traceback.print_exception(e)
            metrics["aptly_metric_collection_failed"][""] = 1

    metrics_help = {
        'aptly_mirror_update_success_timestamp_seconds':
           'Unix timestamp of last successful mirror update',
        'aptly_mirror_source_timestamp_seconds':
            'Date: field from the Release file of the mirror source as a unix timestamp',
        'aptly_metric_collection_failed':
            'Number of errors in the last run of aptly metric collection script',
    }
    for metric_name in metrics:
        print("# HELP", metric_name, metrics_help[metric_name])
        print("# TYPE", metric_name, 'gauge')
        for labels, value in metrics[metric_name].items():
            print("%s%s %d" % (metric_name, labels, value))


if __name__ == '__main__':
  sys.exit(main(sys.argv))

#!/usr/bin/env python
import argparse
import os
import json

import illumio


def connect_to_pce():
    # passing connection params as env vars, but this could be done
    # through the ansible script command from ansible vars as well
    pce = illumio.PolicyComputeEngine(
        url=os.getenv("ILLUMIO_PCE_HOST"),
        port=os.getenv("ILLUMIO_PCE_PORT"),
        org_id=os.getenv("ILLUMIO_PCE_ORG_ID")
    )
    pce.set_credentials(
        os.getenv("ILLUMIO_API_KEY_USERNAME"),
        os.getenv("ILLUMIO_API_KEY_SECRET")
    )
    pce.must_connect()
    return pce


def run():
    parser = argparse.ArgumentParser(prog="apply labels", description="Apply labels to target workload")
    parser.add_argument("workload", help="Name of workload to target")
    parser.add_argument("labels", help="List of labels as JSON string")
    args = parser.parse_args()

    pce = connect_to_pce()

    label_hrefs = json.loads(args.labels)
    workload = pce.workloads.get_by_name(args.workload)
    if set(label_hrefs) ^ set(l.href for l in workload.labels):
        print(f"updating labels on {args.workload}")
        pce.workloads.update(workload.href, {"labels": [{"href": href} for href in label_hrefs]})


if __name__ == "__main__":
    run()

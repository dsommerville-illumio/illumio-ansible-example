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


def create_label_index(labels):
    # convert a list of label objects into a lookup mapping key:value to HREF
    index_ = {}
    for label in labels:
        index_[f"{label['key']}:{label['value']}"] = label["href"]
    return index_


def resolve_labels(labels, label_index):
    # use the label index to lookup HREFs for a given set of label kv pairs
    hrefs = []
    for label in labels:
        hrefs.append(label_index[f"{label['key']}:{label['value']}"])
    return hrefs


def resolve_rules(ruleset, label_index):
    # build rules based on the ruleset definition
    # simplified for the purposes of the example
    rules = []
    for rule_def in ruleset["rules"]:
        rules.append(illumio.Rule.build(
            providers=resolve_labels(rule_def["providers"], label_index),
            consumers=resolve_labels(rule_def["consumers"], label_index),
            ingress_services=[
                {"port": svc["port"], "proto": svc["proto"]}
                for svc in rule_def["services"]
            ],
        ))
    return rules


def run():
    parser = argparse.ArgumentParser(prog="apply rulesets", description="Apply labels to target workload")
    parser.add_argument("rulesets", help="Ruleset definition")
    parser.add_argument("labels", help="Label objects in ruleset scope and rules")
    args = parser.parse_args()

    pce = connect_to_pce()

    rulesets = json.loads(args.rulesets)
    labels = json.loads(args.labels)
    label_index = create_label_index(labels)

    updated_rulesets = []

    for rs in rulesets:
        existing_ruleset = pce.rule_sets.get_by_name(rs["name"])
        # construct the ruleset, replacing label kv pairs with HREFs
        ruleset_body = illumio.RuleSet(
            name=rs["name"],
            scopes=[illumio.LabelSet([
                illumio.Reference(href) for href in resolve_labels(rs["scope"], label_index)
            ])],
            # ... add other relevant fields
            rules=resolve_rules(rs, label_index)
        )
        if existing_ruleset:
            pce.rule_sets.update(existing_ruleset.href, ruleset_body)
            # get the updated rule set
            updated_rulesets.append(pce.rule_sets.get_by_reference(existing_ruleset.href))
        else:
            created_rs = pce.rule_sets.create(ruleset_body)
            updated_rulesets.append(created_rs)

    # provision the updates
    pce.provision_policy_changes(
        change_description="Ansible - update PCE rulesets",
        hrefs=[rs.href for rs in updated_rulesets]
    )


if __name__ == "__main__":
    run()

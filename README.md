# illumio.core Ansible Collection Example  

This repository provides an example playbook showing how the [`illumio.core`](https://galaxy.ansible.com/ui/repo/published/illumio/core/) Ansible collection can be leveraged to interact with the Illumio PCE.  

> [!NOTE]
> In a real environment, it likely makes more sense to submit the workload updates as a batch. The PCE API provides a [`workloads/bulk_update`](https://docs.illumio.com/core/23.5/API-Reference/index.html#bulk-update-workloads) endpoint for this purpose. 

## Configuration  

The playbook defines two host groups: `workloads` and `pce`. The `workloads` group is used to define individual workloads, each with its own `host_vars` file containing its label definitions as a list of key:value pairs. This avoids needing to hardcode label HREFs.  

The `pce` group uses the local Ansible host and defines rule sets using a custom YAML schema in a `group_vars` file.  

## Roles  

The `labels` role iterates over the defined labels for each workload, making sure the labels are present on the PCE before running the `apply_labels.py` script to update the workload's labels.  

The `rulesets` role similarly iterates over the defined rule sets, applying labels in the scope and rule providers/consumers. The labels are then combined and passed along with the rule set definitions to the `apply_rulesets.py` script.  

> [!NOTE]
> These examples are not exhaustive and may require significant additional effort and custom logic to work in a real environment.

## Scripts  

The example playbook contains two python scripts, `apply_labels.py` and `apply_rulesets.py` to show applying labels to individual workload hosts and applying rulesets based on a custom YAML schema respectively.  

> [!NOTE]
> The example scripts don't return results or [define "changed"](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_error_handling.html#defining-changed)

OpenShift Monitoring Platform
====================

Home of the WIP Prometheus-based OpenShift monitoring platform derived from [kube-prometheus](https://github.com/coreos/prometheus-operator/tree/master/contrib/kube-prometheus).

## Quick start:

```
$ oc cluster up
$ oc login -u system:admin
$ ./hack/deploy.sh
```

The Prometheus cluster is exposed at http://prometheus-k8s-monitoring.127.0.0.1.nip.io.

The Alert Manager cluster is exposed at http://alertmanager-main-monitoring.127.0.0.1.nip.io.


## What's in the box

Currently, all the monitoring components live in the `monitoring` namespace. This include the custom resources describing Prometheus and Alert Manager.

* [Prometheus Operator](files/manifests/prometheus-operator)
* [Prometheus](files/manifests/prometheus)
* [Alert Manager](files/manifests/alertmanager)

Built-in rules and alerts are colocated with contributed component rules in the [rules directory](files/assets/prometheus/rules).

The core Alert Manager configuration is in the [alertmanager directory](files/assets/alertmanager)

## How to integrate a new component

Individual component integration can take the following forms.

### Metrics Collection

To enable a component as a metrics collection target, do one or more of the following:

* Create a new `ServiceMonitor` resource in the [prometheus directory](files/manifests/prometheus) following the `prometheus-k8s-service-{COMPONENT_NAME}` convention. The `ServiceMonitor` should use label and/or namespace selectors to find the component's `Service` endpoints.
  * **NOTE**: Only the following namespaces are supported at this time: `monitoring`, `kube-system`, `default`, `openshift`.
* (FUTURE) Create a `Service` in the cluster which matches the following default namespace and label selector: (TODO)

### Recording and Alert Rules

To register new recording and alert rules, add new files to the [rules](files/assets/prometheus/rules) directory. These are YAML files containing fragments of Prometheus [recording](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/) and [alerting](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) rules in their native syntax.

### Alert Manager Routes

TODO: Currently there is a single static Alert Manager configuration file in the [alertmanager](files/assets/alertmanager) directory.

### Example

For now, see the [monitor-project-lifecycle](https://github.com/openshift/monitor-project-lifecycle) component which is already integrated with the monitoring platform.

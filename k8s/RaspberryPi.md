# Raspberry Pi

In order to run a local development cluster, you can use a fleet of Raspberry Pi's.
The tested way was running Ubuntu 22.04 on the Pi's and using MicroK8s.

## Setting up K8s

In order to setup a K8s cluster for Ubuntu, follow this [tutorial](https://ubuntu.com/tutorials/how-to-kubernetes-cluster-on-raspberry-pi#5-master-node-and-leaf-nodes).

Then enable the following plugins.

```shell
microk8s enable dns ha-cluster helm helm3 host-access hostpath-storage ingress metallb rbac registry storage
```

After checking the status, the a similar output should appear (here, three nodes are clustered)

```shel
$ microk8s status
microk8s is running
high-availability: yes
  datastore master nodes: xxx.xxx.xxx.xxx:19001 xxx.xxx.xxx.xxx:19001 xxx.xxx.xxx.xxx:19001
  datastore standby nodes: none
addons:
  enabled:
    dns                  # (core) CoreDNS
    ha-cluster           # (core) Configure high availability on the current node
    helm                 # (core) Helm - the package manager for Kubernetes
    helm3                # (core) Helm 3 - the package manager for Kubernetes
    host-access          # (core) Allow Pods connecting to Host services smoothly
    hostpath-storage     # (core) Storage class; allocates storage from host directory
    ingress              # (core) Ingress controller for external access
    metallb              # (core) Loadbalancer for your Kubernetes cluster
    rbac                 # (core) Role-Based Access Control for authorisation
    registry             # (core) Private image registry exposed on localhost:32000
    storage              # (core) Alias to hostpath-storage add-on, deprecated
  disabled:
    cert-manager         # (core) Cloud native certificate management
    community            # (core) The community addons repository
    dashboard            # (core) The Kubernetes dashboard
    kube-ovn             # (core) An advanced network fabric for Kubernetes
    mayastor             # (core) OpenEBS MayaStor
    metrics-server       # (core) K8s Metrics Server for API access to service metrics
    minio                # (core) MinIO object storage
    observability        # (core) A lightweight observability stack for logs, traces and metrics
    prometheus           # (core) Prometheus operator for monitoring and logging
```

Due to the installation of metallb, you will be prompted to set an IP interval for the loadbalancer. Set any valid range IP from your home network in order to make the selft test work.

## Configuring ingress and metallb

This [tutorial](https://gist.github.com/djjudas21/ca27aab44231bdebb0e72d30e00553ff#file-readme-md) provides a convenient way to setup ingress for a `HA-Cluster`.

> For HA clustering we need to find a way of load-balancing our Ingress, as a multi-node cluster will have one Ingress controller per node, each bound to its own node's IP.

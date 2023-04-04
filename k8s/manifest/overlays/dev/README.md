# How to

## Deploy

```shell
kubectl kustomize . --enable-helm | p8s apply -f -
```

## Delete

```shell
p8s kustomize . --enable-helm | p8s delete -f -
```

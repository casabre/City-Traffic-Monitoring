# How to

## Deploy

```shell
kubectl kustomize . --enable-helm | p8s apply -f -
```

## Delete

```shell
kubectl kustomize . --enable-helm | p8s delete -f -
```

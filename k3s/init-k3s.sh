#! /bin/bash
k3s-uninstall.sh
sleep 5s
curl -sfL https://get.k3s.io | sh -
sleep 1m
sudo kubectl apply -f traefik.yaml
sleep 10s
sudo kubectl get services --all-namespaces

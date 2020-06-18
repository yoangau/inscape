#! /bin/bash
sudo kubectl create deployment laboulette --image=yoangau/laboulette-server:latest
sleep 5s
sudo kubectl create service clusterip laboulette --tcp=80:80
sleep 5s
sudo kubectl apply -f ~/cluster/laboulette.yaml

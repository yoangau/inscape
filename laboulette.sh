#! /bin/bash
sudo kubectl create deployment laboulette --image=yoangau/laboulette-server:latest
sudo kubectl create service clusterip laboulette --tcp=80:80
sudo kubectl apply -f ~/cluster/laboulette.yml

#!/bin/bash
sudo cp github-webhooks-service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start github-webhooks-service
sudo systemctl enable github-webhooks-service

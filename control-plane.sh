#!/bin/bash

kubeadm init --apiserver-advertise-address=$(hostname -I) --pod-network-cidr=10.244.0.0/16

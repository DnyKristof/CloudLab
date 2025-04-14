#!/bin/bash

sysctl net.ipv4.ip_forward=1
kubeadm init --apiserver-advertise-address=$(hostname -I) --pod-network-cidr=10.244.0.0/16


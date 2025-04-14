#!/bin/bash

kubeadm init --apiserver-advertise-address=$(hostname -I) --pod-network-cidr=10.244.0.0/16

kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

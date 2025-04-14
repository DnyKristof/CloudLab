#!/bin/bash
set -e

apt update && apt install -y apt-transport-https ca-certificates curl ebtables

echo "*** Install containerd and runC ***"
apt update && apt install -y --no-install-recommends apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
            $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update && apt install -y --no-install-recommends containerd.io
systemctl start containerd
systemctl enable containerd

mv /etc/containerd/config.toml /etc/containerd/config.toml.orig
containerd config default | sudo tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup \= false/SystemdCgroup \= true/g' /etc/containerd/config.toml
systemctl restart containerd


echo "*** Install Kubernetes ***"
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.30/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.30/deb/ /" | tee /etc/apt/sources.list.d/kubernetes.list
apt update && apt install -y kubeadm kubelet kubectl kubernetes-cni
apt-mark hold kubelet kubeadm kubectl

swapoff -a
sed -i '/ swap / s/^/#/' /etc/fstab

sysctl net.ipv4.ip_forward=1

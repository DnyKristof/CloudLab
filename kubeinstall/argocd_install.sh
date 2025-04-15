echo "Installing ArgoCD"
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

kubectl -n argocd patch secret argocd-secret \
    -p '{"stringData": {"admin.password": "$2a$10$mivhwttXM0U5eBrZGtAG8.VSRL1l9cZNAmaSaqotIzXRBRwID1NT.",
        "admin.passwordMtime": "'$(date +%FT%T)'"
    }}'

echo "Access: "
kubectl get svc -n argocd argocd-server
echo "Waiting for service to load"
sleep 30
echo "Username: admin"
echo "Password : admin"


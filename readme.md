# WSL Ubuntu

# Table of contents
1. [aws](#aws)
2. [kubectl](#kubectl)
3. [eksctl](#eksctl)
4. [Activemq Docker Image](#activemq-docker-image)
5. [eks Activemq](#eks-activemq)

## aws <a name="aws"></a>
### Install
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
### Update
```
sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
```
&nbsp;
### Configure Credentials
* Overview: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config
* Create a key pair: https://console.aws.amazon.com/iam/
  * Updating the configuration file
```
          aws configure --profile poc-activemq
```
*
  * AWS Access Key ID [None]: AKIAI44QH8DHBEXAMPLE
  * AWS Secret Access Key [None]: je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
  * Default region name [None]: us-east-2
  * Default output format [None]: json
  * This will update 2 files
    * ~/.aws/credentials
    * ~/.aws/config
  * To see the config
```
         aws configure list-profiles
         aws configure list --profile poc-activemq
```
  * To see who is logged in
```
aws sts get-caller-identity --profile poc-activemq --debug
```
  * Policies to attach: https://eksctl.io/usage/minimum-iam-policies/ 

## kubectl <a name="kubectl"></a>
### Install
```
curl -LO https://storage.googleapis.com/kubernetes-release/release/v1.18.0/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
```
&nbsp;

## eksctl <a name="eksctl"></a>
### Install
```
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
```
* Enable bash completion, run the following, or put it in ~/.bashrc or ~/.profile:
```
. <(eksctl completion bash)
```
### Setting up a new Kubernetes cluster
* video  https://www.youtube.com/watch?v=p6xDCz00TxU&ab_channel=TechWorldwithNana
* Create cluster. A t2.micro node can only support 4 pods
```
eksctl create cluster \
--name poc-activemq-1 \
--version 1.22 \
--region us-east-2 \
--nodegroup-name poc-activemq-nodes \
--node-type t2.micro \
--nodes 3 \
--profile poc-activemq
```
* /home/hedrickbt/.kube/config will be created for kubectl use
* if you need to manually update your kubeconfig
```
aws eks update-kubeconfig --region us-east-2 --name poc-activemq
```
* Look at the nodes
```
kubectl get nodes
kubectl describe node/...
```
* How many pods are in use
```
kubectl get pods --all-namespaces | grep Running | wc -l
```
* Delete cluster and all items created
```
eksctl delete cluster --name poc-activemq-1 --profile poc-activemq
```
&nbsp;

### eks hello world
* Docs https://docs.aws.amazon.com/eks/latest/userguide/sample-deployment.html
#### Deploy
```
kubectl create namespace eks-sample-app
kubectl config set-context --current --namespace=eks-sample-app
kubectl config get-contexts
kubectl apply -f eks/k8s/helloworld/deployment.yaml
kubectl apply -f eks/k8s/helloworld/service.yaml
```
#### Test
```
kubectl get all
kubectl describe service eks-sample-linux-service
kubectl describe pod/eks-sample-linux-deployment-88ccbcdbc-pmwng
kubectl exec -it pod/eks-sample-linux-deployment-88ccbcdbc-pmwng -- /bin/bash
from inside the pod exec above
  curl eks-sample-linux-service
  cat /etc/resolv.conf
  exit
```

#### Verify External Access
```
kubectl get service
NAME                       TYPE           CLUSTER-IP       EXTERNAL-IP                                                               PORT(S)        AGE
eks-sample-linux-service   LoadBalancer   10.100.241.254   a446f86c690e845869839392607da4b1-1590742746.us-east-2.elb.amazonaws.com   80:32670/TCP   43m 

curl http://a446f86c690e845869839392607da4b1-1590742746.us-east-2.elb.amazonaws.com

NOTE: It can take a bit for the external name to become available.
```

#### Cleanup
```
kubectl config set-context --current --namespace=''
kubectl delete namespace eks-sample-app
```
&nbsp;

## Activemq Docker Image <a name="activemq-docker-image"></a>
### Test that the base image can be pulled from Dockerhub
```
docker image rm eclipse-temurin:17.0.5_8-jdk
docker pull eclipse-temurin:17.0.5_8-jdk
```

### Build the new image 
```
pushd docker
docker image rm hedrickbt/activemq:5.17.2-jdk17.0.5_8
docker build . -t hedrickbt/activemq:5.17.2-jdk17.0.5_8
docker login -u "hedrickbt" --password-stdin docker.io
docker push hedrickbt/activemq:5.17.2-jdk17.0.5_8
popd
```

### Test pull the new image
```
docker pull hedrickbt/activemq:5.17.2-jdk17.0.5_8
```

### Enter the image to look around
```
docker run -it --rm --entrypoint /bin/sh hedrickbt/activemq:5.17.2-jdk17.0.5_8
grep activemq-admin /app/conf/jetty-realm.properties
  activemq-admin: CHANGEME, admin
exit
```


### RUN Tests
#### Check that it starts without error
```
docker run -it --rm hedrickbt/activemq:5.17.2-jdk17.0.5_8
ctrl+c to exit
```
Looking for:
 * INFO | For help or more information please see: http://activemq.apache.org
 * INFO | ActiveMQ WebConsole available at http://0.0.0.0:8161/
 * INFO | ActiveMQ Jolokia REST API available at http://0.0.0.0:8161/api/jolokia/

#### Check the web server works
```
docker run --name activemq-test -id --rm -p 9161:8161 -p 61613:61613 hedrickbt/activemq:5.17.2-jdk17.0.5_8
curl.exe http://localhost:9161/
docker stop activemq-test

NOTE, if you get "An attempt was made to access a socket in a way forbidden by its access permissions." on windows, you can try running this from an elevated prompt.

net stop winnat
net start winnat
```
A good curl response
> <html>
><head>
><meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
><title>Error 401 Unauthorized</title>
></head>
><body><h2>HTTP ERROR 401 Unauthorized</h2>
><table>
><tr><th>URI:</th><td>/</td></tr>
><tr><th>STATUS:</th><td>401</td></tr>
><tr><th>MESSAGE:</th><td>Unauthorized</td></tr>
><tr><th>SERVLET:</th><td>-</td></tr>
></table>
></body>
></html>
&nbsp;

If you get this, try again.  It is likely you tried before the server finished starting
> curl: (52) Empty reply from server
&nbsp;


## eks Activemq <a name="eks-activemq"></a>
#### Deploy
```
kubectl create namespace activemq-test-ns
kubectl config set-context --current --namespace=activemq-test-ns
kubectl config get-contexts
kubectl apply -f eks/k8s/activemq/secret.yaml
kubectl apply -f eks/k8s/activemq/configmap.yaml
kubectl apply -f eks/k8s/activemq/deployment.yaml
kubectl apply -f eks/k8s/activemq/service-web.yaml
kubectl apply -f eks/k8s/activemq/service-stomp.yaml
kubectl apply -f eks/k8s/activemq/ingress.yaml
```
#### Test
```
kubectl get all
kubectl describe service eks-sample-linux-service
kubectl describe pod/eks-sample-linux-deployment-88ccbcdbc-pmwng
kubectl exec -it pod/eks-sample-linux-deployment-88ccbcdbc-pmwng -- /bin/bash
from inside the pod exec above
  curl eks-sample-linux-service
  cat /etc/resolv.conf
  exit
```

#### Verify External Access
```
kubectl get service
NAME                       TYPE           CLUSTER-IP       EXTERNAL-IP                                                               PORT(S)        AGE
eks-sample-linux-service   LoadBalancer   10.100.241.254   a446f86c690e845869839392607da4b1-1590742746.us-east-2.elb.amazonaws.com   80:32670/TCP   43m 

curl http://a446f86c690e845869839392607da4b1-1590742746.us-east-2.elb.amazonaws.com

NOTE: It can take a bit for the external name to become available.
```

#### Cleanup
```
kubectl config set-context --current --namespace=''
kubectl delete namespace activemq-test-ns
```
&nbsp;


# Distributed Cloud Personal Access Token Manager
[![Tableau Supported](https://img.shields.io/badge/Support%20Level-Tableau%20Supported-53bd92.svg)](https://www.tableau.com/support-levels-it-and-developer-tools)

### Requirements:
* Python 3.8 or greater
* Check kubectl is connected to the right kubernetes cluster
```
kubectl config current-context
kubectl get secrets -A
```
* Check access to the tableau cloud server used by your organization
```
curl -s https://online.tableau.com
```
* Use [this page](https://help.tableau.com/current/online/en-us/security_personal_access_tokens.htm) to create personal access tokens per bridge client instance/replica.
* The token name should follow the naming convention bridge-$SITE_NAME-$POOL_NAME-$INDEX where $INDEX starts in 0
* Save the token names and values in a file named ~/.dcpat/tableau_tokens.yaml. Sample content of the file: 
```yaml
tokens:
- name: "<personal-access-token-name>"
  value: "<personal-access-token-value>"
```

### Bridge Tokens
* Arguments required
  * --site is the tableau cloud site name
  * --pool is the tableau cloud bridge pool name
* Arguments with a default value.
  * --server is the tableau cloud url. It defaults to "https://online.tableau.com"
  * --namespace is the kubernetes namespace. It defaults to "tableau"
  * --secret is the kubernetes secret name in the namespace. It defaults to "bridgesecret"
* kubernetes StatefulSet.serviceName must be equal to "bridge-$SITE_NAME-$POOL_NAME" in order to use the tokens 

List tokens. The column inK8sSecret describes if the token exists in the kubernetes cluster. It reads tokens from file and kubernetes secret.
```
$ python3 dcpat.py bridge token list --site $SITE_NAME --pool $POOL_NAME
tokenName               inK8sSecret
bridge-site1-pool1-0              N
bridge-site1-pool1-1              N

list completed
```
Store tokens. It reads tokens from file, it writes and overwrites tokens in kubernetes secret.
```
$ python3 dcpat.py bridge token store --site $SITE_NAME --pool $POOL_NAME
store completed
```
List tokens.
```
$ python3 dcpat.py bridge token list --site $SITE_NAME --pool $POOL_NAME
tokenName               inK8sSecret
bridge-site1-pool1-0              Y
bridge-site1-pool1-1              Y

list completed
```
Test tokens. It reads tokens from kubernetes secret and tries to sign in to Tableau Cloud. If the operation fails then you need to generate new personal access tokens in Tableau Cloud.
```
$ python3 dcpat.py bridge token test --site $SITE_NAME --pool $POOL_NAME
tokenName               signin
bridge-site1-pool1-0         Y
bridge-site1-pool1-1         Y

test completed
```

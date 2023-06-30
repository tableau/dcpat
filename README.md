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
* The token name should follow the naming convention bridge-${POOL_ID}-${INDEX}
* $POOL_ID is a 36 char value. Navigate to the Tableau Site, select Settings, select Bridge, click in the "pool name" value. It opens a dialog containing the $POOL_ID value.
* $INDEX is an incrementing value. The initial value is 0
* Save the token names and values in a file named ~/.dcpat/tokens.yaml. Sample content of the file: 
```yaml
tokens:
- name: "<personal-access-token-name>"
  value: "<personal-access-token-value>"
```

### Bridge Tokens
* Arguments required
  * --site is the tableau site name in the url. For example, in the url https://online.tableau.com/#/site/mysiterocks/home, the site is "mysiterocks"
  * --pool is the tableau bridge pool id
* Arguments with a default value.
  * --server is the tableau cloud url. It defaults to "https://online.tableau.com"
  * --namespace is the kubernetes namespace. It defaults to "tableau"
  * --secret is the kubernetes secret name in the namespace. It defaults to "bridgesecret" 

List tokens. It lists tokens from file which follow the name convention and check if the token exists in the kubernetes secret.
```
$ python3 dcpat.py bridge token list --site $SITE_NAME --pool $POOL_ID
tokenName                                        inK8sSecret
bridge-a9f7c6e8-b2e8-443c-bb7a-14eba2b3f211-0              N
bridge-a9f7c6e8-b2e8-443c-bb7a-14eba2b3f211-1              N

list completed
```
Store tokens. It reads tokens from file and writes the tokens to the kubernetes secret.
```
$ python3 dcpat.py bridge token store --site $SITE_NAME --pool $POOL_ID
store completed
```
List tokens.
```
$ python3 dcpat.py bridge token list --site $SITE_NAME --pool $POOL_ID
tokenName                                        inK8sSecret
bridge-a9f7c6e8-b2e8-443c-bb7a-14eba2b3f211-0              Y
bridge-a9f7c6e8-b2e8-443c-bb7a-14eba2b3f211-1              Y

list completed
```
Test tokens. It reads tokens from kubernetes secret and tries to sign in to Tableau Cloud. If the operation fails then you need to generate new personal access tokens in Tableau Cloud.
```
$ python3 dcpat.py bridge token test --site $SITE_NAME --pool $POOL_ID
tokenName                                         signin details
bridge-a9f7c6e8-b2e8-443c-bb7a-14eba2b3f211-0          Y 
bridge-a9f7c6e8-b2e8-443c-bb7a-14eba2b3f211-1          Y 

test completed
```

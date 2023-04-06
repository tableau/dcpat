from base64 import b64decode, b64encode

from kubernetes import client, config
from kubernetes.client.rest import ApiException


class SecretManager:
    def __init__(self, namespace: str, name: str):
        self.namespace = namespace
        self.name = name
        self.secret_name = 'pat'
        config.load_kube_config()
        self.client = client.CoreV1Api()
        self.create_secret_if_not_exists()

    def create_secret_if_not_exists(self):
        try:
            _ = self.client.read_namespaced_secret(self.name, self.namespace)
        except ApiException as ex:
            if ex.status == 404:
                body = client.V1Secret()
                body.api_version = 'v1'
                body.data = {
                    self.secret_name: b64encode('{}'.encode('ascii')).decode('ascii')
                }
                body.kind = 'Secret'
                body.metadata = {'name': self.name}
                body.type = 'Opaque'
                self.client.create_namespaced_secret(self.namespace, body)
            else:
                raise ex

    def read(self):
        value = self.client.read_namespaced_secret(self.name, self.namespace)
        if not value or not value.data:
            return '{}'
        secret_value = b64decode(value.data.get(self.secret_name))
        return secret_value

    def write(self, value: str):
        body = self.client.read_namespaced_secret(self.name, self.namespace)
        if not body.data:
            body.data = {}
        body.data[self.secret_name] = b64encode(value.encode('ascii')).decode('ascii')
        _ = self.client.replace_namespaced_secret(self.name, self.namespace, body)

import json
from typing import List, Dict

import yaml
from requests import HTTPError

from lib.arguments import KubernetesArgs, TableauArgs
from lib.kubernetes_lib import SecretManager
from lib.tableau import TableauClient


class TableauTokenManager:
    def __init__(self, tokens_path: str, client: TableauClient, secretmanager: SecretManager):
        self.tokens_path = tokens_path
        self.client = client
        self.secretmanager = secretmanager

    def list(self):
        with open(self.tokens_path) as f:
            y = yaml.load(f, Loader=yaml.SafeLoader)
        tokens = y.get('tokens', [])
        tokens = [i for i in tokens if i['name'].startswith(self.client.token_prefix)]
        value = self.secretmanager.read()
        secrets = json.loads(value)
        width = len('tokenName')
        for token in tokens:
            token_name = token['name']
            width = max(width, len(token_name))
        width += 4
        print(f"{'tokenName'.ljust(width, ' ')}{'inK8sSecret':>11}")
        for token in tokens:
            token_name = token['name']
            exists = 'Y' if token_name in secrets else 'N'
            print(f"{token_name.ljust(width, ' ')}{exists:>11}")
        print()

    def store(self):
        with open(self.tokens_path) as f:
            y = yaml.load(f, Loader=yaml.SafeLoader)
        tokens = y.get('tokens', [])
        tokens = [{
            'tokenName': i['name'],
            'tokenSecret': i['value'],
        } for i in tokens if i['name'].startswith(self.client.token_prefix)]
        self._merge_secrets(tokens)

    def test(self):
        value = self.secretmanager.read()
        secrets = json.loads(value)
        tokens = {k: v for k, v in secrets.items() if k.startswith(self.client.token_prefix)}
        width = len('tokenName')
        for token_name, token_value in tokens.items():
            width = max(width, len(token_name))
        width += 4
        print(f"{'tokenName'.ljust(width, ' ')}{'signin':>7} details")
        for token_name, token_value in tokens.items():
            width = max(width, len(token_name))
            signin = 'N'
            try:
                _ = self.client.sign_in(token_name, token_value)
                signin = 'Y'
                message = ''
            except HTTPError as ex:
                message = ex.response.text
            finally:
                if signin == 'Y':
                    self.client.sign_out()
            print(f"{token_name.ljust(width, ' ')}{signin:>7} {message}")
        print()

    def _merge_secrets(self, tokens: List[Dict[str, str]]):
        value = self.secretmanager.read()
        secrets = {} if not value else json.loads(value)
        for token in tokens:
            k = token['tokenName']
            v = token['tokenSecret']
            secrets[k] = v
        value = json.dumps(secrets)
        self.secretmanager.write(value)

    def _remove_secrets(self, indexes: List[int]):
        value = self.secretmanager.read()
        secrets = {} if not value else json.loads(value)
        for i in indexes:
            k = f'{self.client.token_prefix}-{i}'
            if k in secrets:
                del secrets[k]
        value = json.dumps(secrets)
        self.secretmanager.write(value)


class TableauTokenProgram:
    def __init__(self, parent_parser_name):
        self.parent_parser_name = parent_parser_name
        self.parser_name = 'token'

    def parse_args(self, actions):
        parser = actions.add_parser(self.parser_name)
        actions = parser.add_subparsers(dest='action2', required=True)
        p_list = actions.add_parser('list')
        p_store = actions.add_parser('store')
        p_test = actions.add_parser('test')
        self.add_arguments(p_list)
        self.add_arguments(p_store)
        self.add_arguments(p_test)

    def add_arguments(self, parser):
        TableauArgs.parse_args(parser)
        if self.parent_parser_name == TableauBridgeProgram.parser_name:
            parser.add_argument('--pool', required=True,
                                help='tableau cloud bridge pool name')
        KubernetesArgs.parse_args(parser)
        parser.add_argument('--secret', default="bridgesecret",
                            help='kubernetes secret name')

    def check_args(self, args):
        TableauArgs.check_args(args)
        KubernetesArgs.check_args(args)
        d = vars(args)
        names = ['pool', 'secret']
        for name in names:
            if not d.get(name):
                raise ValueError(f'--{name} is required')
        if self.parent_parser_name == TableauBridgeProgram.parser_name:
            d['token_prefix'] = f'bridge-{args.site}-{args.pool}'

    def run(self, args, secrets):
        client = TableauClient(args.server, args.site, args.token_prefix)
        secretmanager = SecretManager(args.namespace, args.secret)
        tokenmanager = TableauTokenManager(args.tokens_path, client, secretmanager)
        if args.action2 == 'list':
            tokenmanager.list()
        elif args.action2 ==  'store':
            tokenmanager.store()
        elif args.action2 == 'test':
            tokenmanager.test()
        else:
            raise NotImplementedError()
        print(f'{args.action2} completed')


class TableauBridgeProgram:
    parser_name = 'bridge'

    def __init__(self):
        self.token = TableauTokenProgram(self.parser_name)

    def parse_args(self, actions):
        parser = actions.add_parser(self.parser_name)
        actions = parser.add_subparsers(dest='action1', required=True)
        self.token.parse_args(actions)

    def check_args(self, args):
        if args.action1 == self.token.parser_name:
            self.token.check_args(args)
        else:
            raise NotImplementedError()

    def run(self, args, secrets):
        if args.action1 == self.token.parser_name:
            self.token.run(args, secrets)
        else:
            raise NotImplementedError()

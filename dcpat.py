from argparse import ArgumentParser, Namespace
import logging
import os
import sys

import yaml

from lib.tableau_token import TableauBridgeProgram


class Program:
    def __init__(self):
        self.home_path = os.path.expanduser('~/.dcpat')
        self.tokens_path = f'{self.home_path}/tokens.yaml'
        self.bridge = TableauBridgeProgram()

    def parse_args(self) -> Namespace:
        parser = ArgumentParser()
        actions = parser.add_subparsers(dest='action0', required=True)
        self.bridge.parse_args(actions)
        return parser.parse_args()

    def check_args(self, args):
        d = vars(args)
        d['tokens_path'] = self.tokens_path
        if args.action0 == self.bridge.parser_name:
            self.bridge.check_args(args)
        else:
            raise NotImplementedError()

    def run(self, args, secrets):
        logging.basicConfig(
            datefmt='%Y-%m-%dT%H:%M:%S%z',
            format='{"ts":"%(asctime)s","sev":"%(levelname)s","ns":"%(module)s","msg":%(message)s}',
            level=os.getenv('LOGLEVEL', 'WARNING'))
        if args.action0 == self.bridge.parser_name:
            self.bridge.run(args, secrets)
        else:
            raise NotImplementedError()

    def parse_secrets(self, args) -> Namespace:
        secrets = Namespace()
        return secrets

    def check_secrets(self, secrets):
        pass


if __name__ == '__main__':
    version = sys.version_info
    if version < (3, 8):
        raise ValueError(f'It requires python 3.8 or greater, your version is {version.major}.{version.minor}')
    program = Program()
    _args = program.parse_args()
    program.check_args(_args)
    _secrets = program.parse_secrets(_args)
    program.check_secrets(_secrets)
    program.run(_args, _secrets)

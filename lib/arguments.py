class TableauArgs:
    @staticmethod
    def parse_args(parser):
        parser.add_argument('--server', default='https://online.tableau.com',
                            help='tableau cloud environment url. Sample: https://online.tableau.com')
        parser.add_argument('--site', required=True, help='tableau cloud site name')

    @staticmethod
    def check_args(args):
        d = vars(args)
        names = ['server', 'site']
        for name in names:
            if not d.get(name):
                raise ValueError(f'--{name} is required')
        prefixes = ['https://']
        match = False
        for prefix in prefixes:
            if args.server.startswith(prefix):
                match = True
                break
        if not match:
            raise ValueError(f'server does not start with a valid prefix: {prefixes}')


class KubernetesArgs:
    @staticmethod
    def parse_args(parser):
        parser.add_argument('--namespace', default='tableau',
                            help='kubernetes namespace of the secret')

    @staticmethod
    def check_args(args):
        d = vars(args)
        names = ['namespace']
        for name in names:
            if not d.get(name):
                raise ValueError(f'--{name} is required')

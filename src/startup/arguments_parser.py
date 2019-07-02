import argparse


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='Disaster Simulator')
        self.add_arguments()

    def add_arguments(self):
        self.parser.add_argument('-conf', required=True, type=str)
        self.parser.add_argument('-url', required=False, type=str, default='127.0.0.1')
        self.parser.add_argument('-sp', required=False, type=str, default='8910')
        self.parser.add_argument('-ap', required=False, type=str, default='12345')
        self.parser.add_argument('-pyv', required=False, type=str, default='')
        self.parser.add_argument('-g', required=False, type=bool, default=False)
        self.parser.add_argument('-step_t', required=False, type=int, default=30)
        self.parser.add_argument('-first_t', required=False, type=int, default=60)
        self.parser.add_argument('-mtd', required=False, type=str, default='time')
        self.parser.add_argument('-log', required=False, type=str, default='true')

    def check_arguments(self):
        return None

    def get_argument(self, arg):
        args = self.parser.parse_args()
        for argument in args.__dict__:
            if argument == arg:
                return args.__dict__[arg]

        return None

    def get_simulation_arguments(self):
        args = self.parser.parse_args()

        return [args.conf, args.url, args.sp, args.ap, args.log]

    def get_api_arguments(self):
        args = self.parser.parse_args()

        return [args.url, args.ap, args.sp, args.step_t, args.first_t, args.mtd]

    def get_arguments(self):
        args = self.parser.parse_args()

        return [args.conf, args.url, args.sp, args.ap, args.pyv, args.g,
                args.step_t, args.first_t, args.mtd]

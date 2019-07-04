import argparse
import secrets


class Parser:
    """Class that handles all the arguments given by the user.

    Almost all the arguments have default values, the only one that is required is the conf.
    This argument is necessary because the project it is not intended to have any configuration files."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog='Disaster Simulator')
        self.secret = secrets.token_urlsafe(15)
        self.add_arguments()

    def add_arguments(self):
        """Add all the arguments to the parser."""

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
        self.parser.add_argument('-secret', required=False, type=str, default='')

    def check_arguments(self):
        """Check all the arguments to prevent wrong format.

        :raises ArgumentFormatException: Exception with the appropriate message of wrong format argument."""

        return None

    def get_argument(self, arg):
        """Return the argument requested.

        :param arg: Argument requested
        :returns [None|primitive type obj]: None if argument not find else the value passed hold on the variable."""

        args = self.parser.parse_args()
        for argument in args.__dict__:
            if argument == arg:
                return args.__dict__[arg]

        return None

    def get_simulation_arguments(self):
        """Return all the arguments necessary for the Simulation.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        if not args.secret:
            secret = self.secret
        else:
            secret = args.secret
        return [args.conf, args.url, args.sp, args.ap, args.log, secret]

    def get_api_arguments(self):
        """Return all the arguments necessary for the API.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        if not args.secret:
            secret = self.secret
        else:
            secret = args.secret

        return [args.url, args.ap, args.sp, args.step_t, args.first_t, args.mtd, secret]

    def get_arguments(self):
        """Return all the arguments.

        :returns list: List of arguments"""

        args = self.parser.parse_args()

        return [args.conf, args.url, args.sp, args.ap, args.pyv, args.g,
                args.step_t, args.first_t, args.mtd, args.secret]

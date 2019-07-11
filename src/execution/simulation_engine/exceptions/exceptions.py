
class FailedWrongParam(Exception):

    def __init__(self, message=None):
        self.message = message


class FailedUnknownFacility(Exception):

    def __init__(self, message=None):
        self.message = message


class FailedNoRoute(Exception):

    def __init__(self, message=None):
        self.message = message


class FailedCapacity(Exception):

    def __init__(self, message):
        self.message = message


class FailedLocation(Exception):

    def __init__(self, message):
        self.message = message


class FailedUnknownItem(Exception):

    def __init__(self, message):
        self.message = message


class FailedItemAmount(Exception):

    def __init__(self, message):
        self.message = message


class FailedInvalidKind(Exception):

    def __init__(self, message):
        self.message = message


class FailedInsufficientBattery(Exception):

    def __init__(self, message):
        self.message = message


class FailedNoSocialAsset(Exception):

    def __init__(self, message):
        self.message = message

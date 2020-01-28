class FoundUncommitedFiles(EnvironmentError):
    pass


class AlreadyPushed(EnvironmentError):
    pass


class KktSectionNotFound(EnvironmentError):
    pass


class MandatoryKeyNotFound(ValueError):
    pass


class MetaDataNotFound(EnvironmentError):
    pass


class NotSupportedKernelType(ValueError):
    pass

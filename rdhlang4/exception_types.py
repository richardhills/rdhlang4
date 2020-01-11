### GENERAL ERRORS
class FatalException(Exception):
    pass

### TYPE SYSTEM ERRORS
class CreateReferenceError(Exception):
    # A run time error, caused by attempts to strongly-type something
    # where we can't make gaurantees. Should only be thrown by casting
    # in strongly typed code
    pass


class IncompatableAssignmentError(Exception):
    # A run time error, caused by attempts in weakly-typed code
    # to assign something to a value that would invalid strongly-syped
    # codes access
    pass

class InvalidDereferenceError(Exception):
    pass

class InvalidSpliceParametersError(Exception):
    pass

class InvalidSpliceModificationError(Exception):
    pass

class InvalidCompositeObject(Exception):
    pass

class NoValueError(Exception):
    pass

class CrystalValueCanNotBeGenerated(Exception):
    pass

class DataIntegrityError(Exception):
    # This error is fatal. Our data model doesn't match the data
    pass

### EXECUTOR ERRORS
class PreparationException(Exception):
    pass

class InvalidApplicationException(Exception):
    pass

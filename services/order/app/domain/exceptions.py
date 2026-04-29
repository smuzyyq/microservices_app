class OrderNotFoundError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class DatabaseConnectionError(Exception):
    pass

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class AuthorizationError(Exception):
    pass


class PermissionError(Exception):
    def __init__(self, permission):
        super().__init__(permission)
        self.permission = permission

    @property
    def message(self):
        return f"you do not have the {self.permission.name} permission"




class ModelAlreadyExistsException(Exception):
    """Элемент уже существует"""

    detail = "Object already exists"


class ModelNoFoundException(Exception):
    """Объект не найден"""

    detail = "Object no found"


class ActivityValidationError(Exception):
    """Исключение для валидации активности"""


class OrganizationNoFoundException(ModelNoFoundException):
    """Организация не найдена"""

    detail = "Organization no found with this id"

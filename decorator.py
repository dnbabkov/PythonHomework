appReference = None

def setApp(app):
    """
    Установка ссылки на экземпляр приложения для использования в декораторе.
    """
    global appReference
    appReference = app

def addToObjectList(func):
    """
    Декоратор для добавления объекта в список объектов приложения.
    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is not None and appReference is not None:
            appReference.addObject(result)
        return result
    return wrapper
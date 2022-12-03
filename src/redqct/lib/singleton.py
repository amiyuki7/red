from typing import Generic, Type, TypeVar

T = TypeVar("T")


class _SingletonWrapper(Generic[T]):
    def __init__(self, cls: Type[T]):
        self.__ptr = cls
        self._instance = None

    def __call__(self, *args, **kwargs) -> T:
        if self._instance is None:
            self._instance = self.__ptr(*args, **kwargs)
        return self._instance


def singleton(cls):
    return _SingletonWrapper(cls)

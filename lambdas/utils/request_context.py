from contextvars import ContextVar
from typing import Any


class RequestContext:
    def __init__(self) -> None:
        self._data = dict()

    def __set__(self, instance, value):
        if instance not in self._data:
            self._data[instance] = ContextVar(instance)
        self._data[instance].set(value)

    def __getitem__(self, __name: str) -> Any:
        context_var = self._data.get(__name)
        if type(context_var) == ContextVar:
            return context_var.get(None)
        return None


request_context = RequestContext()

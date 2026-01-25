from abc import ABCMeta, abstractmethod
from typing import Any, Optional


class LLMProvider(metaclass=ABCMeta):
    @abstractmethod
    def get_generator(self, *args, **kwargs):
        ...

    def get_model(self):
        return self._model

    def get_model_kwargs(self):
        return self._model_kwargs

    def get_context_window_size(self):
        return self._context_window_size


class EmbedderProvider(metaclass=ABCMeta):
    @abstractmethod
    def get_text_embedder(self, *args, **kwargs):
        ...

    @abstractmethod
    def get_document_embedder(self, *args, **kwargs):
        ...

    def get_model(self):
        return self._embedding_model


class DocumentStoreProvider(metaclass=ABCMeta):
    @abstractmethod
    def get_store(self, *args, **kwargs) -> Any:
        ...

    @abstractmethod
    def get_retriever(self, *args, **kwargs):
        ...


class SQLExecutionProvider(metaclass=ABCMeta):
    @abstractmethod
    async def execute_query(self, sql: str, **kwargs) -> Any:
        ...

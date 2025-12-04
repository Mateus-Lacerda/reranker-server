from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RerankRequest(_message.Message):
    __slots__ = ("query", "documents")
    QUERY_FIELD_NUMBER: _ClassVar[int]
    DOCUMENTS_FIELD_NUMBER: _ClassVar[int]
    query: str
    documents: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, query: _Optional[str] = ..., documents: _Optional[_Iterable[str]] = ...) -> None: ...

class RerankResult(_message.Message):
    __slots__ = ("original_index", "score", "text")
    ORIGINAL_INDEX_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    original_index: int
    score: float
    text: str
    def __init__(self, original_index: _Optional[int] = ..., score: _Optional[float] = ..., text: _Optional[str] = ...) -> None: ...

class RerankResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[RerankResult]
    def __init__(self, results: _Optional[_Iterable[_Union[RerankResult, _Mapping]]] = ...) -> None: ...

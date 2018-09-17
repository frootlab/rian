# -*- coding: utf-8 -*-
"""Collection of frequently used type objects."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import (
    Any, Callable, ClassVar, Dict, Hashable, Iterable, List, NewType, Optional,
    Sequence, Tuple, Union)
from types import ModuleType as Module, FunctionType as Function

# Alias types
Object = object

# compound types
StrList = List[str]
StrTuple = Tuple[str, ...]
StrDict = Dict[str, Any]
IntList = List[int]
IntTuple = Tuple[int, ...]
IntDict = Dict[int, Any]
StrDictOfFuncs = Dict[str, Function]
DictOfStrDicts = Dict[Hashable, StrDict]
StrOrBool = Union[str, bool]
StrOrDict = Union[str, dict]

# optional types
OptSet = Optional[set]
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptComplex = Optional[complex]
OptBool = Optional[bool]
OptList = Optional[list]
OptDict = Optional[dict]
OptTuple = Optional[tuple]
OptObject = Optional[Object]
OptModule = Optional[Module]
OptFunction = Optional[Function]
OptCallable = Optional[Callable]

# optional compound types
OptStrList = Optional[StrList]
OptIntList = Optional[IntList]
OptStrTuple = Optional[StrTuple]
OptIntTuple = Optional[IntTuple]
OptStrDictOfFuncs = Optional[StrDictOfFuncs]
OptStrOrBool = Optional[StrOrBool]
OptStrOrDict = Optional[StrOrDict]

# edge attribute dictionary types
DyaDict = Dict[Tuple[str, str], Any]
DyaTuple = Tuple[Sequence[str], Sequence[str]]

# numpy types
NpAxis = Optional[Union[int, Sequence[int]]]
NpFields = Optional[Union[str, Iterable[str]]]
NpRecArray = NewType('NpRecArray', 'numpy.recarray')
NpArray = NewType('NpArray', 'numpy.ndarray')
OptNpArray = Optional[NpArray]
# import numpy
#
# NpArray = typing.NewType('NpArray', numpy.array)


 #typing.NewType('NpArray', ...)
#NpMatrix = typing.NewType('NpMatrix', Any)

# if 'numpy' in dir():
#     numpy = sys.modules['numpy']
#     NpArray = typing.NewType('NpArray', numpy.ndarray)
#     NpMatrix = numpy.matrix
#     NpArray = Union['numpy.ndarray', 'numpy.matrix']

# special
ByteLike = Union[bytes, bytearray, str]

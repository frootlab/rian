# -*- coding: utf-8 -*-
"""Collection of frequently used type objects."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import (
    Any, Callable, ClassVar, Dict, Hashable, List, Optional, Sequence, Tuple,
    Union)
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
DictOfStrDicts = Dict[Hashable, StrDict]

# optional types
OptSet = Optional[set]
OptStr = Optional[str]
OptInt = Optional[int]
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

# edge attribute dictionary types
DyaDict = Dict[Tuple[str, str], Any]
DyaTuple = Tuple[Sequence[str], Sequence[str]]

# numpy types
NpAxis = Optional[Union[int, Sequence[int]]]
NpArray = Union['np.ndarray', 'np.matrix']

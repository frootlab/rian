# -*- coding: utf-8 -*-
"""Collection of types."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from typing import (
    cast, Any, Callable, ClassVar, Dict, Hashable, Iterable,
    List, NewType, Optional, Sequence, Set, Tuple, TypeVar, Union)

# import special types
from types import ModuleType as Module, FunctionType as Function
from array import ArrayType as Array

################################################################################
# Generic Variables
################################################################################

# Generic Type-Variables
S = TypeVar('S')
T = TypeVar('T')

# Built-in Type Aliases for Generic Types
Obj = object

################################################################################
# Literals and Collections of Literals
################################################################################

# Unions of Literals
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptComplex = Optional[complex]
OptBool = Optional[bool]
OptObj = Optional[Obj]
OptArray = Optional[Array]
StrOrBool = Union[str, bool]
OptStrOrBool = Optional[StrOrBool]
ByteLike = Union[bytes, bytearray, str]
Number = Union[int, float, complex]
Scalar = Union[int, float, complex]

# Collections of Literals
StrSet = Set[str]
StrPair = Tuple[str, str]
StrTuple = Tuple[str, ...]
StrList = List[str]
StrDict = Dict[str, Obj]
IntSet = Set[int]
IntPair = Tuple[int, int]
IntTuple = Tuple[int, ...]
IntList = List[int]
IntDict = Dict[int, Obj]
FloatPair = Tuple[float, float]

# Unions of Collections of Literals
OptSet = Optional[Set[Obj]]
OptPair = Optional[Tuple[Obj, Obj]]
OptTuple = Optional[Tuple[Obj, ...]]
OptList = Optional[List[Obj]]
OptDict = Optional[Dict[Hashable, Obj]]
StrOrDict = Union[str, Dict[Hashable, Obj]]
OptStrList = Optional[StrList]
OptIntList = Optional[IntList]
OptStrTuple = Optional[StrTuple]
OptIntTuple = Optional[IntTuple]
OptStrOrDict = Optional[StrOrDict]

# Compounds of Literals
RecDict = Dict[Hashable, StrDict]
DictOfRecDicts = Dict[Hashable, RecDict]
NestRecDict = Dict[Hashable, Union['NestRecDict', StrDict]]
RecDictLike = Union[StrDict, RecDict, DictOfRecDicts]
StrPairDict = Dict[StrPair, Obj]
StrListPair = Tuple[StrList, StrList]
StrTupleDict = Dict[Union[str, Tuple[str, ...]], Obj]
Vector = Sequence[Scalar]
NestDict = Dict[Hashable, Union['NestDict', Any]]
OptNestDict = Optional[NestDict]

# Generators and Iterables
IterNestRecDict = Iterable[NestRecDict]

################################################################################
# Callable types
################################################################################

# Elementary Callables
AnyFunc = Callable[..., Obj]
BoolFunc = Callable[..., bool]
ScalarFunc = Callable[..., Scalar]
VectorFunc = Callable[..., Vector]
UnaryFunc = Callable[[T], Obj]
BinaryFunc = Callable[[S, T], Obj]
TestFunc = Callable[[S, T], bool]

# Unions of Callables and Literals
OptCallable = Optional[AnyFunc]
OptFunction = Optional[Function]
OptModule = Optional[Module]

# Collections of Callables
StrDictOfFuncs = Dict[str, AnyFunc]
StrDictOfTestFuncs = Dict[str, TestFunc]

# Unions of Collections of Callables and Literals
OptStrDictOfFuncs = Optional[StrDictOfFuncs]
OptStrDictOfTestFuncs = Optional[StrDictOfTestFuncs]

# Compounds of Collables and Literals
FuncWrapper = Callable[[Callable[..., T]], Callable[..., T]]

################################################################################
# Types of builtin packages
################################################################################

# os / pathlib
from os import PathLike as Path
# currently recursive types are not fully supported (2018.09)
NestPath = Sequence[Union['NestPath', str, Path]]
NestPathDict = Dict[str, NestPath]
OptNestPathDict = Optional[NestPathDict]

################################################################################
# Types of external packages
################################################################################

# NumPy types

# currently not available (2018.09), but typing support is on the road:
# see: https://github.com/numpy/numpy-stubs
# callables with variing numbers of arguments are on the road:
# see: https://github.com/python/typing/issues/264
NpShape = Optional[IntTuple]
NpShapeLike = Optional[Union[int, Sequence[int]]]
NpAxis = Optional[Union[int, Sequence[int]]]
NpFields = Optional[Union[str, Iterable[str]]]
NpArray = Obj # TODO: replace with numpy.ndarray
NpMatrix = Obj # TODO: replace with numpy.matrix
NpRecArray = Obj # TODO: replace with numpy.recarray
NpDtype = Obj # TODO: replace with numpy.dtype
NpArraySeq = Sequence[NpArray]
NpMatrixSeq = Sequence[NpMatrix]
NpArrayLike = Union[Number, NpArray, NpArraySeq, NpMatrix, NpMatrixSeq]
OptNpRecArray = Optional[NpRecArray]
OptNpArray = Optional[NpArray]
NpArrayFunc = Callable[..., NpArray]
NpRecArrayFunc = Callable[..., NpRecArray]
NpMatrixFunc = Callable[..., NpMatrix]

# networkx types

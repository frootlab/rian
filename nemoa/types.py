# -*- coding: utf-8 -*-
"""Collection of frequently used types, stubs and constants."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

import os
import types
from typing import Any, Callable, ClassVar, Dict, Hashable, IO, Iterable
from typing import Iterator, List, Mapping, Optional, Sequence, Set, Tuple
from typing import Type, TypeVar, Union, Container, Sized, Generic
from nemoa.base import abc

# Type-Variables for Generic Structural Types
S = TypeVar('S')
T = TypeVar('T')

# Type-Surrogates
TypeHint = Generic[T] # pylint: disable=E1136

################################################################################
# Constants
################################################################################

NaN = float('nan') # Standard Constant for the representation of "Not a Number"
Infty = float('inf') # Standard Constant for the representation of infinity
void: Callable[..., None] = lambda *args, **kwds: None

################################################################################
# Stub Classes
################################################################################



################################################################################
# Structural Types for Literals and Collections of Literals
################################################################################

# Numbers
RealNumber = Union[int, float]
Number = Union[RealNumber, complex]
OptNumber = Optional[Number]

# Literals
OptType = Optional[type]
OptStr = Optional[str]
OptInt = Optional[int]
OptFloat = Optional[float]
OptComplex = Optional[complex]
OptBool = Optional[bool]
OptBytes = Optional[bytes]
StrOrBool = Union[str, bool]
OptStrOrBool = Optional[StrOrBool]
StrOrInt = Union[str, int]
BytesLike = Union[bytes, bytearray, memoryview]
BytesLikeOrStr = Union[BytesLike, str]

# Classes
Class = Type[Any]
OptClass = Optional[Class]
ClassInfo = Union[Class, Tuple[Class, ...]]
OptClassInfo = Optional[ClassInfo]

# Collections of numbers
RealVector = Sequence[RealNumber]
Vector = Sequence[Number]

# Collections of literals
HashDict = Dict[Hashable, Any]
AnyDict = Dict[Any, Any]
StrSet = Set[str]
StrPair = Tuple[str, str]
StrTuple = Tuple[str, ...]
StrList = List[str]
StrDict = Dict[str, Any]
IntSet = Set[int]
IntPair = Tuple[int, int]
IntTuple = Tuple[int, ...]
IntList = List[int]
IntDict = Dict[int, Any]
FloatPair = Tuple[float, float]
StrIter = Iterable[str]

# Unions of Collections of Literals
StrOrDict = Union[str, AnyDict]
StrOrType = Union[type, str]
OptSet = Optional[Set[Any]]
OptPair = Optional[Tuple[Any, Any]]
OptTuple = Optional[Tuple[Any, ...]]
OptList = Optional[List[Any]]
OptDict = Optional[Dict[Any, Any]]
OptStrDict = Optional[StrDict]
OptStrList = Optional[StrList]
OptStrTuple = Optional[StrTuple]
OptStrOrDict = Optional[StrOrDict]
OptIntList = Optional[IntList]
OptIntTuple = Optional[IntTuple]
OptStrIter = Optional[StrIter]

# Compounds of Literals and Collections of Literals
StrPairDict = Dict[StrPair, Any]
StrListPair = Tuple[StrList, StrList]
StrTupleDict = Dict[Union[str, Tuple[str, ...]], Any]
RecDict = Dict[Any, StrDict]
DictOfRecDicts = Dict[Any, RecDict]

# Classvariables of Compounds
ClassStrList = ClassVar[StrList]
ClassDict = ClassVar[AnyDict]
ClassStrDict = ClassVar[StrDict]

################################################################################
# Callable Types and Collection Types for Callables
################################################################################

# Callable Types
AnyOp = Callable[..., Any]
BoolOp = Callable[..., bool]
StrOp = Callable[..., str]
IntOp = Callable[..., int]
DictOp = Callable[..., dict]
OpOp = Callable[..., AnyOp]
Void = Callable[..., None]
KeyOp = Callable[[Any, Any], bool]
SeqOp = Callable[[Sequence[Any]], Any]
SeqHom = Callable[[Sequence[Any]], Sequence[Any]]

# Unions of Operators and Literals
OptOp = Optional[AnyOp]
OptVoid = Optional[Void]
OptBoolOp = Optional[BoolOp]
OptSeqOp = Optional[SeqOp]

# Operator Collections
DictOfOps = Dict[str, AnyOp]
DictOfKeyOps = Dict[str, KeyOp]

# Unions of Operator Collections and Literals
OptDictOfOps = Optional[DictOfOps]
OptDictOfKeyOps = Optional[DictOfKeyOps]

################################################################################
# Specific Structural Types
################################################################################

# Containers and Mappings
OptContainer = Optional[Container]
OptSized = Optional[Sized]
OptMapping = Optional[Mapping]

# Exceptions / Errors
ErrMeta = Type[BaseException]
ErrType = BaseException
ErrStack = types.TracebackType

# File Like
FileLike = IO[Any]
BinaryFileLike = IO[bytes]
TextFileLike = IO[str]

# Functions, Methods and Modules
Function = types.FunctionType
Method = types.MethodType
Module = types.ModuleType

# Iterators
IterAny = Iterator[Any]
IterNone = Iterator[None]

# None
NoneType = None.__class__

# Path Like
Path = os.PathLike
OptPath = Optional[Path]
PathList = List[Path]
StrDictOfPaths = Dict[str, Path]
PathLike = Union[str, Path]
PathLikeList = List[PathLike]
OptPathLike = Optional[PathLike]

# File References
FileRef = Union[FileLike, PathLike, abc.FileAccessor]

################################################################################
# Structural Types for external Packages
################################################################################

# Numpy
# TODO (patrick.michl@gmail.com): Currently (numpy 1.15.3) typing support for
# numpy is not available but a workaround is in progress, see:
# https://github.com/numpy/numpy-stubs
NpShape = Optional[IntTuple]
NpShapeLike = Optional[Union[int, Sequence[int]]]
NpAxes = Union[None, int, IntTuple]
NpFields = Union[None, str, Iterable[str]]
NpArray = Any # TODO: Replace with numpy.ndarray, when supported
NpMatrix = Any # TODO: replace with numpy.matrix, when supported
NpRecArray = Any # TODO: replace with numpy.recarray, when supported
NpDtype = Any # TODO: replace with numpy.dtype, when supported
NpArraySeq = Sequence[NpArray]
NpMatrixSeq = Sequence[NpMatrix]
NpArrayLike = Union[Number, NpArray, NpArraySeq, NpMatrix, NpMatrixSeq]
OptNpRecArray = Optional[NpRecArray]
OptNpArray = Optional[NpArray]
NpArrayFunc = Callable[..., NpArray]
NpRecArrayFunc = Callable[..., NpRecArray]
NpMatrixFunc = Callable[..., NpMatrix]
# TODO (patrick.michl@gmail.com): Currently (Python 3.7.2) the typing module
# does not support argument specification for callables with variing numbers of
# arguments, but this feature is in progress, see:
# https://github.com/python/typing/issues/264
# Use argument specification, when available:
# FuncOfNpArray = Callable[[NpArray, ...], Any]
# NpArrayFuncOfNpArray = Callable[[NpArray, ...], NpArray]

# NetworkX

# # -*- coding: utf-8 -*-
# """Dataset NPZ-archive I/O."""
#
# __author__ = 'Patrick Michl'
# __email__ = 'frootlab@gmail.com'
# __license__ = 'GPLv3'
# __docformat__ = 'google'
#
# import nemoa
# import numpy
#
# def filetypes():
#     """Get supported archive filetypes for dataset import."""
#
#     return {
#         'npz': 'Numpy Zipped Archive' }
#
# def load(path, **kwds):
#     """Import dataset from archive file."""
#
#     return Npz(**kwds).load(path)
#
# class Npz:
#     """Import dataset from numpy zipped archive."""
#
#     settings = None
#     default = {}
#
#     def __init__(self, **kwds):
#         from nemoa.base import ndict
#         self.settings = ndict.merge(kwds, self.default)
#
#     def load(self, path):
#         copy = numpy.load(path)
#         return {
#             'config': copy['config'].item(),
#             'tables': copy['tables'].item() }
#
#     def save(self, copy, path):
#
#
#         # # test if filetype is supported
#         # if filetype not in filetypes():
#         #     raise ValueError(f"filetype '{filetype}' is not supported")
#         #
#         # copy = dataset.get('copy')
#         # return Npz(**kwds).save(copy, path)
#
#
#         # create path if not available
#         if not os.path.exists(os.path.dirname(path)):
#             os.makedirs(os.path.dirname(path))
#
#         if self.settings['compress']:
#             numpy.savez_compressed(path, **copy)
#         else: numpy.savez(path, **copy)
#
#         return path

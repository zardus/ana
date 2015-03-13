#pylint:disable=wildcard-import

from .datalayer import *

dl = DataLayer()
def get_dl():
    return dl
def set_dl(*args, **kwargs):
    global dl
    dl = DataLayer(*args, **kwargs)

class M(object):
    '''This is a marker that's used internally by ANA.'''
    __slots__ = [ ]

from .storable import *

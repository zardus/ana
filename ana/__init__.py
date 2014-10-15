from .datalayer import *

dl = DataLayer()
def get_dl():
    return dl

class M(object):
    '''This is a marker that's used internally by ANA.'''
    __slots__ = [ ]

from .storable import *

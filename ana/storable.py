import uuid as uuid_module

import logging
l = logging.getLogger('ana.storable')

class Storable(object):
    __slots__ = [ '_ana_uuid', '_stored', '__weakref__' ]

    def make_uuid(self, uuid=None):
        '''
        If the storable has no UUID, this function creates one. The UUID is then
        returned.
        '''
        u = getattr(self, '_ana_uuid', None)
        if u is None:
            u = str(uuid_module.uuid4()) if uuid is None else uuid
            l.debug("Caching UUID %s", u)
            get_dl().uuid_cache[u] = self
            setattr(self, '_ana_uuid', u)
        return u

    @property
    def ana_uuid(self):
        return self.make_uuid()

    def ana_store(self):
        '''
        Assigns a UUID to the storable and stores the actual data.
        '''
        u = self.ana_uuid
        if not getattr(self, '_stored', False):
            get_dl().store_state(u, self._ana_getstate())
            setattr(self, '_stored', True)
        return u

    @classmethod
    def ana_load(cls, uuid):
        return D(uuid, cls, get_dl().load_state(uuid))

    #
    # ANA API
    #

    def _ana_getstate(self):
        raise NotImplementedError()

    def _ana_setstate(self, s):
        raise NotImplementedError()

    #
    # Pickle API
    #

    def __reduce__(self):
        u = getattr(self, '_ana_uuid', None)
        if u is None:
            return (D, (None, self.__class__, self._ana_getstate()))
        else:
            self.ana_store()
            return (D, (u, self.__class__, None))


from . import get_dl
from .d import D

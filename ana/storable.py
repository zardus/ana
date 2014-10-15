import uuid as uuid_module

import logging
l = logging.getLogger('ana.storable')

#pylint:disable=attribute-defined-outside-init,access-member-before-definition

import abc

class StorableMeta(type):
    def __call__(cls, *args, **kwargs):
        pickled = False
        uuid = None
        if len(args) >= 2 and isinstance(args[0], M):
            uuid = args[1]
            args = args[2:]
            pickled = True

        if len(args) != 0:
            if pickled:
                raise ANAError("too many arguments passed to StorableMeta.__call__ in unpickling")
            if isinstance(args[0], M):
                raise ANAError("multiple M() objects passed to Storable with UUID %s" % uuid)

        l.debug("Storable being created with uuid %s", uuid)

        if uuid is not None:
            try:
                self = get_dl().uuid_cache[uuid]
                l.debug("... returning cached")
            except KeyError:
                # create the object and set up Storable properties
                self = super(StorableBase, cls).__new__(cls) #pylint:disable=bad-super-call
                self._ana_uuid = uuid
                self._stored = True

                # restore the state
                s = get_dl().load_state(self._ana_uuid)
                self._ana_setstate(s)

                # cache and return
                get_dl().uuid_cache[uuid] = self
                l.debug("... returning newly cached")
        else:
            self = super(StorableBase, cls).__new__(cls) #pylint:disable=bad-super-call
            self._ana_uuid = None
            self._stored = False
            if not pickled:
                self.__init__(*args, **kwargs)
            l.debug("... returning new uncached")

        if not hasattr(self, '_ana_uuid'):
            raise ANAError("Storable somehow got through without an _ana_uuid attr")
        return self

class StorableBase(object):
    __slots__ = [ '_ana_uuid', '_stored', '__weakref__' ]

    def __new__(cls, *args, **kwargs):
        return StorableMeta.__call__(cls, *args, **kwargs)

    def make_uuid(self, uuid=None):
        '''
        If the storable has no UUID, this function creates one. The UUID is then
        returned.
        '''
        if self._ana_uuid is None:
            self._ana_uuid = str(uuid_module.uuid4()) if uuid is None else uuid
            l.debug("Caching UUID %s", self._ana_uuid)
            get_dl().uuid_cache[self._ana_uuid] = self
        return self._ana_uuid

    @property
    def ana_uuid(self):
        return self.make_uuid()

    def ana_store(self):
        '''
        Assigns a UUID to the storable and stores the actual data.
        '''
        u = self.ana_uuid #pylint:disable=unused-variable
        self.__getstate__()
        return u

    @classmethod
    def ana_load(cls, uuid):
        return StorableMeta.__call__(cls, M(), uuid)

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

    def __getstate__(self):
        if self._ana_uuid is not None:
            if not self._stored:
                l.debug("Storing Storable with UUID %s", self._ana_uuid)
                get_dl().store_state(self._ana_uuid, self._ana_getstate())
                self._stored = True
            return M()
        else:
            l.debug("Pickling full state.")
            return self._ana_getstate()

    def __setstate__(self, s):
        if isinstance(s, M):
            l.debug("Ignoring setstate for marked Storable")
        else:
            l.debug("Setting state on storable.")
            self._ana_setstate(s)

    def __getnewargs__(self):
        return (M(), self._ana_uuid,)


class Storable(StorableBase): #pylint:disable=abstract-method
    __metaclass__ = StorableMeta

class StorableMetaABC(StorableMeta, abc.ABCMeta):
    pass

class StorableABC(StorableBase): #pylint:disable=abstract-method
    __metaclass__ = StorableMetaABC

from . import get_dl
from . import M
from .errors import ANAError

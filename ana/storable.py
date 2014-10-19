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

    @staticmethod
    def _to_literal(o, known_set):
        if o is None:
            return None
        elif type(o) in (long, int, str, unicode, float, bool):
            return o
        elif isinstance(o, dict):
            return {
                Storable._to_literal(k, known_set):Storable._to_literal(v, known_set) for k,v in o.iteritems()
            }
        elif isinstance(o, list) or isinstance(o, tuple) or isinstance(o, set):
            return [ Storable._to_literal(e, known_set) for e in o ]
        elif isinstance(o, Storable):
            return o.to_literal(known_set)
        else:
            Storable._to_literal(o, known_set)

    def to_literal(self, known_set):
        d = {
            'ana_class': self.__class__.__name__,
            'ana_module': getattr(self, '__module__', '__unknown__')
        }
        uuid = getattr(self, '_ana_uuid', None)
        if uuid is not None:
            d['ana_uuid'] = uuid
            if uuid in known_set:
                return d
            else:
                known_set.add(uuid)

        o = self._ana_getliteral()
        if o is NotImplemented:
            o = self._ana_getstate()
        d['ana_object'] = self._to_literal(o, known_set)
        return d

    #
    # ANA API
    #

    def _ana_getstate(self):
        raise NotImplementedError()

    def _ana_setstate(self, s):
        raise NotImplementedError()

    def _ana_getliteral(self): #pylint:disable=no-self-use
        return NotImplemented

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

import os
import ana
import nose
import pickle

import logging
l = logging.getLogger("ana.test")

class A(ana.Storable):
    def __init__(self, n):
        nose.tools.assert_false(hasattr(self, 'n'))

        self.n = n
        l.debug("%s.__init__", self)

    def __repr__(self):
        return "<A %s>" % str(self.n)

    def _ana_getstate(self):
        l.debug("%s._ana_getstate", self)
        return (self.n,)

    def _ana_setstate(self, s):
        self.n = s[0]
        l.debug("%s._ana_setstate", self)

class B(ana.Storable):
    def __init__(self, n):
        nose.tools.assert_false(hasattr(self, 'n'))

        self.n = n
        l.debug("%s.__init__", self)

    def __repr__(self):
        return "<A %s>" % str(self.n)

    def _ana_getstate(self):
        l.debug("%s._ana_getstate", self)
        return (self.n,)

    def _ana_setstate(self, s):
        self.n = s[0]
        l.debug("%s._ana_setstate", self)

def test_ana():
    l.debug("Initializing 1")
    one = A(1)
    l.debug("Initializing 2")
    two = A(2)

    one.make_uuid()

    l.debug("Copying 1")
    one_p = pickle.dumps(one)
    one_copy = pickle.loads(one_p)
    l.debug("Copying 2")
    two_p = pickle.dumps(two)
    two_copy = pickle.loads(two_p)

    nose.tools.assert_is(one_copy, one)
    nose.tools.assert_is_not(two_copy, two)
    nose.tools.assert_equal(str(two_copy), str(two))

    nose.tools.assert_is(one, A.ana_load(one.ana_store()))
    nose.tools.assert_is(two, A.ana_load(two.ana_store()))

    two_copy2 = pickle.loads(pickle.dumps(two))
    nose.tools.assert_equal(str(two_copy2), str(two))

    l.debug("Initializing 3")
    three = A(3)
    three_str = str(three)
    l.debug("Storing 3")
    three_uuid = three.ana_store()
    l.debug("Deleting 3")
    del three
    nose.tools.assert_false(three_uuid in ana.get_dl().uuid_cache)
    l.debug("Loading 3")
    three_copy = A.ana_load(three_uuid)
    nose.tools.assert_equal(three_copy.ana_uuid, three_uuid) #pylint:disable=no-member
    nose.tools.assert_equal(str(three_copy), three_str)

def test_dir():
    ana.dl = ana.DataLayer(pickle_dir="/tmp/test_ana")
    one = A(1)
    nose.tools.assert_is(one, A.ana_load(one.ana_store()))
    nose.tools.assert_true(os.path.exists("/tmp/test_ana/%s.p" % one.ana_uuid))

if __name__ == '__main__':
    import sys
    logging.getLogger("ana.test").setLevel(logging.DEBUG)
    logging.getLogger("ana.storable").setLevel(logging.DEBUG)
    logging.getLogger("ana.datalayer").setLevel(logging.DEBUG)
    logging.getLogger("ana.d").setLevel(logging.DEBUG)

    if len(sys.argv) > 1:
        globals()['test_%s' % sys.argv[1]]()
    else:
        test_ana()
        test_dir()

        A = B
        test_ana()

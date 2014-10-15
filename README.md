# ANA

ANA is a project to provide easy distributed data storage for stuff.
It provides every object with a UUID and, when pickled, will first serialize the object's state to a central location and then "pickle" the object into just its UUID.
This is really handy when you have to distribute objects in some distributed system, and you'd rather not pickle the whole object every time you need to send it.

ANA violates some of pickle's assumptions.
Users of pickle often have an implicit assumption that the objects they unpickle will be different (identity-wise) than the objects that they pickle.
This is not the case with ANA; in fact, it has an object cache specifically to avoid this.
Furthermore, depending on the mode of operation, ANA might store the objects centrally, by UUID, where it will be accessed by other instances of ANA.
Because of these things, the objects serialized with ANA should be immutable, if you know what's good for you.

## Usage

To use ANA, simply derive off of `ana.Storable` and implement `_ana_getstate` and `_ana_setstate`.
These should function identically to how you would normally implement `__getstate__` and `__setstate__` for pickle.

Here's an example:

```python
import ana
import pickle

class A(ana.Storable):
	def __init__(self, n):
		self.n = n
		l.debug("Initialized %s", self)
		
	def __repr__(self):
		return "<A %d>" % self.n
		
	def _ana_getstate(self):
		return self.n
		
	def _ana_setstate(self, s):
		self.n = s

# create an instance
a = A()

# First, this instance will be pickled more or less normally.
# For example, the following will actually contain the state,
# and deserializing it will create a new object.
a_pickled = pickle.dumps(a)
b = pickle.loads(a_pickled)
assert b is not a

# Now, let's try assigning this guy a UUID
a.make_uuid()

# If we pickle it again, the only thing returned from the dumps
# is the UUID. The actual state is stored in ANA. Now, when the
# object is unpickled, the identity is preserved.
a_pickled = pickle.dumps(a)
b = pickle.loads(a_pickled)
assert b is a

# There are also functions that provide easy storing and loading.
a_uuid = a.uuid
a.ana_store()
b = A.ana_load(a_uuid) # note that this is a class method
assert b is a
```

There is also a StorableABC subclass, for those that need to store ABCs in this way (i.e., collections.MutableMapping).
You'll need to have it as a subclass in additon to the MutableMapping.
For example:

```python
import ana
import collections

class StorableDict(ana.StorableABC, collections.MutableMapping):
	# your code here
```

Have fun!

## Storage Backends

There are several storage backends for ANA:

| Backend | Description |
|---------|-------------|
| None | With this backend, the pickled states are simply held in a dict. This is the default mode. |
| Directory | With this backend, states are pickled into a directory (by default, "$PWD/pickles"). This can be created by passing the `pickle_dir` option to ana.set_dl() |


# Filename: FileSystem/__init__.py
# Copyright: 2005-2007 James Robey
# Project: XC (please reference the xc.license file for copyright details.)

##modulify
import FrozenSpaceFSAdapter

######## Pointer: the tree creation mechanism #################### # # #    #       #        #
class Pointer:
    def __init__(self, fspath=[]):
        self._pointer_ = FrozenSpaceFSAdapter.Pointer()
        self._fspath_ = fspath

    #return the path to the object joined
    def __str__(self):
        if len(self._fspath_) > 1:
            return '/'.join(self._fspath_[1:])
        else:
            return ''

    #return the path to the object as python list represtation
    def __repr__(self):
        if len(self._fspath_) > 1:
            return '/'.join(self._fspath_[1:])
        else:
            return ''

    def __call__(self):
        if len(self._fspath_) > 1:
            return self._fspath_[1:]
        else:
            return []

    #return the number of items the Pointer contains (folders)  X
    def __len__(self):
        return len(self._pointer_.keys(self._fspath_))

    #if a Pointer object exists with the requested name return it, otherwise return a new Pointer with that name.
    def __getitem__(self, key):
        # TODO: Check 'read' in _pointer_.permissions(key, username) if the space already exists
        if not self.__dict__.has_key(key):
            self.__dict__[key] = Pointer(fspath=self._fspath_ + [key])
        return self.__dict__[key]

    #You can't assign to a Pointer object, but you CAN assign to an attribute inside of one aka F = True is bad, F.a = true is good.
    def __setitem__(self, key, value):
        # TODO: setitem should only raise an exception if value isn't an instance
        # of Pointer!
        raise "Can't assign to a FileSystem object: %s[%s]" % (self.fspath, key)

    #delete an Pointer object using the 'del syntax'
    def __delitem__(self, key):
        # TODO: Check 'delete' in _pointer_.permissions(key, username)
        return self._pointer_.rmspace(self._fspath_ + [key])

    #delete a contained attribute using the 'del syntax'
    def __delattr__(self, key):
        # TODO: Check 'delete' in _pointer_.permissions(key, username)
        # This is a file so you have to actually check key's container.
        if key.endswith('_'):
            del self.__dict__[key]
        else:
            return self._pointer_.rm(self._fspath_ + [key])

    #return an attribute of a given name, None if not there
    def __getattr__(self, key):
        # TODO: Check 'read' in _pointer_.permissions(key,username)
        # This is a file so you have to actually check key's container
        return self._pointer_.get(self._fspath_ + [key], default=None)

    #set an attribute of a given name UNLESS an Pointer of that name already exists, except if so.
    def __setattr__(self, key, value):
        # TODO: If the file exists check for 'update' in _pointer_.permissions(key,username)
        # If it doesn't exist, check for 'create' in _pointer_.permissions(key,username)
        # This is a file so you have to actually check key's container
        if key.endswith('_'):
            self.__dict__[key] = value
        else:
            try:
                self._pointer_.set(self._fspath_ + [key], value)
            except:
                raise `self._fspath_` + `[key]` + `value`

    def goto(self, gotopath):
        if type(gotopath) == type(''):
            gotopath = gotopath.split('/')
        return Pointer(fspath=self._fspath_ + gotopath)

    #if the name given to this doesn't exist inside of the Pointer object, create a new Pointer object there
    def touch(self, key):
        if self._pointer_.touch(self._fspath_ + [key]):
            return self[key]
        else:
            return False

    #reset, clear, empty, what-have-you an Pointer object such that it now exists with no attributes inside
    def empty(self):
        self._pointer_.rmspace(self._fspath_)
        self._pointer_.touch(self._fspath_)
        return self

    #test if a given item OR folder is inside of an Pointer
    def has_key(self, key):
        return self._pointer_.has_key(self._fspath_ + [key])

    def has_space(self, key):
        return self._pointer_.has_space(self._fspath_ + [key])

    #return the names of the attributes the Pointer contains
    def keys(self):
        return self._pointer_.keys(self._fspath_)

    #return the names of the folders the Pointer contains
    def spaces(self):
        self._pointer_.touch(self._fspath_)
        return self._pointer_.spaces(self._fspath_)

    #set a given attribute on an Pointer object
    def set(self, key, value):
        return self._pointer_.set(self._fspath_ + [key], value)

    #get a given attribute value or Pointer object from an Pointer object
    def get(self, key, default=None):
        return self._pointer_.get(self._fspath_ + [key], default=default)

    def rm(self, key):
        return self._pointer_.rm(self._fspath_ + [key])

    def rmspace(self, key):
        return self._pointer_.rmspace(self._fspath_ + [key])

    #given another Pointer object, copy that object into this Pointer object
    def copy(self, copyObj):
        self._pointer_.touch(self._fspath_)
        return self._pointer_.copy(self._fspath_, copyObj._fspath_)

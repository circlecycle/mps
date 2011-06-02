
# Filename: FileSystem/Zodb36.py
# Copyright: 2005-2007 James Robey
# Project: XC (please reference the xc.license file for copyright details.)

"""
Copyright (c) 2006, James Robey
All rights reserved.
"""

import os
import copy
import cPickle as pickle

from mps.bin.Settings import path_to_storage

class Pointer:
    def __init__(self):
        # TODO: look for a dotfile in the space called .space
        # e.g. for a space called foo look for .foo
        #
        # This file contains a pickled dictionary in the following format:
        # dict[filename][username]
        #
        # As a leaf is stored a tuple of the permissions for the current space
        # e.g. ('create','read','update','delete')
        #
        # If the username doesn't exist in the dict return ()
        pass

    def permissions(self, path, username):
        # TODO: Read the dict we slurped in init and return the tuple for the
        # user on the given path.  Let FrozenSpace.py deal with the fallout!
        pass

    def resolvePath_(self, path, name=""):
        """given a path and an optional name, construct the fully qualified path using the prefix stored in path_to_storage"""

        path = '/'.join(path)
        return "%s%s" % (path_to_storage, path)

    def resolvePathToPickleOrText_(self, path):
        """
             if a name is given, check first to see if there is a .pickle of the same to use, 
             which is used instead of the basename at all times
        """

        path = '/'.join(path)
        path = "%s%s" % (path_to_storage, path)
        picklePath = "%s.pickle" % path

        if os.path.exists(picklePath):
            return picklePath
        else:
            return path

    def resolveDir_(self, path):
        path = '/'.join(path[:-1])
        return "%s%s" % (path_to_storage, path)

    def keys(self, path):
        if path[-1].startswith('.'): return False
        k = os.listdir(self.resolvePath_(path))
        output = []
        #we have to remove the .pickle appellate if it exists
        for i in k:
            if i.endswith('.pickle'):
                output.append(i[:-7])
            else:
                output.append(i)
        return output

    def spaces(self, path):
        if path[-1].startswith('.'): return False
        spaceList = os.listdir(self.resolvePath_(path))
        return [x for x in spaceList if not x.startswith('.')]

    def has_key(self, path):
        """do we have a key with the given name? """
        if path[-1].startswith('.'): return False
        return os.path.exists(self.resolvePath_(path))

    def has_space(self, path):
        """do we have a space with a given name"""
        return os.path.exists(self.resolvePath_(path))

    def touch(self, path):
        """make a new space or leave it alone if it exists"""
        if path[-1].startswith('.'): return False
        if not os.path.exists(self.resolvePath_(path)):
            os.makedirs(self.resolvePath_(path))

    def set(self, path, value=None):
        """set a given key to a given value"""

        if path[-1].startswith('.'): return False

        #?ensure the directory structure needed exists.
        try:        os.makedirs(self.resolveDir_(path))
        except: pass

        #? Open the file and store it's contents as either a string (if its a string) OR serialized object
        #? if it IS a object that needs to be serialized, then give it a special extension so we know
        if [type(''), type(u'')].count(type(value)):
            fp = file(self.resolvePath_(path), 'w')
            fp.write(value)
        else:
            newpath = "%s.pickle" % self.resolvePath_(path)
            fp = file(newpath, 'w')
            fp.write(pickle.dumps(value))
        fp.close()

    def get(self, path, default=None):
        #? given a path, return the value at the given dom element at that path

        if path[-1].startswith('.'): return default

        try:
            fp = file(self.resolvePathToPickleOrText_(path))
            value = fp.read()
            fp.close()
        except:
            return default

        #? if it's a pickle return it, or just return the raw value. (we'd' hope the 
        #? pickle class can tell it's not a pickle and except quickly but don't know that for sure
        try:
            return pickle.loads(value)
        except:
            return value

    def rmspace(self, path):
        if path[-1].startswith('.'): return False
        os.rmdir(self.resolvePath_(path))

    def rm(self, path):
        if path[-1].startswith('.'): return False
        os.remove(self.resolvePath_(path))

    def copy(self, path, pathOfObj):
        if path[-1].startswith('.'): return False
        copy.copy(self.resolvePath_(path), self.resolvePath_(pathOfObj))

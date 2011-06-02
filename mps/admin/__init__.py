
from mps import Servlet
from mps.bin.Utils import Tag

class shadow(Servlet):
    """ initialize a set of default users non destructively to
        if the system currently has no users.
    """

    def __call__(self):
        self.acl.setShadowDefaults();
        return Tag('status', {'msg':"default shadow set"}).render();

class credentials(Servlet):
    """ return the users name and groups they belong to in a pretty xml format"""
    def __call__(self):

        #login action?
        if self.args['name'] and self.args['pw']:
            self.acl.login(self.args['name'], self.args['pw'])

        #logout action?
        if self.args['logout']:
            self.acl.logout()

        #render current credentials
        t = Tag('set')
        t.append(Tag('user', {'name':self.acl.user}))
        for group in self.acl.getGroups():
            t.append(Tag('group', {'name':group}))

        return t.render()

class listusers(Servlet):
    """ list all of the users currently listed in the system """

    allowed = ['admins']

    def __call__(self):
        t = Tag('users')
        [t.append(Tag('user', {'name':x})) for x in self.acl.getUsers()]
        return t.render()

class status(Servlet):
    """ show the status of the current user """

    def __call__(self):
        msg = "Currently logged in as '%s' with a session id of '%s'." % (self.acl.user, self.acl.sessid)
        return Tag('status', {"msg":msg}).render()

class adduser(Servlet):
    """ given a username stored in the 'name' query string, 
        a password stored in the 'pw' query string,
        and a comma seperated list of groups stored in the 'groups' query string,
        add the user to the system 
    """

    allowed = ['admins']

    def __call__(self):
        #collect info from the query string
        name = self.args['name']
        pw = self.args['pw']
        groups = self.args['groups']

        #massage group string into list
        if not groups: groups = []
        else:          groups = [x.strip() for x in groups.split(',')]

        #add the new user
        self.acl.addUser(name, {'pw':pw, 'groups':groups})

        #return status string
        msg = "user %s added" % name
        return Tag('status', {"msg":msg}).render()

class removeuser(Servlet):
    """ given a username stored in the 'name' query string, remove it from the system """

    allowed = ['admins']

    def __call__(self):
        #collect info from the query string
        name = self.args['name']

        #remove user
        self.acl.removeUser(name)

        #return status string
        msg = "user %s removed" % name
        return Tag('status', {"msg":msg}).render()


class loadtest(Servlet):
    def __call__(self):
        return Tag('status', {"msg":"Dummy Called"}).render()




# Filename: Identity.py
# Copyright: 2005-2010 James Robey
# Project: MPS (please reference the MPS.license file for copyright details.)

import time, os, random, md5, shelve, os.path
from mod_python import apache, Cookie
from mps.bin.Settings import path_to_sessions, db_extension
from mps.bin import Utils

class Session:
    unauthorized = 'anonymous'
                
    def __init__(self, req):
        """get, extract info, and do upkeep on the session cookie. This determines what the sessid and user are 
             for this request."""
        #pass the request in making in so we can edit it later if requested (ACL for example)
        self.ip = req.connection.remote_ip
        c = Cookie.get_cookies(req)
        if not c.has_key('mps'):
            self.sessid = Uid().new_sid(req)
        else:
            c = c['mps']
            self.sessid = c.value
            
        #make new cookie so the cycle continues
        c = Cookie.Cookie('mps', self.sessid)
        c.path = '/'
        Cookie.add_cookie(req, c)
        
        self.session_path = "%s%s"%(path_to_sessions, self.sessid)
        self.full_session_path = "%s%s"%(self.session_path, db_extension)
        
        #use previous authenication until cookie is reevaluated, if they are officially logged in (in Instance)
        if os.path.exists(self.full_session_path):
            session = shelve.open(self.session_path, 'rw')
            self.user  = session['USER_']
            session.close()
        else:
            self.user = self.unauthorized
        
    def login(self, user):
        self.user = user
        session = shelve.open(self.session_path, 'c')    
        session['USER_'] = self.user
        session.close()
        
    def logout(self):
        """remove the session's entry and set self.users to unauthorized, logging the user out."""
        if self.user != self.unauthorized:
            self.user = self.unauthorized
            os.remove(self.full_session_path)
        

#one of these per request.
#fundamentally this is tied into the SessionHandler, which is relied on to return credentials.
#the session is estabilshed before the ACL, but it is then wrapped here to provide easier
#access from an API perspective.

class ACL:
    shadowDefault = {
        "anonymous":  { 'pw':'',        'groups':['anonymous', 'notloggedin'] },
        "jamesr":     { 'pw':'letmein', 'groups':['anonymous', 'users', 'teachers'] },
        "admin":      { 'pw':'letmein', 'groups':['anonymous', 'users', 'admins'] },
        "bob":        { 'pw':'letmein', 'groups':['anonymous', 'users', 'bobsgroup'] },
        "ted":        { 'pw':'letmein', 'groups':['anonymous', 'users',] },
    }
        
    def __init__(self, session, userspace):
        global setup
        #this is the session handler from the Adapters.apache2 module
        self.session = session
        self.userspace = userspace
        self.refreshState()
        
    def refreshState(self):
        self.user = self.session.user
        self.sessid = self.session.sessid
        
        #are they registered as anonymous?
        self.anonymous = (self.user == self.session.unauthorized)
        
        #retrieve their info
        if self.anonymous:
            self.info = self.shadowDefault['anonymous']
        else:
            self.info = self.userspace[self.user].info                   
            
    def login(self, newuser, pw):
        #does the user exist and does 
        if self.userspace.has_space(newuser) and (self.userspace[newuser].info['pw'] == pw):
            self.session.login(user=newuser)
            
        #refresh the state and return the pw_matched flag
        self.refreshState()
        #return true if the operation resulted in a logged in user
        return (self.user != self.session.unauthorized)
    
    def logout(self):
        #logout the active user
        self.session.logout()
        #and refresh the state of attributes for inspection by other modules
        self.refreshState()
        
    #these get information on group status
    def getGroups(self):     
        return self.info['groups']
        
    def isInGroup(self, group):
        if Utils.intersect(group, self.info['groups']):
            return True
        return False
        
    def addToGroup(self, group):
        if group not in self.info['groups']:
            self.info['groups'].append(group)
            self.user.info = self.info
            
    def removeFromGroup(self, group):
        if group in self.info['groups']:
            del self.info['groups'][self.info['groups'].index(group)]
            self.user.info = self.info
            
    #These are used for the management of the users
    def setShadowDefaults(self):
        """use me to initialize a userspace from above dict - run just once, usually, or for debugging."""
        for user in self.shadowDefault.keys():
            #if not self.userspace.has_key(user):
            self.userspace[user].info = self.shadowDefault[user]
            
    def getUsers(self):      
        return self.userspace.spaces()
        
    def getGroupsFor(self, user):
        if self.userspace.has_space(user):
            info = self.userspace[user].info 
            return info['groups']
        else:
            return []
        
    def isUserInGroup(self, user, groups):
        if Utils.intersect(groups, self.userspace[user].groups):
            return True
        return False
        
    def addUserToGroup(self, user, group):
        info = self.userspace[user].info
        if group not in info['groups']:  
            del info['groups'][info['groups'].index(group)]
            self.userspace[user].info = info
            
    def removeUserFromGroup(self, user, group):
        info = self.userspace[user].info
        if group in info['groups']:  
            info['groups'].append(group)
            self.userspace[user].info = info
            
    def addUser(self, name, info=False):
        if not self.userspace.has_space(name):
            if not info:
                self.userspace[user] = {'pw':"12345", 'groups':[]}
            else:
                self.userspace[user] = info
                
    def removeUser(self, user):
        if self.userspace.has_space(user):
            del self.userspace[user]
            
    def changePassword(self, user, password):
        if self.userspace.has_space(user):
            userinfo = self.userspace[user].info
            userinfo['pw'] = password
            acl[user].info = userinfo

#borrowed from the mod_python Session.py machinery
class Uid:
    def __init__(self):
        self.rnd_gens = self.init_rnd()
        self.rnd_iter = iter(self.rnd_gens)

    def init_rnd(self):
        """ initialize random number generators
        this is key in multithreaded env, see
        python docs for random """

        # query max number of threads
        gennum = apache.AP_MPMQ_MAX_SPARE_THREADS
        # make generators
        # this bit is from Python lib reference
        g = random.Random(time.time())
        result = [g]
        for i in range(gennum - 1):
            laststate = g.getstate()
            g = random.Random()
            g.setstate(laststate)
            g.jumpahead(1000000)
            result.append(g)
        return result

    def get_generator(self):
        # get rnd_iter.next(), or start over
        # if we reached the end of it
        try:
            return self.rnd_iter.next()
        except StopIteration:
            # the small potential for two threads doing this
            # seems does not warrant use of a lock
            self.rnd_iter = iter(self.rnd_gens)
            return self.rnd_iter.next()

    def new_sid(self, req):
        # Make a number based on current time, pid, remote ip
        # and two random ints, then hash with md5. This should
        # be fairly unique and very difficult to guess.

        t = long(time.time()*10000)
        pid = os.getpid()
        g = self.get_generator()
        rnd1 = g.randint(0, 999999999)
        rnd2 = g.randint(0, 999999999)
        ip = req.connection.remote_ip

        return md5.new("%d%d%d%d%s" % (t, pid, rnd1, rnd2, ip)).hexdigest()
     
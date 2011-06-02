
# Filename: mps/__init__.py
# Copyright: 2005-2010 James Robey
# Project: XC (please reference the xc.license file for copyright details.)

import os

#our base path
basepath = os.path.dirname(__file__)

#START MODPYTHONSERVER
from mod_python import apache, util

#and our own utilities:
from mps.bin import Utils, Identity, FrozenSpace
from mps.bin.Settings import exceptionHTML, metatypes

#and the django templating engine!
#   tell the django system to get it's settings from this module (for TEMPLATE_DIRS and it's ilk)
os.environ["DJANGO_SETTINGS_MODULE"] = "mps"
#   tell the django system to search for templates in the 'templates' directory
TEMPLATE_DIRS = ("%s/templates" % os.path.dirname(__file__))
#   actually import the template and context classes from django (all we use)
from django.template import Template, Context
#   and import the loader, which is necessary to use the extends keyword in templates
import django.template.loader

def Publisher(request):
    try:
        #using the request, determine what object to call
        path_split = request.uri.split('/')[1:]
        
        #if the path refers to our static directory, then serve a file in that directory
        #based on path. There is no access control or templating provided for these files
        #meant for things like javascript and css. Note that even sessions are not established
        #for such files
        if path_split[0] == "static":
            #use the extension to set the metatype
            extension = path_split[-1].split('.')[-1]
            if metatypes.has_key(extension):
                request.content_type = metatypes[extension]
            else:
                request.content_type = "text/html"
            #get the full path to the requested static thing to serve
            path = "%s/static/%s"%(basepath, '/'.join(path_split[1:]))
            #read in the data from the file and return it to the client.
            buf = file(path).read()
            request.write(buf)
            return apache.OK
           
        #if we're here then the request is tendered to what is presumed to be a Servlet.
        #if not, an exception is raised. All dynamic or protected content is thus generated.
        
        #Initialize storage
        space = FrozenSpace.Pointer()
        
        #initialize the session
        session = Identity.Session(request)
        
        #initialize the user
        acl = Identity.ACL(session, space['acl'])
        
        #derive the full namespace of the Servlet e.g. a.b.c.d from /a/b/c/d
        module_name = "%s.%s"%( __name__, '.'.join( path_split[:-1] ) )
        class_name = path_split[-1]
                                                                     
        #create the context
        context = {
            "request":request,
            "args":Utils.ArgsShell(util.FieldStorage(request)),
            "uri":request.uri,
            "ip":request.connection.remote_ip,
            "session":session,
            "content_type":"text/html",
            "acl":acl,
            "local":FrozenSpace.Pointer(fspath=['local']+path_split),
            "module":FrozenSpace.Pointer(fspath=['module']+path_split[:-1]),
            "here":FrozenSpace.Pointer(fspath=['here']+[acl.user]+path_split),
            "user":FrozenSpace.Pointer(fspath=['users']+[acl.user]),
        }

        #get the servlet module to import
        ServletModule = Utils.importFromString(module_name)

        #get the servlet object to instantiate
        ServletClass = getattr(ServletModule, class_name)

        #instantiate the servlet
        servlet = ServletClass(context)
        
        #test to make sure we are calling a servlet. No funny business!
        if not isinstance(servlet, Servlet):
            raise Exception("Sorry, the path does not resolve to a Servlet")

        #run the servlet and save the response to send back
        response = servlet()

        #write the results back to the stream.
        request.content_type = servlet.content_type
        request.write(str(response))
        
    except Exception, e:
        request.content_type = "text/html"
        errormsg = exceptionHTML % (request.uri, `e`) 
        request.write(errormsg)
        
    return apache.OK
        
class Servlet:
    """ Base class to enable servlet classes to be nice and small and automated """
    
    allowed = []
    template = None
    
    def __init__(self, context):
        """ on init, copy over attributes from the context, 
            and if they aren't authorized to run the servlet,
            change the __call__ method to the dummy method nothing__
            that will 
        """
        
        #copy over the attributes from the context into the servlets namespace
        self.context = context
        for key in context.keys():
            setattr(self, key, context[key])
            
        #check to see if the current user is denied access to the servlet
        #if they are denied, overwrite the __call__ function with a dummy.
        if self.allowed and not context['acl'].isInGroup(self.allowed):
            self.__dict__['__call__'] = self.__denied__
            return   
            
        #if a template has been defined, replace the __call__ function
        #with the kickoff function to process the given template.
        if self.template != None:
            self.__dict__['__call__'] = self.processTemplate
        
    def __denied__(self):
        """if the user of this servlet doesn't have permission to run it, 
           substitute this function in place of __call__, ensuring that the servlet 
           doesn't run anything"""
        return """<div align="center">Permission to run this servlet denied.</div>"""
        
    def processTemplate(self):
        """if a template has been specified, i'll be subbed for the __call__ function
           causing a template to be rendered with the current servlet as context and
           the path (in the self.template variable) used ads the HTML source"""
        global basepath
        fullpath = "%s/templates/%s"%(basepath, self.template) 
        buf = file(fullpath).read()
        #set up our namespace with self, for better looking references
        self.__dict__['self'] = self
        #this is for the django machinery that belches without it
        return Template(buf).render(Context(self.__dict__))
 


from mod_python import apache
import time, os, random, md5

def intersect(set1, set2):
    """
    Returns intersection of tuples/lists of data
    
    """
    results = []
    for entry in set1:
      if entry in set2:
        results.append(entry)
    return results

class ArgsShell:
    def __init__(self, fieldstorage):
      self.fieldstorage = fieldstorage
      
    def __getitem__(self, key):
      return self.fieldstorage.get(key, None)
      
    def keys(self):
      return self.fieldstorage.keys()
      
    def has_key(self, key):
      return self.fieldstorage.has_key(key)
      
    def upload(self):
      if self.fieldstorage.has_key('Filename'): 
          fn = self.fieldstorage['Filename'].value
          fd = self.fieldstorage['Filedata'].value
          return (fn, fv)                      
          
      return None

def importFromString(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
    
class Tag:
    """ Make a widely used convenience class availble, one to create nested xml trees 
        example usage:
        
        e = Tag('set')
        e.add( Tag('person', {'name':'james'}) )
        print e.render()
        
        will give:
        
        <set>
            <person name="james"/>
        </set>
        
    """

    from xml.sax import saxutils

    def __init__(self, tagname, attributes={}):
        self.tagname = tagname
        self.attributes = attributes
        self.children = []
        self.text = ""

    def append(self, child):
        self.children.append(child)
	return self
        
    def appendText(self, text):
        self.text += text;
	return self

    def render(self, topmost=True):
        #each render op will have a stack
        stack = []
        #each render op will have a certain number of attributes, or zero
        attrs = ""

        #convert the dictionary of attributes into an xml form
        for key in self.attributes:
            attrs += " %s=\"%s\""%(key, str(self.attributes[key]))

        #place on the stack the opening tag, note that if there are no children we open it
        if not self.children and not self.text:
            stack.append("<%s%s/>"%(self.tagname, attrs))
            
        else:
            stack.append("<%s%s>"%(self.tagname, attrs))

            #for each of the children extend the stack by the result of their render method
            for child in self.children:
                stack.extend(child.render(topmost=False))
                
            if self.text:
                stack.append( self.saxutils.escape(self.text) )

            #place on the stack the closing tag
            stack.append("</%s>"%self.tagname)

        #we are done return the stack
        if topmost:
            return ''.join(stack)
        else:
            return stack


from mps import Servlet
        
class templatetest(Servlet):
    allowed = ['users', 'admin', 'anonymous']
    template = "test.html"
        
class extendo(templatetest):
    def content(self):
        return "here is new content"
        
class notservlet:
    def __init__(self, context):
        pass
        
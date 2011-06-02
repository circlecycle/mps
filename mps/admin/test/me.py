

from mps import Servlet

class please(Servlet):
    def __call__(self):
        return self.acl.user

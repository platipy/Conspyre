from types import ModuleType
import sys
import time
import requests

conspyre_modules = {}

class ConspyreConnection(object):
    def __init__(self):
        self.name = self.__class__.__name__
        self.username = ""
        self.password = ""
        self.teacher = ""
        self.school = ""
    
    def login(self, username, password):
        print "Test"
        
    def _make_server_command(self, command):
        def _server_command(**kwargs):                
            metadata = { 'username' : self.username,
                         'password' : self.password,
                         'teacher'  : self.teacher,
                         'school'   : self.school,
                         'module'   : self.name,
                         'time'     : time.time(),
                         'command'  : command,
                         'data'     : kwargs
                     }
            # upload metadata
            # if the command wasn't found, then return a list of "near-matches"
            return metadata
        return _server_command
    
    def __getattr__(self, name):
        return self._make_server_command(name)
            

class module(ModuleType):
    def __getattr__(self, name):
        # if we have already loaded the module, return it
        if name in conspyre_modules:
            return conspyre_modules[name]
        
        # otherwise create an instance of it now
        c = type(name, (ConspyreConnection,), dict())
        conspyre_modules[name] = c()
        return conspyre_modules[name]

old_module = sys.modules['conspyre']
new_module = sys.modules['conspyre'] = module('conspyre')
new_module.__dict__.update({
    '__file__' : __file__,
    '__package__' : 'conspyre',
    # '__path__' : __path__,
    '__doc__' : __doc__
    })

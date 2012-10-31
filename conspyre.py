from types import ModuleType
import sys
import time
import requests
try:
    import json
except:
    import simplejson as json
import fix_json

settings = json.loads(open('conspyre.config','rb').read())

conspyre_modules = {}

class ConspyreConnection(object):
    def __init__(self):
        self.module = self.__class__.__name__
        self.student_id = None
        self.student_name = ""
        self.student_email = ""
        self.student_password = ""
        self.teacher = settings['teacher']
        self.school = settings['school']
        self.server = settings['server']
        self.connected = False
    
    def login(self, student_email, student_password):
        r = requests.get(self.server+"/conspyre/login/", 
                         params={"email" : student_email,
                                 "password" : student_password})
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
        self.student_email = student_email
        self.student_password = student_password
        self.student_name = r['data']['name']
        self.student_id = int(r['data']['id'])
        
    def reset_password(self, student_email, student_password):
        r = requests.get(self.server+"/conspyre/reset_password/", 
                         params={"email" : student_email,
                                 "password" : student_password})
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
        self.student_email = student_email
        self.student_password = student_password
        self.student_name = r['data']['name']
        self.student_id = int(r['data']['id'])
    
    def register(self, student_email, student_name, student_password):
        r = requests.get(self.server+"/conspyre/register/", 
                         params={"email" : student_email,
                                 "name" : student_name,
                                 "password" : student_password})
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
        self.student_email = student_email
        self.student_password = student_password
        self.student_name = student_name
        self.student_id = int(r['data']['id'])
    
    def request_reset(self, student_email):
        r = requests.get(self.server+"/conspyre/request_reset/", 
                         params={"student" : student_email,
                                 "teacher" : self.teacher})
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
            
    def password_is_resetable(self, student_email):
        r = requests.get(self.server+"/conspyre/password_resetable/", 
                         params={"student" : student_email})
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        return r['data']['status']
        
    def logout(self):
        self.student_id = None
        self.student_name = ""
        self.student_email = ""
        self.student_password = ""
        
    def get_teacher_list(self):
        r = requests.get(self.server+"/conspyre/teacher_list/")
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
        return r['data']['teachers']
    
    def get_student_list(self, teacher):
        if teacher is None:
            teacher = ""
        r = requests.get(self.server+"/conspyre/student_list/",
                         params={"teacher" : teacher})
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
        return r['data']['students']
        
    def connect(self, server = None):
        if server is not None:
            self.server = server
        r = requests.get(self.server+"/test/"+self.module)
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['message'])
        self.connected = True
        
    def _make_server_command(self, command):
        def _server_command(**kwargs):
            metadata = { 'metadata' : {'email'    : self.student_email,
                                       'password' : self.student_password,
                                       'id'       : self.student_id,
                                       'teacher'  : self.teacher,
                                       'school'   : self.school,
                                       'module'   : self.module,
                                       'time'     : time.time(),
                                       'command'  : command},
                         'data'     : dict(kwargs)
                     }
            assert self.connected, "You are not connected; cannot call command %s." % command
            r = requests.post(self.server+'/modules/'+self.module+'/'+command,
                              data = json.dumps(metadata))
            if r != 200:
                r.raise_for_status()
            r = json.loads(r.content)
            return r['data']
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

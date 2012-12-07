from types import ModuleType
import sys
import time
import requests
try:
    import json
except:
    import simplejson as json
import fix_json

import requests

conspyre_modules = {}

class ConspyreException(Exception):
    def __str__(self):
        return """There was an ambiguous exception that occurred while attempting to communicate with the server."""

class HTTPError(ConspyreException):
    def __str__(self):
        return """An HTTP error occurred. Please check the server to confirm that it is running correctly."""
        
class ServerError(ConspyreException):
    def __str__(self):
        return """There was an error on the server, check the server's logs for errors."""

class ConnectionError(ConspyreException):
    def __str__(self):
        return """A Connection error occurred. Recheck your internet connection and make sure the server is running."""

class Timeout(ConspyreException):
    def __str__(self):
        return """The request timed out."""

class UserNotFoundException(ConspyreException):
    def __str__(self):
        return """You must log in before you make that call."""
        
class LoginException(ConspyreException):
    def __str__(self):
        return """You must log in before you make that call."""
        
class ModuleNotFoundException(ConspyreException):
    def __str__(self):
        return """That module does not fully exist yet, and it could not be created. Please fix it's setup on the server."""
        
class PasswordMismatchException(ConspyreException):
    def __str__(self):
        return """The username and password do not match."""
        
class UsernameExistsException(ConspyreException):
    def __str__(self):
        return """That username already exists."""
        
class ResetNotApprovedException(ConspyreException):
    def __str__(self):
        return """Your teacher hasn't approved your password reset yet."""
        
class ResetAlreadyRequestedException(ConspyreException):
    def __str__(self):
        return """You have already requested a password reset from this teacher."""
        
exceptions = {"PasswordMismatch": PasswordMismatchException,
              "ModuleNotFound": ModuleNotFoundException,
              "UserNotFound": UserNotFoundException,
              "UsernameExists": UsernameExistsException,
              "ResetNotApproved": ResetNotApprovedException,
              "ResetAlreadyRequested": ResetAlreadyRequestedException}
        
class ConspyreConnection(object):
    """
        This is the main class for connecting to a server. Besides the
        explicitly defined functions, you can make other calls to the server by
        using conspyre.<module_name>.<method_name>(). All parameters must be
        named.
        
        *connected*
        *logged_in*
        *teacher*
    """
    
    def raise_error_from_status(self, request_object):
        status = request_object.status_code
        if status == 500:
            raise HTTPError()
        else:
            request_object.raise_for_status()
    
    def __init__(self):
        self.module = self.__class__.__name__
        self.id = None
        self.name = ""
        self.email = ""
        self.password = ""
        self.teacher = ""
        self.server = ""
        self.connected = False
        self.logged_in = False
        self.devel = True
        
    def log(self, message):
        """
        Logs a *message* string into the module's log (stored in JSON on the 
        server). This could be used to easily dump crash logs, for instance.
        """
        id = -1 if self.id is None else self.id
        data = { 'metadata' : {'email'    : self.email,
                                   'password' : self.password,
                                   'id'       : id,
                                   'teacher'  : self.teacher,
                                   'module'   : self.module,
                                   'time'     : time.time()
                                   },
                     'message'     : message}
        print data
        try:
            r = requests.post(self.server+'/logging/'+self.module,
                              data = json.dumps(data))
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            raise Exception(r['error'])
    
    def login(self, username, password, teacher_id = None):
        """
        Logs the user named by the *username* into the server using the
        *password*. This method must be called before any methods that 
        assume a user.
        
        Optionally, a teacher's id can also be passed in. This will create
        a Teaching association between this student and teacher.
        
        """
        params={"email" : username,
                    "password" : password}
        if password is not None:
            params['teacher'] = teacher_id;
        try:
            r = requests.get(self.server+"/conspyre/login/", 
                            params=params)
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            self.raise_error_from_status(r);
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
        self.email = username
        self.password = password
        self.name = r['data']['name']
        self.id = int(r['data']['id'])
        self.logged_in = True
        
    def reset_password(self, username, password):
        """
        Changes *username*'s password to *password*. After this function is called, 
        the user will also be logged in.
        
        Does not require login.
        """
        params={"email" : username,
                    "password" : password}
        try:
            r = requests.get(self.server+"/conspyre/reset_password/", 
                            params=params)
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
        self.email = username
        self.password = password
        self.name = r['data']['name']
        self.id = int(r['data']['id'])
    
    def register(self, username, name, password, teacher_id = None):
        """
        Creates a new user with the *username*, *name*, and *password*. After this
        function is called, the user will also be logged in.
        
        Optionally, a teacher's id can also be passed in. This will create
        a Teaching association between this student and teacher.
        
        Does not require login.
        """
        params={"email" : username,
                    "name" : name,
                    "password" : password}
        if password is not None:
            params['teacher'] = teacher_id;
        try:
            r = requests.get(self.server+"/conspyre/register/", 
                             params= params)
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
        self.email = username
        self.password = password
        self.name = name
        self.id = int(r['data']['id'])
    
    def request_reset(self, username):
        """
        Sends a request to the current teacher to reset the password for
        *username*.
        
        Does not require login.
        """
        try:
            r = requests.get(self.server+"/conspyre/request_reset/", 
                            params={"student" : username,
                                    "teacher" : self.teacher})
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
            
    def password_is_resetable(self, username):
        """
        Returns whether the current teacher has approved a reset for *username*.
        
        Does not require login.
        """
        try:
            r = requests.get(self.server+"/conspyre/password_resetable/", 
                            params={"student" : username})
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        return r['data']['status']
        
    def logout(self):
        """
        Logs the currently logged in user out of the system, most likely so that
        another user can log in. This does not actually communicate with the
        server.
        """
        if not self.logged_in:
            raise LoginException()
        self.id = None
        self.name = ""
        self.email = ""
        self.password = ""
        self.logged_in = False
        
    def get_teacher_list(self):
        """
        Returns a list of all the teachers. This will be a list of dictionaries
        with the keys "id" (a number that uniquely identifies a teacher), "name"
        (a name that children will recognize as their teacher), and "username"
        (a unique name that identifies them, but will probably not be
        recognizeable to a child).
        
        Does not require login.
        """
        try:
            r = requests.get(self.server+"/conspyre/teacher_list/")
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
        return r['data']['teachers']
    
    def get_student_list(self, teacher):
        """
        Returns a list of all the students associated with a specific teacher.
        This will be a list of dictionaries with the keys "id" (a number that
        uniquely identifies a student), "username" (a unique name that 
        identifies them and hopefully they've memorized), and a "name" (a name
        that they will recognize as their own but may not be unique).
        
        Does not require login.
        """
        if teacher is None:
            teacher = ""
        try:
            r = requests.get(self.server+"/conspyre/student_list/",
                            params={"teacher" : teacher})
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            r.raise_for_status()
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
        return r['data']['students']
        
    def connect(self, server = 'http://127.0.0.1:8080', devel=True):
        """
        Establishes a connection to the *server*. This function must be called
        before any others.
        """
        self.server = server
        self.devel = devel
        try:
            r = requests.get(self.server+"/test/"+self.module)
        except requests.exceptions.ConnectionError, ce:
            raise ConnectionError()
        except requests.exceptions.Timeout, to:
            raise Timeout()
        except requests.exceptions.HTTPError, he:
            raise HTTPError()
        if r.status_code != 200:
            return self.raise_error_from_status(r)
        r = json.loads(r.content)
        if r['type'] == "error":
            if r['error'] in exceptions:
                raise exceptions(r['error'])
            else:
                raise Exception(r['error'])
        self.connected = True
        
    def disconnect(self):
        """
        Disconnects from the server. This does not communicate with the server.
        """
        self.connected = False
        
    def _make_server_command(self, command):
        def _server_command(**kwargs):
            metadata = { 'metadata' : {'email'    : self.email,
                                       'password' : self.password,
                                       'id'       : self.id,
                                       'teacher'  : self.teacher,
                                       'module'   : self.module,
                                       'time'     : time.time(),
                                       'command'  : command},
                         'data'     : dict(kwargs)
                     }
            if not self.logged_in:
                raise LoginException()
            r = requests.post(self.server+'/modules/'+self.module+'/'+command,
                              data = json.dumps(metadata))
            if r.status_code != 200:
                return self.raise_error_from_status(r)
            r = json.loads(r.content)
            if r['type'] == 'error':
                raise Exception(r['error'], r['data'])
            if len(r['data']) == 0:
                return None
            if len(r['data']) == 1:
                return r['data'][0]
            else:
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

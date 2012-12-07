import sys
import conspyre
import time
from conspyre import ConnectionError, ModuleNotFoundException

try:
    conspyre.template.connect(server= 'http://127.0.0.1:8080')
except Exception, me:
    print me
    print "Skipping creation"

conspyre.template.login('Template_dog_lover', 'pass')

conspyre.template.put(key="points", value=100)
print conspyre.template.get(key="points")
print conspyre.template.has(key="points")
conspyre.template.update(dict={"points":101, "title":"Lord Awesome"})
print conspyre.template.items()

print conspyre.template.has(key="points")
print conspyre.template.items()
print conspyre.template.put(key="points", value=100)
print conspyre.template.get(key="points")
print conspyre.template.has(key="clothes")
print conspyre.template.update(pairs={"points":200, "clothes": "Alpha, Beta"})
print conspyre.template.get(key="points")
print conspyre.template.items()
conspyre.template.logout()

sys.exit()
    
print "Testing Logging"
conspyre.template.log("Exploding!")
conspyre.template.log("Another!!")
conspyre.template.log("Puppies!")
conspyre.template.disconnect()

print "Attempting to connect to the school server."
conspyre.template.connect(server= 'http://127.0.0.1:8080', school= 'Chester Community Charter School')
    
try:
    print "Registering Becky"
    conspyre.template.register('rtrexler', 'Becky Trexler', 'pass')
except ConnectionError, c:
    print c
except Exception, e:
    print e

print "Logging Becky in and out"
conspyre.template.login('rtrexler', 'pass')
conspyre.template.logout()

print "Viewing Teachers"
teachers = conspyre.template.get_teacher_list()
print teachers

print "Setting Teacher to Cory"
conspyre.template.teacher= teachers[0]['id']

print "Viewing Students"
print conspyre.template.get_student_list(None)

print "Requesting Password Reset"
try:
    conspyre.template.request_reset('rtrexler')
except Exception, e:
    print e
    print "Skipping password reset."

attempts_left = 5
print "Waiting for password to be reset..."
print "(Log into the server to reset the password)"
while not conspyre.template.password_is_resetable('rtrexler') and attempts_left:
    time.sleep(4)
    attempts_left-= 1
    print "... Password still not reset. Trying %d more times." % attempts_left
if attempts_left:
    pass
    #conspyre.template.reset_password('rtrexler', 'password')
    
conspyre.template.login('dog_lover', 'pass')

print "Welcome %s!" % conspyre.template.student_name
print "First", conspyre.template.get_dog_list()['dogs']
dogs = conspyre.template.get_dog_list()['dogs']
conspyre.template.rename_dog(id=dogs[0]['id'], name='Alfred')
print "Renamed", conspyre.template.get_dog_list()['dogs']
conspyre.template.add_dog(breed='poodle', name='dogbert')
print "Added", conspyre.template.get_dog_list()['dogs']
dogs = conspyre.template.get_dog_list()['dogs']
conspyre.template.release_dog(id=dogs[0]['id'])
print "Removed", conspyre.template.get_dog_list()['dogs']
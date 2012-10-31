import conspyre
import time

conspyre.example.connect()

try:
    print "Registering Becky"
    conspyre.example.register('rtrexler', 'Becky Trexler', 'pass')
except Exception, e:
    print e

print "Logging Becky in and out"
conspyre.example.login('rtrexler', 'pass')
conspyre.example.logout()

print "Viewing Teachers"
print conspyre.example.get_teacher_list()

print "Setting Teacher to Cory"
conspyre.example.teacher= 'acbart'

print "Viewing Students"
print conspyre.example.get_student_list(None)

print "Requesting Password Reset"
try:
    conspyre.example.request_reset('rtrexler')
except Exception, e:
    print e
    print "Skipping password reset."

while not conspyre.example.password_is_resetable('rtrexler'):
    print "Waiting for password to be reset..."
    time.sleep(4)

conspyre.example.reset_password('rtrexler', 'password')
    
conspyre.example.login('dog_lover', 'pass')

print "Welcome %s!" % conspyre.example.student_name
print "First", conspyre.example.get_dog_list()['dogs']
dogs = conspyre.example.get_dog_list()['dogs']
conspyre.example.rename_dog(id=dogs[0]['id'], name='Alfred')
print "Renamed", conspyre.example.get_dog_list()['dogs']
conspyre.example.add_dog(breed='poodle', name='dogbert')
print "Added", conspyre.example.get_dog_list()['dogs']
dogs = conspyre.example.get_dog_list()['dogs']
conspyre.example.release_dog(id=dogs[0]['id'])
print "Removed", conspyre.example.get_dog_list()['dogs']

#print conspyre.broadway.login("blah", "blah")
#conspyre.broadway.teacher = "Dr. Burns"
#print conspyre.broadway.teacher
#print conspyre.broadway.upload_story(story="This is a story about a puppy.", title="Puppy Story");
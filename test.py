from django.db import models

class Roles(models.IntegerChoices):
    NOT_DEFINED = 1, 'not defined'
    STUDENT = 2, 'student'
    TEACHER = 3, 'teacher'
    SECRETARY = 5, 'secretary'
    SUPERVISOR = 7, 'supervisor'
    ADMIN = 13, 'admin'
    TEACHER_SUPERVISOR = TEACHER[0]*SUPERVISOR[0], 'teacher and supervisor'

def valid(password):
    has_upper = False
    has_lower = False
    has_number = False
    has_other = False
    for p in password:
        if p.isdecimal():
            has_number=True
        elif p.islower():
            has_lower=True
        elif p.isupper():
            has_upper=True
        else:
            has_other=True
    return has_upper, has_lower, has_number, has_other

print(valid("Amir8731"))
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Semester

@receiver(pre_save, sender=Semester)
def set_semesterID_by_year_and_semester(sender, instance, **kwargs):
    year = instance.year
    semester = instance.semester
    id = year[1:4]+str(semester)
    instance.semester_id = int(id)

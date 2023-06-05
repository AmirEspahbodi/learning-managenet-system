from datetime import timedelta, datetime

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import CourseTime, Session
from django.db.models import Q


@receiver(pre_save, sender=CourseTime)
def set_semesterID_by_year_and_semester(sender, instance, **kwargs):
    instance.semester = instance.course.semester


def create_session(course, date, time_slot):
    try:
        session = Session.objects.get(Q(date=date) & Q(time_slot=time_slot))
    except BaseException:
        session = None

    if session is None:
        session = Session(course=course, date=date, time_slot=time_slot)
        session.save()


@receiver(post_save, sender=CourseTime)
def generate_sessions_for_group_courses_by_times(sender, instance, created, **kwargs):
    if created:

        current_date = datetime.strptime(
            instance.course.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(
            instance.course.end_date, '%Y-%m-%d').date()
        time_slot = instance.time_slot

        time_slot_day = time_slot.day-1
        current_date_day = current_date.weekday()

        days_differ = 0
        if current_date_day <= time_slot_day:
            days_differ = time_slot_day - current_date_day
        else:
            days_differ = (6 - current_date_day) + time_slot_day

        current_date += timedelta(days=days_differ)
        create_session(instance.course, current_date, time_slot)

        while current_date <= end_date:
            current_date += timedelta(days=7)
            create_session(instance.course, current_date, time_slot)

        # تنظیم شماره کلاس های درس
        this_group_course_sessions = Session.objects.filter(
            course=instance.course)
        this_group_course_sessions.order_by('-date', '-time_slot__start')
        for session in this_group_course_sessions:
            count = this_group_course_sessions.filter(
                Q(date__lt=session.date) | Q(Q(date=session.date) &
                                             Q(time_slot__start__lt=session.time_slot.start))
            ).count()
            session.session_number = count
            session.save()

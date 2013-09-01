from hab.models import *
from celery import task

@task()
def update_assignments():
    for t in AssignmentTemplate.objects.filter(abstract=False):
        days_left = t.days_left()
        if not days_left is None and days_left <= 0:
            new, ass = t.instanciate()
            print "Time for another '{}'!".format(str(t))

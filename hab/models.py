# coding=utf-8
import random
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from datetime import timedelta

"""
    "Buy cabbage" -> verb: "buy", subject: "cabbage", format: "{verb} {subject}"
    "Handla kålhuvud" -> verb: "handla", subject: "kålhuvud", format: "{verb} {subject}""
"""

class AssignmentView(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, editable=False)
    template = models.OneToOneField('AssignmentTemplate', related_name='+')

    def __unicode__(self):
        return u'View: {}'.format(self.name)

    def save(self, *a, **kw):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(AssignmentView, self).save(*a, **kw)


class Verb(models.Model):
    name = models.CharField(max_length=50)
    template = models.CharField(max_length=50, blank=True, help_text="Defaults to \"{verb} {subject}\"")

    def format(self, verb, subject):
        return (self.template or u"{verb} {subject}").format(verb=verb, subject=subject)

    def __unicode__(self):
        return self.format(self.name, '<subject>')

IMPORTANCE = [(x, str(x)) for x in range(0,4)]

class Assignment(models.Model):
    verb = models.ForeignKey(Verb, related_name="assignments")
    subject = models.CharField(max_length=50, blank=True)

    owner = models.ForeignKey(User, related_name="assignments_own", null=True, blank=True)
    assignee = models.ForeignKey(User, blank=True, null=True, related_name="assignments_assigned")

    importance = models.IntegerField(choices=IMPORTANCE, default=1)

    completed = models.DateTimeField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    cleared = models.BooleanField(default=False, editable=False)

    template = models.ForeignKey('AssignmentTemplate', on_delete=models.SET_NULL, blank=True, null=True, related_name='assignments')

    def __unicode__(self):
        return u"{}".format(self.verb.format(self.verb.name, self.subject))

    def get_absolute_url(self):
        return reverse('get-assignment', args=[str(self.id)])

    def countdown(self):
        if self.deadline:
            now = timezone.now()
            then = self.deadline
            diff = (then - now)
            days = diff.total_seconds()/(60*60*24)
            return int(round(days))
        else:
            return None

    def complete(self, request=None):
        if request:
            user = request.user
        else:
            user = self.owner
        self.assignee = user
        self.completed = timezone.now()
        self.save()
        if self.template:
            self.template.update()


class AssignmentTemplate(models.Model):
    verb = models.ForeignKey(Verb, related_name="+")
    subject = models.CharField(max_length=50, blank=True)
    owners = models.ManyToManyField(User, related_name="+")
    importance = models.IntegerField(verbose_name='default importance', choices=((0, '0'), (1, '1'), (2, '2'), (3, '3')), default=1)
    delay = models.IntegerField(verbose_name='days to delay creating a new event', blank=True, null=True)
    deadline = models.IntegerField(verbose_name='days to deadline', blank=True, null=True)
    single = models.BooleanField(default=True, help_text='Do not make a new instance as long as there are uncompleted assignments based on this template already')
    abstract = models.BooleanField(default=False)

    def __unicode__(self):
        return u"{}Template: {}".format('Abstract ' if self.abstract else '', self.verb.format(self.verb.name, self.subject))

    def get_absolute_url(self):
        return reverse('get-template', args=[str(self.id)])

    def pick_owner(self):
        owners = [o['id'] for o in self.owners.values('id')]
        prototasks = [t['assignee'] for t in self.assignments.filter(completed__isnull=False).order_by('-completed').values('assignee')]
        tasks = []
        for t in prototasks:
            if not t in tasks:
                tasks.append(t)
        print "{} potential owners".format(len(owners))
        last = owners[random.randint(0, len(owners)-1)]
        owners.remove(last)
        print "Pick one at random and remove from list; {}".format(last)
        if tasks:
            print "This task has been completed a few times"
            for o in tasks:
                print "{} completed this task".format(o)
                if o in owners:
                    print "  ... and hasn't been removed from the list yet"
                    last = o
                    owners.remove(o)
                if not owners:
                    print "No more owners, the last one has to be the right one"
                    break
            else:
                print "Didn't exaust the owners list"
                last = owners[random.randint(0, len(owners)-1)]
        return User.objects.get(id=last)
        return self.owners.all()[0] if self.owners.all()[0:] else User.objects.all()[0]

    def update(self):
        if not self.delay or (not self.days_left() is None and self.days_left() <= 0):
            self.instanciate()
            return True
        else:
            return False

    def active(self):
        return not self.abstract and self.single and self.assignments.filter(completed__isnull=True).exists()

    def days_left(self):
        if not self.deadline or self.active():
            return None
        completed = self.assignments.filter(completed__isnull=False, deadline__isnull=False)
        if completed.exists():
            last = completed.latest('completed')
            then = last.completed + timedelta(days=self.delay)
            now = timezone.now()
            diff = (then - now)
            return int(round(diff.total_seconds()/(24*60*60)))
        else:
            return 0

    def instanciate(self, assign=True):
        if self.abstract:
            return (False, None)
        if self.active():
            return (False, self.assignments.all()[0])
        ass = Assignment.objects.create(
                verb=self.verb,
                subject=self.subject,
                owner=self.pick_owner(),
                importance=self.importance,
                deadline=(timezone.now() + timedelta(days=self.deadline)) if self.deadline else None,
                template=self)
        if assign:
            ass.assignee = ass.owner
        return (True, ass)

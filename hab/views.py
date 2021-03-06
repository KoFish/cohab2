import re
from datetime import timedelta
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils import simplejson as json
from django.http import HttpResponse, Http404
from django.contrib import messages
from hab.forms import CreateAssignmentForm, CreateViewAssignmentForm
from hab.models import *
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.serializers import json as json_serializer, serialize
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy as __

def make_status(status, **kw):
    d = {'status': status}
    d.update(dict((k,v) for k,v in kw.iteritems() if v is not None))
    return d

make_failure = lambda msg, **kw: make_status('failed', message=msg, **kw)
make_success = lambda **kw: make_status('success', **kw)

class JsonResponse(HttpResponse):
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = json.dumps(object, indent=2, cls=json_serializer.DjangoJSONEncoder, ensure_ascii=False)
        super(JsonResponse, self).__init__(
            content, content_type='application/json')

class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, *a, **kw):
        return login_required(super(LoginRequiredMixin, cls).as_view(*a, **kw))

def ajax_object_action(model):
    def outer(f):
        def inner(request, pk, *a, **kw):
            if request.method == 'POST' or request.is_ajax() or 'ajax' in request.GET:
                try:
                    obj = model.objects.get(pk=pk)
                except model.DoesNotExist:
                    return JsonResponse(make_failure(_('No {name} with that id ({pk})').format(name=__(str(model.__name__)), pk=pk)))
                else:
                    return f(request, obj, *a, **kw)
            else:
                raise Http404(_('This action is not available by GET'))
        return inner
    return outer

class RootView(RedirectView):
    permanent = True

    def get_redirect_url(self):
        return reverse('assignments-list')

def get(request, key):
    if not (request.is_ajax() or 'ajax' in request.GET):
        raise Http404(_('This url has no meaning unless fetched by ajax'))

    def get_messages(request):
        msgs = []
        for message in messages.get_messages(request):
            msgs.append({
                "level": message.level,
                "message": message.message,
                "extra_tags": message.tags,
                })
        return {'messages': msgs}

    def get_verbs(request):
        q = request.GET.get('q')
        nocount = 'nocount' in request.GET
        query = Verb.objects
        if q:
            query = query.filter(name__contains=q)
        if not nocount:
            query = query.extra(select={'count': 'SELECT COUNT(*) FROM hab_assignment WHERE hab_assignment.verb_id = hab_verb.id AND hab_assignment.completed IS NULL'})
            return {'verbs': list(set([(v.name, v.count) for v in query.all()]))}
        else:
            return {'verbs': list(set([v.name for v in query.all()]))}

    def get_subjects(request):
        asubjects = [a['subject'] for a in Assignment.objects.values('subject').all()]
        tsubjects = [a['subject'] for a in AssignmentTemplate.objects.values('subject').all()]
        return {'subjects': filter(bool, list(set(asubjects + tsubjects)))}

    cmds = {'messages': get_messages,
            'verbs': get_verbs,
            'subjects': get_subjects}
    if key in cmds:
        res = cmds[key](request)
        return JsonResponse(make_success(**res))
    else:
        return JsonResponse(make_failure(_('No such value.')))


@csrf_exempt
@login_required
@ajax_object_action(Assignment)
def complete_assignment(request, obj):
    obj.complete(request)
    messages.info(request, _('Completed assignment {}').format(obj))
    return JsonResponse(make_success())


@csrf_exempt
@login_required
@ajax_object_action(Assignment)
def clear_assignment(request, obj):
    obj.cleared = True
    obj.save()
    return JsonResponse(make_success())


@csrf_exempt
@login_required
@ajax_object_action(Assignment)
def reopen_assignment(request, obj):
    if obj.cleared:
        return JsonResponse(make_failure(_('Not allowed to reopen cleared task')))
    else:
        obj.completed = None
        obj.save()
        return JsonResponse(make_success())



@csrf_exempt
@login_required
@ajax_object_action(Assignment)
def assign_assignment(request, obj):
    try:
        username = request.GET.get('to', None)
        if username:
            user = User.objects.get(username=username)
        else:
            user = None
    except User.DoesNotExist:
        messages.danger(request, _("Could not assign task to {}, no such user exists.").format(username));
        return JsonResponse(make_failure("No user named {}".format(username)))
    else:
        obj.assignee = user
        obj.save()
        return JsonResponse(make_success())


@csrf_exempt
@login_required
@ajax_object_action(Assignment)
def suspend_assignment(request, obj):
    try:
        days = int(request.GET.get('days', '0'))
        if obj.deadline and days and days > 0:
            obj.deadline = obj.deadline + timedelta(days=days)
            obj.save()
        print obj
        return JsonResponse(make_success(deadline=obj.deadline.strftime('%c'), days_left="{} days left".format(obj.countdown())));
    except ValueError:
        return JsonResponse(make_failure(_('{} is not an integer').format(request.GET.get('days'))))


@csrf_exempt
@login_required
@ajax_object_action(AssignmentTemplate)
def instanciate_template(request, obj):
    obj.instanciate()
    return JsonResponse(make_success())


@csrf_exempt
@login_required
@ajax_object_action(AssignmentTemplate)
def remove_template(request, obj):
    obj.delete()
    return JsonResponse(make_success())

class HabMixin(object):
    def get_context_data(self, *a, **kw):
        cx = super(HabMixin, self).get_context_data(*a, **kw)
        cx['views'] = AssignmentView.objects.all()
        cx['now'] = timezone.now()
        return cx

class AssignmentViewList(HabMixin, DetailView):
    model = AssignmentView

    def get_context_data(self, *a, **kw):
        cx = super(AssignmentViewList, self).get_context_data(*a, **kw)
        q = Assignment.objects.filter(template=self.get_object().template)
        q = q.extra(select={
                'deadline_is_null': 'deadline IS NULL',
                'i_own': 'owner_id = \''+str(self.request.user.id)+'\'',
                'mine': 'assignee_id = \''+str(self.request.user.id)+'\'',
            },
            order_by=['-mine', '-i_own', 'deadline_is_null', 'deadline', 'importance'])
        q = q.filter(cleared=False)
        q = q.filter(Q(assignee__isnull=True)|Q(assignee=self.request.user))
        cx['assignments'] = q.all()
        cx['slug'] = self.kwargs['slug']
        cx['users'] = User.objects.all()
        return cx


class AssignmentsList(LoginRequiredMixin, HabMixin, ListView):
    model = Assignment

    def get_queryset(self, *a, **kw):
        sort_order = ['-mine', '-i_own', '-importance', 'deadline_is_null', 'deadline']
        if self.request.GET.get('sort', 'importance') == 'deadline':
            sort_order = ['-mine', '-i_own', 'deadline_is_null', 'deadline']
        q = super(AssignmentsList, self).get_queryset(*a, **kw).filter(cleared=False)
        q = q.extra(select={
                'deadline_is_null': 'deadline IS NULL',
                'i_own': 'owner_id = \''+str(self.request.user.id)+'\'',
                'mine': 'assignee_id = \''+str(self.request.user.id)+'\'',
            },
            order_by=sort_order)
        limit = self.request.GET.get('q')
        owner = self.request.GET.get('owner')
        if owner:
            q = q.filter(owner__username=owner)
        if limit:
            q = q.filter(Q(verb__name__contains=limit) | Q(subject__contains=limit))
        return q

    def get_context_data(self, *a, **kw):
        cx = super(AssignmentsList, self).get_context_data(*a, **kw)
        verbs = Verb.objects.extra(select={'count': 'SELECT COUNT(*) FROM hab_assignment WHERE hab_assignment.verb_id = hab_verb.id AND hab_assignment.completed IS NULL'})
        cx['verbs'] = verbs.all()
        cx['users'] = User.objects.all()
        return cx


class AssignmentTemplatesList(LoginRequiredMixin, HabMixin, ListView):
    model = AssignmentTemplate

    def get_queryset(self, *a, **kw):
        q = super(AssignmentTemplatesList, self).get_queryset(*a, **kw).filter(abstract=False)
        limit = self.request.GET.get('q')
        if limit:
            q = q.filter(verb__name__contains=limit)
        return q


class UserList(LoginRequiredMixin, HabMixin, ListView):
    model = User
    template_name = 'hab/user_list.html'


class TemplateDetails(DetailView):
    model = AssignmentTemplate


class AssignmentDetails(DetailView):
    model = Assignment


def parse_deadline(deadline):
    days = 0
    dm = re.search(r'(\d+)\s*(?:d|days)', deadline)
    if dm:
        days = dm.group(1)
    if not dm and days == 0:
        m = re.search(r'(\d+)', deadline)
        if m:
            days = int(m.group(1))
    return timedelta(days=int(days))


class LoggedInAjaxRequiredMixin(object):
    def dispatch(self, request, *a, **kw):
        if request.is_ajax() or 'ajax' in request.GET:
            if request.user.is_authenticated():
                return super(LoggedInAjaxRequiredMixin, self).dispatch(request, *a, **kw)
            else:
                return JsonResponse(make_failure(_('You have to be logged in.')))
        raise Http404(_("You aren't allowed to fetch this without ajax."))


class CreateAssignmentView(LoggedInAjaxRequiredMixin, FormView):
    template_name = 'hab/create_assignment_form.html'
    form_class = CreateAssignmentForm

    def get_context_data(self, **kwargs):
        cx = super(CreateAssignmentView, self).get_context_data(**kwargs)
        cx['users'] = User.objects.all()
        return cx

    def form_valid(self, form):
        data = form.cleaned_data
        verb, new_verb = Verb.objects.get_or_create(name=unicode(data['verb']).lower())
        subject = data['subject'].lower()
        if data['deadline']:
            deadline = timezone.now() + parse_deadline(data['deadline']) 
        else:
            deadline = None
        if data.get('repeat', False):
            template = AssignmentTemplate(
                verb=verb,
                subject=subject,
                importance=data['importance'],
                delay=parse_deadline(data['repeat_delay']).days,
                deadline=parse_deadline(data['deadline']).days,
                single=True)
            template.save()
            for owner in data['allowed_owners']:
                template.owners.add(owner)
        else:
            template = None
        ass = Assignment(
            verb=verb,
            subject=subject,
            owner=User.objects.get(username=data['owner']) if data['owner'] else None,
            importance=data['importance'],
            deadline=deadline,
            template=template)
        if data.get('mine', False):
            ass.assignee = self.request.user
        ass.save()
        return JsonResponse(make_success())

    def form_invalid(self, form):
        return JsonResponse(make_failure(_('Errors in form'), errors=form.errors))

    def get_success_url(self):
        return reverse('assignments-list')

class CreateViewAssignmentView(LoggedInAjaxRequiredMixin, FormView):
    template_name = 'hab/create_view_assignment_form.html'
    form_class = CreateViewAssignmentForm

    def get_context_data(self, **kwargs):
        slug = self.kwargs.get('slug')
        cx = super(CreateViewAssignmentView, self).get_context_data(**kwargs)
        cx['users'] = User.objects.all()
        cx['view'] = AssignmentView.objects.get(slug=slug)
        cx['slug'] = slug
        return cx

    def form_valid(self, form):
        view = AssignmentView.objects.get(slug=self.kwargs.get('slug'))
        data = form.cleaned_data
        verb = view.template.verb
        if data['deadline']:
            deadline = timezone.now() + parse_deadline(data['deadline']) 
        else:
            deadline = None
        ass = Assignment(
            verb=verb,
            subject=data['subject'].lower(),
            owner=self.request.user,
            importance=data['importance'],
            deadline=deadline,
            template=view.template)
        if data.get('mine', False):
            ass.assignee = self.request.user
        ass.save()
        return JsonResponse(make_success())

    def form_invalid(self, form):
        return JsonResponse(make_failure(_('Errors in form'), errors=form.errors))

    def get_success_url(self):
        return reverse('assignments-list')

from django import template

register = template.Library()

@register.simple_tag(takes_context = True)
def query_replace(context, field, value):
    dict_ = context['request'].GET.copy()
    dict_[field] = value
    return dict_.urlencode()
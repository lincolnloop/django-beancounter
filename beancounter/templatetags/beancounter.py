from django import template
import calendar

register = template.Library()

@register.filter
def timestamp(date_object):
    return calendar.timegm(date_object.timetuple()) * 1000
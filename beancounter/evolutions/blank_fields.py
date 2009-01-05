#----- Evolution for beancounter
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    ChangeField('Project', 'bid', initial=None, null=True),
    ChangeField('Employee', 'gmt_offset', initial=None, null=True)
]
#----------------------

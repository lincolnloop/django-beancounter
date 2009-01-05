#----- Evolution for beancounter
from django_evolution.mutations import *
from django.db import models

MUTATIONS = [
    AddField('Project', 'bid', models.DecimalField, initial=0.00, max_digits=8, decimal_places=2)
]
#----------------------

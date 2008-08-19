import datetime

from django import newforms as forms

from models import Entry

MONTH_CHOICES = (
    (0, 'All'),
    (1, 'Jan'),
    (2, 'Feb'),
    (3, 'Mar'),
    (4, 'Apr'),
    (5, 'May'),
    (6, 'Jun'),
    (7, 'Jul'),
    (8, 'Aug'),
    (9, 'Sep'),
    (10, 'Oct'),
    (11, 'Nov'),
    (12, 'Dec'), 
)

this_year = datetime.date.today().year
try:
    first_year = Entry.objects.all().order_by('date')[0].date.year
except KeyError:
    first_year = this_year
YEAR_CHOICES = []
for year in range(first_year, this_year+1):
    YEAR_CHOICES.append((year, year))
    
class DateForm(forms.Form):
    month = forms.ChoiceField(choices=MONTH_CHOICES)
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    
    def clean(self):
        if self.cleaned_data.has_key('year'):
            self.cleaned_data['year'] = int(self.cleaned_data['year'])
        if self.cleaned_data.has_key('month'):
            self.cleaned_data['month'] = int(self.cleaned_data['month'])
        return self.cleaned_data
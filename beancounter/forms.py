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
    
    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs) 
        today = datetime.date.today()
        self.fields['month'].initial = str(today.month)
        self.fields['year'].initial = str(today.year)
        
    
    def start_end_date(self, month, year):
        """
        Return datetime objects for the start and end of the month. 
        If month is 0 return start and end of year
        """
        year_start = year
        year_end = year
        if month == 0: #full year
            month_start = 1
            end = datetime.date(year_end, 12, 31)
        else: #1 month
            month_start = month
            if month == 12:
                month_end = 1
                year_end = year + 1
            else:
                month_end = month + 1
            end = datetime.date(year_end, month_end, 1)
        start = datetime.date(year_start, month_start, 1)
        return start,end
    
    def get_date_range(self):
        if self.is_valid():
            month = self.cleaned_data['month']
            year = self.cleaned_data['year']
        else:
            today = datetime.date.today()
            month = today.month
            year = today.year
            self = DateForm({'month':month, 'year':year})
        return self.start_end_date(int(month), int(year))


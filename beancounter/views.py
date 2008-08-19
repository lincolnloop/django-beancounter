import datetime
import decimal
from operator import itemgetter

from django.template import Context, loader, RequestContext
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic import simple
from django.utils.datastructures import SortedDict
from django.contrib.auth.decorators import login_required

from models import *
from forms import DateForm
    
def htmlDates(theMonth,theYear):
    return ''
    
def build_dates(month, year):
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
    
def detail_for_type(month,year,cat_type):
    """Get list of each category total for a given category type."""
    categories = Category.objects.filter(type__exact=cat_type)
    report_start,report_end = build_dates(month,year)
    entries = Entry.objects.filter(
                    date__gte=report_start, 
                    date__lt=report_end, 
                    category__type=cat_type).order_by('category')
    category_dict = {}
    type_total = decimal.Decimal('0')
    if entries:
        for e in entries:
            if category_dict.has_key(e.category.name):
                category_dict[e.category.name] += e.amount
            else:
                category_dict[e.category.name] = e.amount
            type_total += e.amount
    
    #Sort dictonary by values
    #Python voodoo courtesy of http://www.python.org/dev/peps/pep-0265/   
    category_list = sorted(category_dict.iteritems(), key=itemgetter(1), reverse=True)
    return category_list,type_total
    

    
@login_required
def overview(request):
    form = DateForm(request.GET)
    if form.is_valid():
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
    else:
        today = datetime.date.today()
        month = today.month
        year = today.year
    
    income_list,income = detail_for_type(month, year,"INC")
    cogs_list,cogs = detail_for_type(month, year,"COGS")
    expense_list,expense = detail_for_type(month, year,"EXP")
    
    cogs_plus_expense = cogs + expense
    net = income - cogs_plus_expense
    return simple.direct_to_template(request,
                                     template='beancounter/overview.html',
                                     extra_context = { 
                                        'form': form,
                                        'income_list': income_list,
                                        'income': income,
                                        'cogs_list': cogs_list,
                                        'cogs': cogs,
                                        'expense_list': expense_list,
                                        'expense': expense,
                                        'cogs_plus_expense': cogs_plus_expense,
                                        'net': net, 
                                    })

@login_required
def history(request):
    """
    Tally total expenses and income for each month
    """
    history = SortedDict()
    entries = Entry.objects.all().order_by('-date')
    for e in entries:
        
        # Create dict key
        this_month = datetime.date(e.date.year, e.date.month, 1)
        if not history.has_key(this_month):
            history[this_month] = {'income':0, 'expense':0}
            
        #sum values for month
        if e.category.type in ['EXP', 'COGS']:
            history[this_month]['expense'] += e.amount
        elif e.category.type == 'INC':
             history[this_month]['income'] += e.amount

    
    for date, value_dict in history.items():
        value_dict['net'] = value_dict['income'] - value_dict['expense']

    return simple.direct_to_template(request,
                                     template='beancounter/history.html',
                                     extra_context = { 'history': history })
        
@login_required
def income_vs_cost(request):
    try:
        theMonth = int(request.GET['month'])
        theYear = int(request.GET['year'])
    except (KeyError):
        theMonth = datetime.date.today().month
        theYear = datetime.date.today().year
    
    (monthOptions,yearOptions) = htmlDates(theMonth,theYear)
    (report_start,report_end) = buildDates(theMonth,theYear)
    cogsCats = Category.objects.filter(type__exact='COGS')
    total = 0.00
    linkNumber = 0
    Totals = []
    cTotals = []
    iTotals = []
    iCats = []
    cogsLabels = ""


    for c in cogsCats:
        cogsEntries = Entry.objects.filter(date__gte = report_start) & Entry.objects.filter(date__lt = report_end) &  Entry.objects.filter(category__id=c.id)
        cSum = 0.00
        #total for COGS category
        for e in cogsEntries:
            cSum = cSum + float(e.amount)
        cTotals += [cSum]
        iSum = 0.00
        incomeEntries = Entry.objects.filter(date__gte = report_start) & Entry.objects.filter(date__lt = report_end) &  Entry.objects.filter(category__id=c.income.id)
        #total for associated Income category
        iCats += [c.income]
        for i in incomeEntries:
            iSum = iSum + float(i.amount)
        iTotals += [iSum]
        Totals += [iSum-cSum]
        linkNumber = linkNumber +1
    lN = range(7)
    
    cogsList = zip(lN,iCats,iTotals,cTotals,Totals)
    sortby(cogsList,4)
    h = 0
    for i in cogsList:
        cogsLabels += '{label: "' + i[1].name + '", v: ' + str(i[0]) + '}, '
    cogsLabels = cogsLabels.rstrip(', ')
    
    return render_to_response('beancounter/incomevscost.html',locals(),context_instance=RequestContext(request))
                
@login_required
def moneyin_moneyout(request):
    try:
        theMonth = int(request.GET['month'])
        theYear = int(request.GET['year'])
    except (KeyError):
        theMonth = datetime.date.today().month
        theYear = datetime.date.today().year
    
    (monthOptions,yearOptions) = htmlDates(theMonth,theYear)
    (report_start,report_end) = build_dates(theMonth,theYear)
    
    peeps = Person.objects.filter()
    ipeepsList = []
    incomeList = []
    epeepsList = []
    expenseList = []
    iLabels = ""
    eLabels = ""
    for p in peeps:
        iSum = 0.00
        incomeEntries = Entry.objects.filter(date__gte = report_start) & Entry.objects.filter(date__lt = report_end) & Entry.objects.filter(category__type = 'INC') & Entry.objects.filter(name = p)
        for i in incomeEntries:
            iSum = iSum + float(i.amount)
        if iSum > 0:
            iLabels += '{label: "' + p.name + '", v: ' + str(p.id) + '}, '
            ipeepsList += [p]
            incomeList += [iSum]
            
        eSum = 0.00
        expenseEntries = Entry.objects.filter(date__gte = report_start) & Entry.objects.filter(date__lt = report_end) & Entry.objects.filter(Q(category__type = 'EXP') | Q(category__type = 'COGS')) & Entry.objects.filter(name = p)
        for e in expenseEntries:
            eSum = eSum + float(e.amount)
        if eSum > 0:
            eLabels += '{label: "' + p.name + '", v: ' + str(p.id) + '}, '
            epeepsList += [p]
            expenseList += [eSum]
        
        
    incomeMash = zip(ipeepsList,incomeList)
    sortby(incomeMash,1)
    expenseMash  = zip(epeepsList,expenseList)
    sortby(expenseMash,1)
    return render_to_response('beancounter/moneyin-moneyout.html',locals(),context_instance=RequestContext(request))

@login_required
def balance(request):
    """Track account balances over time."""
    #
    #Not fully implemented yet. 
    #Also needs different graphing library as Plotkit can't do negative numbers.
    #
    accounts = BankAccount.objects.filter(track_balance__exact=True)
    tally_labels = []
    tally = []

    this_id = -1
    this_account = 0
    for a in accounts:
        this_tally = []
        this_tally_labels = ""
        entries = Entry.objects.filter(bank_account__exact=a).order_by('date')
        transfers = AccountTransfer.objects.filter(bank_account__exact=a).order_by('date')
        total = a.initial_balance
        n = 0
        start = True
        for e in entries:
            if start:
                this_date = e.date
                start = False
            if this_date != e.date:
                this_tally.append([n,this_date,total])
                this_date = e.date
                this_tally_labels += '{label: "' + str(e.date) + '", v: ' + str(n) + '}, '
                n = n+1
            if e.category.type == 'COGS' or e.category.type == 'EXP':
                amount = -e.amount
            else:
                amount = e.amount
            total = total + amount
        this_tally.append([n,this_date,total])
        tally += [this_tally]
        this_date = e.date
        this_tally_labels += '{label: "' + str(e.date) + '", v: ' + str(n) + '}'
        tally_labels += [this_tally_labels]

    title = 'Account Balances'
    return render_to_response('beancounter/account-balances.html',locals(),context_instance=RequestContext(request))            

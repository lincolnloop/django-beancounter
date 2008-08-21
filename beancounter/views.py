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

    
def detail_for_type(start, end, cat_type):
    """Get list of each category total for a given category type."""
    
    entries = Entry.objects.filter(
                    date__gte=start, 
                    date__lt=end, 
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
    if request.GET.has_key('month') and request.GET.has_key('year'):
        form = DateForm(request.GET)
    else:
        form = DateForm()
    start, end = form.get_date_range()
    
    income_list,income = detail_for_type(start, end,"INC")
    cogs_list,cogs = detail_for_type(start, end,"COGS")
    expense_list,expense = detail_for_type(start, end,"EXP")
    
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
    """
    Return a list of dictionaries containing COGS and related INC spending
    for the report time specified.
    
    """
    if request.GET.has_key('month') and request.GET.has_key('year'):
        form = DateForm(request.GET)
    else:
        form = DateForm()
    start, end = form.get_date_range()
    
    
    cogs_categories = Category.objects.filter(type__exact='COGS')
    totals = []
    for cat in cogs_categories:
        if cat.income: #this should be in the query
            cogs_entries = Entry.objects.filter(date__gte=start,
                                               date__lt=end,
                                               category=cat)
            cogs_total = decimal.Decimal('0')
            #total for COGS category
            for e in cogs_entries:
                cogs_total += e.amount

        
            income_total = decimal.Decimal('0')
            income_entries = Entry.objects.filter(date__gte=start,
                                                 date__lt=end,
                                                 category=cat.income)
            #total for associated Income category
            for i in income_entries:
                income_total += i.amount
        
            totals.append({
                'cogs_category': cat.name,
                'cogs_total': cogs_total,
                'income_category': cat.income,
                'income_total': income_total,
                'balance': income_total - cogs_total,
            })
    
    return simple.direct_to_template(request,
                                     template='beancounter/incomevscost.html',
                                     extra_context={
                                        'form':form,
                                        'totals': totals,
                                    })
                
@login_required
def moneyin_moneyout(request):
    """
    Return a list of dictionaries containing COGS and related INC spending
    for the report time specified.
    
    """
    if request.GET.has_key('month') and request.GET.has_key('year'):
        form = DateForm(request.GET)
    else:
        form = DateForm()
    start, end = form.get_date_range()
    
    entries = Entry.objects.filter(date__gte=start,
                                   date__lt=end)
             
    income_dict = {}
    expense_dict = {}                     
    for e in entries:
        if e.category in ['EXP', 'COGS']:
            if expense_dict.has_key(e.name.name):
                expense_dict[e.name.name] += e.amount
            else:
                expense_dict[e.name.name] = e.amount
        elif e.category == 'INC':
            if income_dict.has_key(e.name.name):
                income_dict[e.name.name] += e.amount
            else:
                income_dict[e.name.name] = e.amount
            
    return simple.direct_to_template(request,
                                     template='beancounter/moneyin-moneyout.html',
                                     extra_context={
                                        'form':form,
                                        'income': income_dict,
                                        'expense': expense_dict,
                                    })

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

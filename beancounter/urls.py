from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^overview/$', 'beancounter.views.overview'),
    (r'^history/$', 'beancounter.views.history'),
    (r'^income-vs-cost/$', 'beancounter.views.incomeVsCost'),
    (r'^moneyin-moneyout/$', 'beancounter.views.moneyInMoneyOut'),
    (r'^account-balances/$', 'beancounter.views.balance'),
)

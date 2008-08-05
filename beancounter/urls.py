from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^overview/$', 'beancounter.views.overview', name="beancounter_overview"),
    url(r'^history/$', 'beancounter.views.history', name="beancounter_history"),
    url(r'^income-vs-cost/$', 'beancounter.views.income_vs_cost', name="beancounter_income_cost"),
    url(r'^moneyin-moneyout/$', 'beancounter.views.moneyin_moneyout', name="beancounter_inout"),
    url(r'^account-balances/$', 'beancounter.views.balance', name="beancounter_balances"),
)

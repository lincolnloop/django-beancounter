from beancounter.models import Category, BankAccount, AccountTransfer, Person, Entry
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

class CategoryOptions(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('type','name')
        }),
        ('Associate Costs of Goods Sold to an Income Category', {
            'classes': ('collapse',),
            'fields' : ('income',)
        }),
    )

class BankAccountOptions(admin.ModelAdmin):
    list_display = ('name','type')
    ordering = ['-track_balance','name','type']

class PersonOptions(admin.ModelAdmin):
    list_display = ('name','phone','email')

class AccountTransferOptions(admin.ModelAdmin):
    list_display = ('date','amount','from_account','to_account')
    list_filter = ('to_account','from_account')
    date_hierarchy = 'date'

class EntryOptions(admin.ModelAdmin):
    list_display = ('date', 'name', 'category', 'amount')
    date_hierarchy = 'date'
    search_fieldsets = ('name','memo')
    list_filter = ('category','name','bank_account')

admin.site.register(Category, CategoryOptions)
admin.site.register(BankAccount, BankAccountOptions)
admin.site.register(Person, PersonOptions)
admin.site.register(AccountTransfer, AccountTransferOptions)
admin.site.register(Entry, EntryOptions)


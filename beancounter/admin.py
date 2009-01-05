from django.contrib import admin

from beancounter.models import (Category, BankAccount, AccountTransfer,
                                Person, Entry, Employee, Project, ProjectTime,
                                ProjectInvoice)

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

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'gmt_offset', 'rate')
    search_fields = ('name',)

class ProjectInvoiceInline(admin.TabularInline):
    model = ProjectInvoice

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name','start_date')
    inlines = [ProjectInvoiceInline,]
    
class ProjectTimeAdmin(admin.ModelAdmin):
    list_display = ('project', 'employee', 'hours', 'cost_converted')
    list_filter = ('project', 'employee')

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
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectTime, ProjectTimeAdmin)


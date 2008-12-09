from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField

TYPE_CHOICES = (
    ('INC', 'Income'),
    ('EXP', 'Expense'),
    ('COGS', 'Cost of Goods Sold'),
)
class Category(models.Model):
    type = models.CharField(max_length=4,choices=TYPE_CHOICES)
    name = models.CharField(max_length=50)
    income = models.ForeignKey('self', null=True, blank=True, limit_choices_to = {'type__exact':'INC'}, help_text='Use this to enable tracking your costs of goods vs. income')

    def __str__(self):
        return "%s: %s" % (self.type,self.name)
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['type','name']
    
    class Admin:
        fields = (
            (None, {
                'fields': ('type','name')
            }),
            ('Associate Costs of Goods Sold to an Income Category', {
                'classes': 'collapse',
                'fields' : ('income',)
            }),
        )
    
class BankAccount(models.Model):
    type = models.CharField(max_length=50,help_text='Checking, Savings, Credit, etc.')
    name = models.CharField(max_length=50)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True,blank=True)
    track_balance = models.BooleanField(help_text='Generate reports of the balance of this account over time.')

    def __str__(self):
        return "%s (%s)" % (self.name,self.type)
    class Admin:
        list_display = ('name','type')
        ordering = ['-track_balance','name','type']
        
class AccountTransfer(models.Model):
    date = models.DateField()
    from_account = models.ForeignKey(BankAccount,related_name='transferred_from')
    to_account = models.ForeignKey(BankAccount,related_name='transferred_to')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    memo = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return "$%.2f from %s to %s" % (self.amount,self.from_account,self.to_account)
        
    class Admin:
        list_display = ('date','amount','from_account','to_account')
        list_filter = ('to_account','from_account')
        date_hierarchy = 'date'
        
        
class Person(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100,null=True,blank=True)
    phone = PhoneNumberField(null=True,blank=True)
    website = models.URLField(null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    notes = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return "%s" % (self.name)
    
    class Meta:
        verbose_name_plural = 'People'
        ordering = ['name']
        
    
    class Admin:
        list_display = ('name','phone','email')

class Entry(models.Model):
    category = models.ForeignKey(Category)
    date = models.DateField()
    name = models.ForeignKey(Person)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    bank_account = models.ForeignKey(BankAccount,related_name='paid_from',null=True,blank=True)
    memo = models.CharField(max_length=100,null=True,blank=True)
    
    def __str__(self):
        return "$%.2f | %s | %s" % (self.amount,self.name,self.date)
    class Meta:
        verbose_name_plural = 'Entries'
            
    class Admin:
        list_display = ('date', 'name', 'category', 'amount')
        date_hierarchy = 'date'
        search_fields = ('name','memo')
        list_filter = ('category','name','bank_account')

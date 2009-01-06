import datetime
import decimal

from django.db import models
from django.contrib.localflavor.us.models import PhoneNumberField
from tagging.fields import TagField

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
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'People'
        ordering = ['name']
        
        
class Employee(Person):
    PAYMENT_CHOICES = (
        ('paypal', 'PayPal'),
        ('check', 'Mail Check'),
        ('wire', 'Wire Transfer'),
        ('elance', 'Elance'),
        ('other', 'Other'),
    )
    gmt_offset = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    skills = TagField()
    payment_preference = models.CharField(blank=True, max_length=100, choices=PAYMENT_CHOICES)
    payment_notes = models.TextField(blank=True)
    contract = models.DateField(blank=True, null=True, help_text="Date contractor contract was signed and received.")
    hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="If rate varies, enter average and note below.")
    currency = models.CharField(default="USD", max_length=3)
    rate_notes = models.TextField(blank=True, help_text="Additional notes regarding contractor rates.")


    def timezone(self):
        if self.gmt_offset == int(self.gmt_offset):
            gmt_offset = int(self.gmt_offset)
        else:
            gmt_offset = self.gmt_offset
        if gmt_offset > 0:
            gmt_offset = '+%s' % gmt_offset
        return 'GMT%s' % gmt_offset

    def under_contract(self):
        if self.contract:
            return True
        return False
    under_contract.boolean = True

    def rate(self):
        return "%s %s" % (self.hourly_rate, self.currency)

class Project(models.Model):
    name = models.CharField(max_length=100)
    employees = models.ManyToManyField(Employee)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name
        
    def total_invoiced(self):
        #TODO aggregate support
        total = decimal.Decimal("0.00")
        for invoice in self.projectinvoice_set.all():
            total += invoice.amount
        return total
    
    def total_cost(self):
        #TODO aggregate support
        total = decimal.Decimal("0.00")
        for time in self.projecttime_set.all():
            total += time.cost_converted
        return total
    
    def profit(self):
        return self.total_invoiced() - self.total_cost()
            

class ProjectInvoice(models.Model):
    """
    Invoice sent for project
    
    """
    project = models.ForeignKey(Project)
    date = models.DateField(default=datetime.date.today())
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __unicode__(self):
        return "$%s for %s on %s" % (self.amount, self.project, self.date)
        
        
class ProjectTime(models.Model):
    """
    Hours spent by an employee on a project
    
    """
    
    employee = models.ForeignKey(Employee)
    project = models.ForeignKey(Project)
    start_date = models.DateField(default=datetime.date.today())
    end_date = models.DateField(default=datetime.date.today())
    hours = models.DecimalField(max_digits=6, decimal_places=3)
    cost = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, help_text="Leave blank to automatically calculate")
    cost_converted = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, help_text="Cost converted to local currency")

    def __unicode__(self):
        return "%s on %s (%s-%s)" % (self.employee, self.project, self.start_date, self.end_date)
    
    def save(self, force_insert=False, force_update=False):
        if not self.cost:
            self.cost = self.hours * self.employee.hourly_rate
        if not self.cost_converted and self.employee.currency == "USD":
            self.cost_converted = self.cost
        super(ProjectTime, self).save(force_insert, force_update)


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

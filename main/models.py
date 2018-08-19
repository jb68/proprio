# vim: ai ts=4 sts=4 et sw=4
from django.db import models
from django.db.models import Max
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, \
                                   ValidationError
from datetime import date
from calendar import monthrange
from collections import namedtuple, deque
import itertools
from operator import attrgetter
from django.forms import Textarea
from decimal import Decimal
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Building(models.Model):
    name = models.CharField(_("name"), max_length=255)
    notes = models.TextField(_("notes"), blank=True)

    def main_thm(self):
        """
          Returns the main picture thumb
        """
        entry = BuildingPhoto.objects.filter(building=self.id).first()
        if entry:
            return u'<a href="%s" target="blank" /><img src="%s" /></a>' % \
                (entry.image.url, entry.image_thumbnail.url)
        else:
            return '(No image found)'
    main_thm.short_description = 'Main Building Photo'
    main_thm.allow_tags = True

    class Meta:
        verbose_name = _("building")
        verbose_name_plural = _("buildings")
        ordering = ['name']

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name

    def property_count(self):
        return self.property_set.count()

    property_count.short_description = _("number of properties")


class BuildingFile(models.Model):
    building = models.ForeignKey(
        Building, verbose_name=Building._meta.verbose_name)
    name = models.CharField(_("name"), max_length=255)
    file = models.FileField(_('file'), upload_to='building')

    class Meta:
        verbose_name = _("file")

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name


class BuildingPhoto(models.Model):
    building = models.ForeignKey(
        Building, verbose_name=Building._meta.verbose_name)
    image = models.ImageField(_('image'), upload_to='building')
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFill(200, 100)],
                                      format='JPEG',
                                      options={'quality': 60})

    class Meta:
        verbose_name = _("building image")
    def __unicode__(self):
        return ''
    def __str__(self):
        return ''

    def image_thm(self):
        if self.image_thumbnail:
            return u'<a href="%s" target="blank" /><img src="%s" /></a>' % \
                (self.image.url, self.image_thumbnail.url)
        else:
            return '(No image found)'
    image_thm.short_description = 'Thumb'
    image_thm.allow_tags = True

class PropertyType(models.Model):
    name = models.CharField(_("name"), max_length=32)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("property type")
        verbose_name_plural = _("property types")
        ordering = ['name']

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name

#   def room_count(self):
#        return self.room_set.count()

#    room_count.short_description = _("number of rooms")


class Room(models.Model):
     propertytype = models.ForeignKey(
         PropertyType, verbose_name=PropertyType._meta.verbose_name)
     name = models.CharField(_("name"), max_length=32)

     def __unicode__(self):
         return self.name
     def __str__(self):
         return self.name


class Property(models.Model):
    building = models.ForeignKey(Building,
        verbose_name=Building._meta.verbose_name,
        blank=True, null=True, on_delete=models.PROTECT)
    # main_photo = models.ForeignKey('PropertyPhoto',
    #         verbose_name='Main Photo', related_name='property_main_photo',
    #         blank=True, null=True,on_delete=models.PROTECT)
    property_type = models.ForeignKey(PropertyType,
        verbose_name=PropertyType._meta.verbose_name,
        blank=True, null=True, on_delete=models.PROTECT)
    name = models.CharField(_("name"), max_length=255)
    address = models.TextField(_("address"))
    notes = models.TextField(_("notes"), blank=True)
    area = models.DecimalField(
        _("surface area"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)])

    floorplan = models.ImageField(_('floorplan'),
                                  upload_to='property',
                                  null=True,
                                  blank=True)
    plan_thumbnail = ImageSpecField(source='floorplan',
                                      processors=[ResizeToFill(200, 100)],
                                      format='JPEG',
                                      options={'quality': 60})
    reservefund = models.SmallIntegerField(
        _('percentage into reserve fund'), default=10)
    def plan_thm(self):
        if self.plan_thumbnail:
            return u'<a href="%s" target="blank" /><img src="%s" /></a>' % \
                (self.floorplan.url, self.plan_thumbnail.url)
        else:
            return '(No image found)'
    plan_thm.short_description = 'Floorplan'
    plan_thm.allow_tags = True

    def main_thm(self):
        """
          Returns the main picture thumb
        """
        entry = PropertyPhoto.objects.filter(property=self.id).first()
        if entry:
            return u'<a href="%s" target="blank" /><img src="%s" /></a>' % \
                (entry.image.url, entry.image_thumbnail.url)
        else:
            return '(No image found)'
    main_thm.short_description = 'Main Property Photo'
    main_thm.allow_tags = True

    class Meta:
        verbose_name = _("property")
        verbose_name_plural = _("properties")
        ordering = ['name']

    def __unicode__(self):
        return u'{}\n{}'.format(self.name, self.address)
    def __str__(self):
        return u'{}\n{}'.format(self.name, self.address)




class PropertyPhoto(models.Model):
    property = models.ForeignKey(
        Property, verbose_name=Property._meta.verbose_name)
    # room = models.ForeignKey(Room, null=True, blank=True,
    #     default=None, verbose_name=Room._meta.verbose_name)
    image = models.ImageField(_('image'), upload_to='property')
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFill(200, 100)],
                                      format='JPEG',
                                      options={'quality': 60})

    class Meta:
        verbose_name = _("property image")

    def image_thm(self):
        if self.image_thumbnail:
            return u'<a href="%s" target="blank" /><img src="%s" /></a>' % \
                (self.image.url, self.image_thumbnail.url)
        else:
            return '(No image found)'
    image_thm.short_description = 'Thumb'
    image_thm.allow_tags = True
    def __unicode__(self):
        return ''
    def __str__(self):
        return ''


class PropertyFile(models.Model):
    property = models.ForeignKey(
        Property, verbose_name=Property._meta.verbose_name)
    name = models.CharField(_("name"), max_length=255)
    file = models.FileField(_('file'), upload_to='property')

    class Meta:
        verbose_name = _("file")
        verbose_name_plural = _("files")

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name

def validate_month(value):
    if value is not None and value.day != 1:
        raise ValidationError(
            _("month expected. Please use first day of the month"))


class Utility(models.Model):
    property = models.ForeignKey(
        Property, verbose_name=Property._meta.verbose_name)
    name = models.CharField(_("name"), max_length=255)
    account = models.CharField(_("account info"), max_length=255, blank=True)
    issueday = models.SmallIntegerField(_("issue day"), default=1,
        validators=[MinValueValidator(0),MaxValueValidator(31)])
    issuemonth = models.SmallIntegerField(_("issue month"), default=0,
        choices=(
            (0,"All"), (1,"Jan"), (2,"Feb"), (3,"Mar"), (4,"Apr"),
            (5,"May"), (6,"Jun"), (7,"Jul"), (8,"Aug"), (9,"Sep"),
            (10,"Oct"), (11,"Nov"), (12, "Dec")
        )
    )
    gracedays = models.SmallIntegerField(_("grace days"), default=15,
        validators=[MinValueValidator(0),MaxValueValidator(99)])
    paydby = models.SmallIntegerField(_("paid by"), default=0,
        choices=( (0,"Tenant"), (1,"Landlord"), (3, "Other") )
    )
    class Meta:
        verbose_name = _("utility")
        verbose_name_plural = _("utilities")
        ordering = ['name']

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name

class Tenant(models.Model):
    property = models.ForeignKey(
        Property,
        verbose_name=Property._meta.verbose_name,
        on_delete=models.PROTECT)
    name = models.CharField(_("name"), max_length=255)
    tenancy_begin_date = models.DateField(_("tenancy begin date"))
    tenancy_end_date = models.DateField(
        _("tenancy end date"), blank=True, null=True)
    deposit = models.DecimalField(
        _("deposit"), max_digits=7, decimal_places=2,
        help_text=_(
            'A sum of money asked to tenant on day 1. '
            'It is payed back in full on the final day of the tenancy'),
        validators=[MinValueValidator(0)], default=0)
    contact_info = models.TextField(_("contact info"), blank=True)
    notes = models.TextField(_("notes"), blank=True)

    def cashflows(self, date_until=None):
        if date_until is None:
            date_until = date.today()
        rents = revisions_to_cashflows(
            date_until, self.rentrevision_set.all())
        payments = payments_to_cashflows(
            date_until, self.payment_set.all(), Payment)
        refunds = payments_to_cashflows(
            date_until, self.refund_set.all(), Refund, negate=True)
        discounts = payments_to_cashflows(
            date_until, self.discount_set.all(), Discount)
        fees = payments_to_cashflows(
            date_until, self.fee_set.all(), Fee, negate=True)
        deposit_cashflows = self.deposit_cashflows(date_until)
        non_sorted = itertools.chain.from_iterable([
            payments, refunds, rents, fees, discounts, deposit_cashflows])
        date_sorted = sorted(non_sorted, key=attrgetter('date', 'amount'))
        result = []
        balance = 0
        for c in date_sorted:
            balance += c.amount
            result.append(
                CashflowAndBalance(c.date, c.amount, c.description, balance))
        return reversed(result)

    def deposit_cashflows(self, date_until):
        result = [Cashflow(
            self.tenancy_begin_date, -self.deposit, _('deposit'))]
        if self.has_left(date_until):
            result.append(Cashflow(
                self.tenancy_end_date, self.deposit, _('deposit refund')))
        return result

    def trend(self):
        return moving_average(date.today(), list(self.cashflows()), 3)

    def balance(self):
        return sum([c.amount for c in self.cashflows()])

    def has_left(self, date_until=None):
        if date_until is None:
            date_until = date.today()
        return (
            self.tenancy_end_date is not None
            and date_until > self.tenancy_end_date)

    def rent(self):
        query_set = self.rentrevision_set.all()
        result = query_set.aggregate(Max('rent'))['rent__max']
        if result is None:
            result = 0
        return result

    # Translators: This is the balance of the tenant's payments
    balance.short_description = _("balance")

    def expired_reminders_count(self):
        return (
            self.reminder_set
            .filter(read=False)
            .filter(date__lte=date.today())
            .count())

    def pending_reminders_count(self):
        return (
            self.reminder_set
            .filter(read=False)
            .count())

    class Meta:
        verbose_name = _("tenant")
        verbose_name_plural = _("tenants")
        ordering = ['tenancy_end_date', 'name']

    def __unicode__(self):
        return u"{} {}".format(self.name, self.property)


class TenantFile(models.Model):
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    name = models.CharField(_("name"), max_length=255)
    file = models.FileField(_('file'), upload_to='tenant')

    class Meta:
        verbose_name = _("file")
        verbose_name_plural = _("files")

    def __unicode__(self):
        return self.name
    def __str__(self):
        return self.name


class Reminder(models.Model):
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    date = models.DateField(_("date"))
    text = models.TextField(_("description"))
    text.widget = Textarea(attrs={'rows': 2})
    read = models.BooleanField(_("mark as read"), default=False)

    class Meta:
        verbose_name = _("reminder")
        verbose_name_plural = _("reminders")
        ordering = ['-date']

    def __unicode__(self):
        return u"{} : {}".format(self.tenant, self.text)


class RentRevision(models.Model):
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    start_date = models.DateField(_("start date"))
    end_date = models.DateField(
        _("end date"), blank=True, null=True, help_text=_(
            "date at which the rent generation should stop (non-inclusive)"))
    rent = models.DecimalField(
        _("monthly rent"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)])
    provision = models.DecimalField(
        _("monthly provision"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = _("rent revision")
        verbose_name_plural = _("rent revisions")
        ordering = ['-start_date']

    def __unicode__(self):
        return u"{} - {}".format(self.start_date, self.end_date or "")


class PropertyExpense(models.Model):
    """amounts paid for property """
    property = models.ForeignKey(
        Property,
        verbose_name=Property._meta.verbose_name,
        on_delete=models.PROTECT)
    description = models.CharField(
        _("description"), max_length=1024)
    pmtype = models.CharField(_("Payment Type"), max_length=4,
        choices = (
            ("BILL", "Bill"),
            ("TAX",  "Tax"),
            ("COM",  "Commission"),
            ("MNTN", "Maintenance")
        ), default = "BILL" )
    amount = models.DecimalField(_("amount"), max_digits=7, decimal_places=2)
    date = models.DateField(_("due date"))
    bytenant = models.BooleanField(_("paid by tenant"))
    paid = models.BooleanField(_("paid"))

    class Meta:
        verbose_name = _("property expense")
        ordering = ['-date']

    def __unicode__(self):
        return u"{} - {}".format(self.date, self.amount)


class Inventory(models.Model):
    """Inventory on property passed on tenant"""
    property = models.ForeignKey(
        Property,
        verbose_name=Property._meta.verbose_name,
        on_delete=models.PROTECT)
    room = models.ForeignKey(Room, null=True, blank=True, default=None,
                             verbose_name=Room._meta.verbose_name,
                             on_delete=models.PROTECT)
    name = models.CharField(_("name"), max_length=100)
    amount = models.SmallIntegerField(_("nr of items"), default=1)
    condition = models.CharField(_("usage condition"), max_length=5,
        choices = (
            ("NEW", "new"),
            ("LKNEW", "like new"),
            ("GOOD", "good"),
            ("USED", "used"),
            ("POOR", "poor")
        ), default = "GOOD" )
    value = models.SmallIntegerField(_("replacement value (ron)"), default=1)
    pdate = models.DateField(_("purchase date"))
    rdate = models.DateField(_("last repair date"), null=True, blank=True)
    class Meta:
        verbose_name = _("inventory on property")
        verbose_name_plural = _("inventory on property")


class Payment(models.Model):
    """money received from the tenant"""
    description = models.CharField(
        _("description"), max_length=1024)
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    date = models.DateField(_("date"))
    amount = models.DecimalField(
        _("amount"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = _("payment received from tenant")
        verbose_name_plural = _("payments received from tenant")
        ordering = ['-date']

    def __unicode__(self):
        return u"{} - {}".format(self.date, self.amount)
    def __str__(self):
        return u"{} - {}".format(self.date, self.amount)


class Refund(models.Model):
    """money returned to the tenant"""
    description = models.CharField(
        _("description"), max_length=1024)
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    date = models.DateField(_("date"))
    amount = models.DecimalField(
        _("amount"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = _("money transfer to tenant")
        verbose_name_plural = _("money transfers to tenant")
        ordering = ['-date']

    def __unicode__(self):
        return u"{} - {}".format(self.date, self.amount)
    def __str__(self):
        return u"{} - {}".format(self.date, self.amount)


class Fee(models.Model):
    """a one-time fee (for example an end of year adjustment fee)"""
    description = models.CharField(_("description"), max_length=255)
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    date = models.DateField(_("date"))
    amount = models.DecimalField(
        _("amount"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)], default=0)

    class Meta:
        verbose_name = _("one-time fee")
        verbose_name_plural = _("one-time fees")
        ordering = ['-date']

    def __unicode__(self):
        return u"{} - {}".format(self.description, self.date)
    def __str__(self):
        return u"{} - {}".format(self.description, self.date)


class Discount(models.Model):
    """a one-time discount
    example: the tenant repainted a room and the
    landlord agrees to pay for it
    """
    description = models.CharField(_("description"), max_length=255)
    tenant = models.ForeignKey(Tenant, verbose_name=Tenant._meta.verbose_name)
    date = models.DateField(_("date"))
    amount = models.DecimalField(
        _("amount"), max_digits=7, decimal_places=2,
        validators=[MinValueValidator(0)], default=0)

    class Meta:
        verbose_name = _("one-time discount")
        verbose_name_plural = _("one-time discount")
        ordering = ['-date']

    def __unicode__(self):
        return u"{} - {}".format(self.description, self.date)
    def __str__(self):
        return u"{} - {}".format(self.description, self.date)

Cashflow = namedtuple('Cashflow', ['date', 'amount', 'description'])
CashflowAndBalance = namedtuple('Cashflow',
                                ['date', 'amount', 'description', 'balance'])


def payments_to_cashflows(
        date, payments, model_class, negate=False):
    for p in payments:
        if p.date > date:
            continue
        model_class_label = model_class._meta.verbose_name
        if p.description:
            # Translators: this is used for the tenant cashflow summary,
            # for example: 'one-time-fee "broken window fee"'
            d = _('%(model_class)s "%(description)s"') % {
                'model_class': model_class_label,
                'description': p.description}
        else:
            d = model_class_label
        yield Cashflow(p.date, -p.amount if negate else p.amount, d)


def first_of_month_range(start_date, end_date):
    start_index = 12*start_date.year + start_date.month
    end_index = 12*end_date.year + end_date.month
    for index in range(start_index, end_index):
        month =int((index - 1) % 12 + 1)
        year = int((index - 1) / 12)
        yield date(year, month, 1)


TWOPLACES = Decimal('0.00')


def fractional_amount(amount, days, month_days):
    """Computes the amount for months that are not paid in full
    """
    return Decimal(amount * days / month_days).quantize(TWOPLACES)


def revision_to_cashflows(rev, end_date):
    """Converts a revision to a list of cashflows
    end_date -- the date from which we want to stop computing
    """
    if rev.end_date is not None:
        end_date = next_month(rev.end_date)
    result = []
    for first_of_month in first_of_month_range(rev.start_date, end_date):
        start = max(first_of_month, rev.start_date)
        end = next_month(first_of_month)
        if rev.end_date is not None:
            end = min(end, rev.end_date)
        delta = end - start
        total_days = monthrange(first_of_month.year, first_of_month.month)[1]
        rent = fractional_amount(-rev.rent, delta.days, total_days)
        result.append(Cashflow(first_of_month, rent, _("rent")))
        if rev.provision != 0:
            p = fractional_amount(-rev.provision, delta.days, total_days)
            result.append(Cashflow(
                first_of_month, p, _("provision")))
    return result


def revisions_to_cashflows(date, revisions):
    date = next_month(date)
    result = map(lambda r: revision_to_cashflows(r, date), revisions)
    joined_result = itertools.chain.from_iterable(result)
    return [c for c in joined_result if c.date < date]


def next_month(date, increment=1):
    date = date.replace(day=1)
    return add_month(date, increment)


def add_month(d, increment=1):
    month = d.month - 1 + increment
    year = int(d.year + month / 12)
    month = int(month % 12 + 1)
    day = d.day
    max_day = monthrange(year, month)[1]
    day = int(min(day, max_day))
    return date(month=month, year=year, day=day)


def pop_cashflows_until(sorted_cashflows, until):
    result = []
    while len(sorted_cashflows) > 0 and sorted_cashflows[0].date < until:
        c = sorted_cashflows.popleft()
        result.append(c)
    return result


def moving_average(to_date, sorted_cashflows, size):
    """
    Returns an array of the requested size.
    Each point of this array correspond to the average balance of the account
    over the course of a month
    The last point is the average between to_date and to_date - 1 month
    """
    if len(sorted_cashflows) == 0:
        sorted = True
    else:
        sorted = sorted_cashflows[-1].date <= sorted_cashflows[0].date
    assert sorted, "sorted_list is not sorted"
    # clone and sort by ascending date
    cashflows = deque(reversed(sorted_cashflows))
    from_date = add_month(to_date, -size)
    cashflows_before = pop_cashflows_until(cashflows, from_date)
    balance = 0
    balance += sum([float(c.amount) for c in cashflows_before])
    result = []
    for i in range(size):
        to_date = add_month(from_date)
        month_cashflows = pop_cashflows_until(cashflows, to_date)
        product = 0
        last_balance = balance
        last_date = from_date
        for c in month_cashflows:
            product += last_balance * (c.date - last_date).days
            last_balance += float(c.amount)
            last_date = c.date
        product += last_balance * (to_date - last_date).days
        result.append(product / (to_date - from_date).days)
        from_date = to_date
        balance = last_balance
    return result

# vim: ai ts=4 sts=4 et sw=4
from django.test import TestCase
from views import create_formset, submit_form, remove_saved_lines
from main.models import Property, Tenant, Building, Payment
from datetime import date
from models import ImportLine
from django.contrib.auth.models import User
from django.test import Client
from decimal import Decimal
import views


class BankImporter(TestCase):
    @classmethod
    def setUpClass(cls):
        # MIN_SCORE has been optimized based on the number of tenants
        # since we only have 2 tenants we'll never match anything with
        # a non-zero min_score
        cls.prevMinScore = views.MIN_SCORE
        views.MIN_SCORE = 0.0

    @classmethod
    def tearDownClass(cls):
        views.MIN_SCORE = cls.prevMinScore

    def setUp(self):
        building = Building.objects.create(name="test building")
        property = Property.objects.create(
            name="test property", building=building,
            address="test address", area=53, rooms=3)
        self.tenant_a = Tenant.objects.create(
            property=property, name="Olivier Adam",
            tenancy_begin_date=date(2011, 1, 1),
            tenancy_end_date=date(2013, 9, 1))
        self.tenant_b = Tenant.objects.create(
            property=property, name="John Doe",
            tenancy_begin_date=date(2011, 1, 1),
            tenancy_end_date=date(2013, 9, 1))
        User.objects.create_user(
            'toto', 'toto@gmail.com', 'toto_pass')

    def test_guesses(self):
        lines = [
            ImportLine(
                date=date(day=1, month=1, year=2011),
                amount=Decimal('100'),
                caption="Vir Olivier Adam rent january"),
            ImportLine(
                date=date(day=3, month=1, year=2011),
                amount=Decimal('600'),
                caption="Doe rent"),
            ImportLine(
                date=date(day=3, month=1, year=2011),
                amount=Decimal('12.98'),
                caption="unrelated utility bill"),
            ImportLine(
                date=date(day=1, month=2, year=2011),
                amount=Decimal('100'),
                caption="Vir Olivier Adam rent february"),
            ]
        current_mapping = [{'mapping': ''} for x in lines]
        formset = create_formset(lines, current_mapping)
        choices = [form['mapping'].field.choices for form in formset]
        self.assertEquals(len(choices), 4)
        self.assertEquals([c[0][0] for c in choices], [''] * 4)
        self.assertEquals([c[1][0] for c in choices], ['HIDE'] * 4)
        # automatic guesses
        self.assertEquals([len(c[2][1]) for c in choices], [1, 1, 0, 1])
        a_choice = '["tenant_payment", {}]'.format(self.tenant_a.id)
        self.assertEquals(choices[0][2][1][0][0], a_choice)
        self.assertEquals(choices[3][2][1][0][0], a_choice)
        # exhaustive tenant choices
        self.assertEquals([len(c[3][1]) for c in choices], [2] * 4)

    def test_save(self):
        lines = [
            ImportLine(
                date=date(day=1, month=1, year=2011),
                amount=Decimal('100'),
                caption="Vir Olivier Adam rent january"),
            ImportLine(
                date=date(day=3, month=1, year=2011),
                amount=Decimal('600'),
                caption="Doe rent"),
            ImportLine(
                date=date(day=3, month=1, year=2011),
                amount=Decimal('12.98'),
                caption="unrelated utility bill"),
            ]
        data = {
            'form-INITIAL_FORMS': '3',
            'form-TOTAL_FORMS': '3',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-mapping':
                '["tenant_payment", {}]'
                .format(self.tenant_a.id),
            'form-1-mapping':
                '["tenant_payment", {}]'
                .format(self.tenant_b.id),
            'form-2-mapping': 'HIDE'
        }
        current_mapping = [{'mapping': ''} for x in lines]
        formset = create_formset(lines, current_mapping, post=data)
        is_valid = formset.is_valid()
        self.assertTrue(is_valid)
        cleaned = [f.cleaned_data.get('mapping') for f in formset]
        submit_form(lines, cleaned)
        # we've mapped all lines so they should not reappear
        saved_removed = remove_saved_lines(lines)
        self.assertEqual(
            saved_removed, [],
            msg='imported lines stop showing up')
        # cashflows must have been created for tenants
        payments = Payment.objects.all()
        self.assertEqual(len(payments), 2)

    def test_upload_page(self):
        c = Client()
        c.login(username='toto', password='toto_pass')
        response = c.get('/import', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_submit(self):
        c = Client()
        c.login(username='toto', password='toto_pass')
        with open('bank_import/import_test.csv') as fp:
            response = c.post(
                '/import',
                {type: 'CA-CSV', file: fp},
                follow=True)
        self.assertEqual(response.status_code, 200)

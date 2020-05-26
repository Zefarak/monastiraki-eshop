# Generated by Django 3.0.1 on 2020-05-02 07:28

import cart.validators
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('voucher', '0001_initial'),
        ('site_settings', '0007_shipping_site_tracker'),
        ('catalogue', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(blank=True, max_length=50, null=True, verbose_name='Κωδικός')),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('Open', 'Open - currently active'), ('Merged', 'Merged - superceded by another basket'), ('Saved', 'Saved - for items to be purchased later'), ('Frozen', 'Frozen - the basket cannot be modified'), ('Submitted', 'Submitted')], default='Open', max_length=128, verbose_name='Status')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('date_merged', models.DateTimeField(blank=True, null=True, verbose_name='Date merged')),
                ('date_submitted', models.DateTimeField(blank=True, null=True, verbose_name='Date submitted')),
                ('shipping_method_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('payment_method_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('final_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Αξία')),
                ('value', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[cart.validators.validate_positive_decimal], verbose_name='Αξία Προϊόντων')),
                ('discount_value', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Έκπτωση')),
                ('voucher_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Έκπτωση από Κουπόνια')),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.PaymentMethod', verbose_name='Αντικαταβολή')),
                ('shipping_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='site_settings.Shipping', verbose_name='Τρόπος Μεταφοράς')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL, verbose_name='Χρήστης')),
                ('vouchers', models.ManyToManyField(to='voucher.Voucher')),
            ],
            options={
                'ordering': ['-id'],
            },
            managers=[
                ('my_query', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.PositiveIntegerField(default=1)),
                ('have_attributes', models.BooleanField(default=False)),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[cart.validators.validate_positive_decimal])),
                ('price_discount', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[cart.validators.validate_positive_decimal])),
                ('final_value', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[cart.validators.validate_positive_decimal])),
                ('total_value', models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[cart.validators.validate_positive_decimal])),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='cart.Cart')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogue.Product')),
            ],
        ),
        migrations.CreateModel(
            name='CartProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('first_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Ονομα')),
                ('last_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Επιθετο')),
                ('address', models.CharField(blank=True, max_length=100, null=True, verbose_name='Διευθυνση')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Πολη')),
                ('zip_code', models.CharField(blank=True, max_length=5, null=True, verbose_name='Ταχυδρομικος Κωδικας')),
                ('cellphone', models.CharField(blank=True, max_length=10, null=True, verbose_name='Κινητό')),
                ('phone', models.CharField(blank=True, max_length=10, verbose_name='Σταθερο Τηλεφωνο')),
                ('notes', models.TextField(blank=True, verbose_name='Σημειωσεις')),
                ('cart_related', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart_profile', to='cart.Cart')),
            ],
        ),
        migrations.CreateModel(
            name='CartItemAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=1)),
                ('attribute', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.Attribute')),
                ('cart_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attribute_items', to='cart.CartItem')),
            ],
        ),
    ]

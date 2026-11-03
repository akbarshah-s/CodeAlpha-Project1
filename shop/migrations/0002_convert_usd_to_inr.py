from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations


USD_TO_INR_RATE = Decimal('94.928524')
CENT = Decimal('0.01')


def convert_amount(amount):
    return (amount * USD_TO_INR_RATE).quantize(CENT, rounding=ROUND_HALF_UP)


def restore_amount(amount):
    return (amount / USD_TO_INR_RATE).quantize(CENT, rounding=ROUND_HALF_UP)


def convert_prices(apps, schema_editor, converter):
    database = schema_editor.connection.alias
    Product = apps.get_model('shop', 'Product')
    Order = apps.get_model('shop', 'Order')
    OrderItem = apps.get_model('shop', 'OrderItem')

    for product in Product.objects.using(database).iterator():
        product.price = converter(product.price)
        if product.discount_price is not None:
            product.discount_price = converter(product.discount_price)
        product.save(using=database, update_fields=['price', 'discount_price'])

    for order in Order.objects.using(database).iterator():
        order.total_price = converter(order.total_price)
        order.save(using=database, update_fields=['total_price'])

    for item in OrderItem.objects.using(database).iterator():
        item.price = converter(item.price)
        item.save(using=database, update_fields=['price'])


def forwards(apps, schema_editor):
    convert_prices(apps, schema_editor, convert_amount)


def backwards(apps, schema_editor):
    convert_prices(apps, schema_editor, restore_amount)


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

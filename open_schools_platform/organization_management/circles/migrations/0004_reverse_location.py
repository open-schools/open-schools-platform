from django.db import migrations


def reverse_circles_location(apps, schema_editor):
    circles = apps.get_model('circles', 'Circle')
    for circle in circles.objects.all():
        x = circle.location.x
        circle.location.x = circle.location.y
        circle.location.y = x
        circle.save()


def return_location_to_initial(apps, schema_editor):
    circles = apps.get_model('circles', 'Circle')
    for circle in circles.objects.all():
        y = circle.location.y
        circle.location.y = circle.location.x
        circle.location.x = y
        circle.save()


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0003_circle_location'),
    ]

    operations = [
        migrations.RunPython(reverse_circles_location, return_location_to_initial)
    ]

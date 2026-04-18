from django.db import migrations

def create_initial_categories(apps, schema_editor):
    # We get the model from the versioned app registry
    Category = apps.get_model('transactions', 'Category')
    
    # List the categories you want in your production app
    category_list = [
        "Food & Dining",
        "Transportation",
        "Rent & Utilities",
        "Shopping",
        "Entertainment",
        "Health",
        "Salary",
        "Gifts",
    ]

    for name in category_list:
        Category.objects.get_or_create(name=name)

class Migration(migrations.Migration):

    dependencies = [
        # This tells Django to run your initial table creation first
        ('transactions', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(create_initial_categories),
    ]
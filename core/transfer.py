import os
import django
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from django.conf import settings
from core.models import User
from django.db import transaction
from django.contrib.auth.hashers import make_password


# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planejaMed2.settings")  # Adjust project name
django.setup()

# MySQL connection settings (adjust as needed)
MYSQL_DB_URI = "mysql+pymysql://david:741852@localhost/planejamed"

# Create MySQL engine and session
engine = create_engine(MYSQL_DB_URI)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData()
metadata.reflect(bind=engine)

# Define the MySQL table (adjust as needed)
old_table = Table("users", metadata, autoload_with=engine)

# Fetch all records
with session.begin():
    records = session.execute(old_table.select()).fetchall()

# Data transformation function
def transform_data(old_record):
    """Convert MySQL record to match Django model."""

    if old_record.middle_name == "":
        name = f"{old_record.first_name.strip()} {old_record.last_name.strip()}".strip()
    else:
        name = f"{old_record.first_name.strip()} {old_record.middle_name.strip()} {old_record.last_name.strip()}".strip()

    return {
        "name": name,
        "crm": old_record.crm,
        "rqe": old_record.rqe,

        "email": old_record.email,
        "phone": old_record.phone,  # Adjust as necessary

        "is_active": old_record.is_active,
        "is_invisible": not old_record.is_visible,

        "is_manager": old_record.pre_approved_vacation,
        "is_staff": old_record.is_root,
        "is_superuser": old_record.is_root,

        "date_joined": old_record.date_joined,
        "compliant_since": old_record.compliant_since,

        "password": make_password("123456"),
    }

# Insert into SQLite3 Django DB
with transaction.atomic():
    new_objects = [User(**transform_data(row)) for row in records if (row.crm != 10000 and row.crm != 0)]
    User.objects.bulk_create(new_objects)

print(f"Successfully transferred {len(new_objects)} records from MySQL to SQLite3.")

from pymongo import MongoClient
import tempfile, zipfile, configparser
from rest_framework.test import APIClient

from audit.models import AuditType, AuditSession, AuditCategory, AuditQuestion
from authentication.models import Auditor
from django.contrib.auth.models import User

DB = MongoClient(
    "mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true"
)[config.get('credentials', 'database')]


def cek_mongodb(name_collection, id):
    # Check that the files were saved to the child collection
    collection = DB[name_collection]
    data_name = name_collection + "-" + id
    child_collection = collection[data_name]
    return collection.count_documents(
        {"name": data_name}
    ), child_collection.count_documents({})


def create_test_zip():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.name = "test.zip"

    # Create a zip file with some test data
    with zipfile.ZipFile(temp_file.name, "w") as zip_ref:
        zip_ref.writestr("test1.txt", "test1")
        zip_ref.writestr("test2.txt", "test2")

    return temp_file


def delete_audit_question_session(name_collection, name_child_collection, id):
    collection = DB[name_collection]
    data_name = name_child_collection + "-" + id
    child_collection = collection[data_name]

    collection.delete_one({"name": data_name})
    child_collection.drop()


def login_test():
    config = configparser.ConfigParser()
    config.read("test_config.ini")
    username = config.get("credentials", "test-username")
    password = config.get("credentials", "test-password")

    r = APIClient().post(
        "/authentication/token/", data={"username": username, "password": password}
    )
    return r.json()


def test_post_audit_data():
    client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
    db = client[config.get('credentials', 'database')]
    collection = db["audit_data"]
    data_name = "audit-data-123"
    collection.insert_one({"name": data_name})
    child_collection = collection[data_name]

    lst = [
        {
            "Name": "Alice",
            "Age": 25,
            "filename": "Sheet1"
        }, {
            "Name": "Bob",
            "Age": 30,
            "filename": "Sheet1"
        }]
    for data in lst:
        child_collection.insert_one(data)


def create_test_objects():
    AuditType.objects.update_or_create(id=123)
    AuditSession.objects.update_or_create(id=123, type=AuditType.objects.get(id=123))
    AuditSession.objects.update_or_create(id=456, type=AuditType.objects.get(id=123))
    AuditSession.objects.update_or_create(
        id=999, type=AuditType.objects.get(id=123), is_active=False
    )
    AuditCategory.objects.update_or_create(
        id=123, audit_type=AuditType.objects.get(id=123)
    )

    AuditQuestion.objects.update_or_create(
        id=123,
        audit_category=AuditCategory.objects.get(id=123),
        query="""
              {
                 "Name": "Alice",
                 "sort": [["Age", 1]],
                 "limit": 0
              }
              """,
    )
    AuditQuestion.objects.update_or_create(
        id=456,
        audit_category=AuditCategory.objects.get(id=123),
        query="""
                  {
                     "Name": "Alice",
                     "sort": [["Age", 1]],
                     "limit": 0
                  }
                  """,
    )
    AuditQuestion.objects.update_or_create(
        id=789,
        audit_category=AuditCategory.objects.get(id=123),
    )


def delete_test_objects():
    AuditQuestion.objects.get(id=789).delete()
    AuditQuestion.objects.get(id=456).delete()
    AuditQuestion.objects.get(id=123).delete()
    AuditCategory.objects.get(id=123).delete()
    AuditSession.objects.get(id=999).delete()
    AuditSession.objects.get(id=456).delete()
    AuditSession.objects.get(id=123).delete()
    AuditType.objects.get(id=123).delete()


def make_auditors_test():
    user_0 = User.objects.create_user(
        "testing0", password="password0", first_name="testing", last_name="0", id=0
    )
    user_1 = User.objects.create_user(
        "testing1", password="password1", first_name="testing", last_name="1", id=123
    )
    user_2 = User.objects.create_user(
        "testing2", password="password2", first_name="testing", last_name="2", id=456
    )
    user_3 = User.objects.create_user(
        "testing3", password="password3", first_name="testing", last_name="3", id=789
    )

    session_1 = AuditSession.objects.get(id=123)
    session_2 = AuditSession.objects.get(id=456)
    session_2.is_active = False
    session_2.save()

    auditor_1, created = Auditor.objects.update_or_create(
        user=user_1, id=123, on_audit=True, session=session_1
    )

    auditor_2, created = Auditor.objects.update_or_create(
        user=user_2, id=456, on_audit=True, session=session_1
    )

    Auditor.objects.update_or_create(
        user=user_3,
        id=789,
    )

    Auditor.objects.update_or_create(
        user=user_0, id=0, on_audit=True, session=session_1
    )

    return [auditor_1, auditor_2]


def delete_auditors_test():
    User.objects.get(username="testing0").delete()
    User.objects.get(username="testing1").delete()
    User.objects.get(username="testing2").delete()
    User.objects.get(username="testing3").delete()

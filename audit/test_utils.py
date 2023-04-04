from pymongo import MongoClient
import tempfile, zipfile, configparser, requests


def cek_mongodb(name_collection, id):
    # Check that the files were saved to the child collection
    client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
    db = client['masys']
    collection = db[name_collection]
    data_name = name_collection + '-' + id
    child_collection = collection[data_name]
    return collection.count_documents({'name': data_name}), child_collection.count_documents({})


def create_test_zip():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.name = "test.zip"

    # Create a zip file with some test data
    with zipfile.ZipFile(temp_file.name, 'w') as zip_ref:
        zip_ref.writestr('test1.txt', 'test1')
        zip_ref.writestr('test2.txt', 'test2')

    return temp_file


def delete_audit_question_session(name_collection, id):
    client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
    db = client['masys']
    collection = db[name_collection]
    data_name = name_collection + '-' + id
    child_collection = collection[data_name]

    collection.delete_one({'name': data_name})
    child_collection.drop()


def login_test():
    login_url = 'http://localhost:8000/authentication/token/'

    config = configparser.ConfigParser()
    config.read('test_config.ini')
    username = config.get('credentials', 'test-username')
    password = config.get('credentials', 'test-password')

    r = requests.post(login_url, json={"username": username, "password": password})
    return r.json()

from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from pymongo import MongoClient
import json, re, zipfile

from audit.models import AuditQuestion, AuditSession
from audit.serializer import AuditQuestionSerializer
@require_GET
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sample(request):
    id_session = request.GET.get('id_session')
    id_question = request.GET.get('id_question')

    query_string = AuditQuestion.objects.get(id=int(id_question)).query

    if query_string != '':
        session = AuditSession.objects.get(
            id=int(id_session))
        date = session.date

        query, sort, limit = manage_query(query_string, date)

        try:
            data_json = query_sample(id_session, query, sort, limit)
            return HttpResponse(data_json, content_type="application/json")
        except ValueError:
            msg = "Data audit tidak ditemukan. Harap upload data terlebih dahulu."
            return Response(data={'message': msg}, status=status.HTTP_404_NOT_FOUND)
    else:
        msg = "Query tidak ditemukan. Harap menghubungi Admin untuk memasukkan query."
        return Response(data={'message': msg}, status=status.HTTP_404_NOT_FOUND)


def manage_query(query_str, date):
    query = json.loads(query_str)

    try:
        sort = eval(re.sub(r'\[([\w\',\s-]+)]', r'(\1)', str(query["sort"])))
        del query["sort"]
    except KeyError:
        sort = {}

    try:
        limit = query["limit"]
        del query["limit"]
    except KeyError:
        limit = 0

    if "TGL_KONDISI" in query:
        query = query_date(query, date, ["TGL_KONDISI", "$gte"])
        query = query_date(query, date, ["TGL_KONDISI", "$lte"])

    query_str = json.dumps(query, default=json_converter)

    return json.loads(query_str), sort, limit


def json_converter(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def query_date(query, date, params):
    date_str = query[params[0]][params[1]]

    # date is for date_str == "TODAY"

    if date_str == "LASTYEAR":
        date = date - timedelta(days=365)
    elif date_str == "LASTMONTH":
        date = date - timedelta(days=30)
    elif date_str == "YESTERDAY":
        date = date - timedelta(days=1)

    query[params[0]][params[1]] = date

    return query


def query_sample(id_session, query, sort, limit):
    client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
    db = client['masys']
    collection = db['audit_data']
    data_name = 'audit-data-' + str(id_session)

    data_count = collection.count_documents({'name': data_name})

    if data_count != 0:
        child_collection = collection[data_name]
        if sort == {}:
            data = list(child_collection.find(query, {"_id": 0}).limit(limit))
        else:
            data = list(child_collection.find(query, {"_id": 0}).sort(sort).limit(limit))
        return json.dumps(data)
    else:
        raise ValueError("Data audit cannot be empty.")


@require_POST
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_audit_question_session(request):
    id_audit = request.POST.get('id_audit')
    zip_attachment = request.FILES.get('attachment')
    comment = request.POST.get('comment')
    remark = request.POST.get('remark')

    client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
    db = client['masys']
    collection = db['attachment']
    data_name = 'attachment-' + str(id_audit)

    data_count = collection.count_documents({'name': data_name})

    if data_count == 0:
        collection.insert_one({'name': data_name})
    child_collection = collection[data_name]

    data = {}
    data = save_comment_remark(comment, remark, data)
    data = save_attachment(zip_attachment, data)

    child_collection.insert_one(data)

    return Response(data={'message': "File uploaded to database"}, status=status.HTTP_200_OK)


def save_attachment(zip_file, data):
    extracted_data = extract_zip(zip_file)

    count = 0
    for filename, file_data in extracted_data.items():
        count = count + 1
        data.update({'file_name_' + str(count): filename})
        data.update({'file_data_' + str(count): file_data})

    return data


def save_comment_remark(comment, remark, data):
    data.update({'comment': str(comment)})
    data.update({'remark': str(remark)})

    return data


def extract_zip(zip_file):
    result_data = dict()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for filename in zip_ref.namelist():
            file_data = zip_ref.read(filename)
            result_data[filename] = file_data

    return result_data

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from django.views.decorators.http import require_POST
from pymongo import MongoClient
from audit.views import extract_zip


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

    if (data_count == 0):
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
from django.shortcuts import get_object_or_404
from pymongo import MongoClient
from audit.models import AuditCategory, AuditHistory, AuditQuestion, AuditSession, AuditType

class PdfDTO:
    def __init__(self, history: AuditHistory):
        audit_session = get_object_or_404(AuditSession, pk=history.audit_session.id)
        audit_type = get_object_or_404(AuditType, pk=audit_session.type.id)
        audit_categories = list(AuditCategory.objects.filter(audit_type=audit_type))
        audit_attachments = self.get_attachments(audit_session.id)

        self.session_id = audit_session.id
        self.type_label = audit_type.label
        self.start_date = self.convert_date(audit_session.date)
        self.end_date = self.convert_date(history.date)
        self.tim_auditor = eval(history.auditors_name)
        self.categories = self.convert_categories(audit_categories, audit_attachments)

    def get_attachments(self, session_id):
        client = MongoClient('mongodb+srv://cugil:agill@juubi-microfinance.am8xna1.mongodb.net/?retryWrites=true')
        db = client[config.get('credentials', 'database')]
        collection_name = f'attachment-{str(session_id)}'
        collection = db['attachment'][collection_name]

        object_list = list(collection.find())
        return object_list


    def convert_date(self, date):
        month_names = {
            'January': 'Januari',
            'February': 'Februari',
            'March': 'Maret',
            'April': 'April',
            'May': 'Mei',
            'June': 'Juni',
            'July': 'Juli',
            'August': 'Agustus',
            'September': 'September',
            'October': 'Oktober',
            'November': 'November',
            'December': 'Desember'
        }

        english_month = date.strftime("%B")
        indonesian_month = month_names[english_month]
        formatted_date = date.strftime("%d %B %Y").replace(english_month, indonesian_month)

        return formatted_date

    def convert_categories(self, audit_categories: list[AuditCategory], audit_attachments):
        categories = []

        for category in audit_categories:
            questions = list(AuditQuestion.objects.filter(audit_category=category))
            categories.append({
                'num_cat': len(categories)+1,
                'name': category.title,
                'questions': self.convert_questions(questions, audit_attachments)
            })

        return categories
    
    def convert_questions(self, audit_questions: list[AuditQuestion], audit_attachments: list):
        questions = [] 

        for question in audit_questions:
            perihal = question.title
            filtered_attachments = [obj for obj in audit_attachments if obj['id_question'] == str(question.id)]
            for attachment in filtered_attachments:
                questions.append({
                    'num_question': len(questions)+1,
                    'perihal': perihal,
                    'catatan': attachment['comment'],
                    'remark': attachment['remark']
                })

        return questions

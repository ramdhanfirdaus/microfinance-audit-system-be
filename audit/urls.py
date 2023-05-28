from django.urls import path

from audit.views.views import (
    get_all_auditors,
    create_new_audit_session,
    post_audit_data,
)
from audit.views.views_questions import (
    get_sample,
    post_audit_question_session,
    get_audit_question,
    get_all_audit_questions,
    add_audit_question,
    get_audit_questions_by_id,
    save_query
)
from audit.views.views_categories import (
    get_audit_categories,
    get_audit_categories_by_session,
    post_audit_category,
    get_all_audit_categories,
)
from audit.views.views_types import get_all_audit_types, post_audit_type
from audit.views.views_sessions import (
    get_auditors_by_session,
    get_session_by_auditor,
    stop_audit,
)
from audit.views.views_history import (
    get_history,
    download_result_pdf,
    get_result_html,
)

urlpatterns = [
    path("create-audit-type", post_audit_type, name="create audit type"),
    path("get-all-audit-types/", get_all_audit_types, name="get_audit_types"),
    path("get-all-auditors/", get_all_auditors),
    path(
        "create-new-audit-session/<str:id>",
        create_new_audit_session,
        name="create_audit_session",
    ),
    path("create-audit-category", post_audit_category, name="create audit category"),
    path(
        "get-all-audit-categories/",
        get_all_audit_categories,
        name="get_audit_categories",
    ),
    path("audit-categories/<str:id>", get_audit_categories, name="audit category"),
    path(
        "audit-categories-by-session/<str:session_id>",
        get_audit_categories_by_session,
        name="get_audit_categories_by_session",
    ),
    path("upload-data", post_audit_data, name="upload data"),
    path("sample-data", get_sample, name="sample data"),
    path(
        "audit-question-session",
        post_audit_question_session,
        name="audit-question-session",
    ),
    path("audit-questions/<str:id>", get_audit_question, name="audit_question"),
    path(
        "get-all-audit-questions",
        get_all_audit_questions,
        name="get_all_audit_questions",
    ),
    path("add-audit-question", add_audit_question, name="add_audit_question"),
    path(
        "get-auditor-by-session/<str:id_session>/<str:user_id>",
        get_auditors_by_session,
        name="get_auditors_by_session",
    ),
    path(
        "get-session-by-auditor/<str:user_id>",
        get_session_by_auditor,
        name="get_session_by_auditor",
    ),
    path("stop-audit", stop_audit, name="stop_audit"),
    path("history", get_history, name="history"),
    path("get-audit-questions-by-id/<str:id>", get_audit_questions_by_id, name="get_audit_questions_by_id"),
    path("download-report-file", download_result_pdf, name="download report file"),
    path("get-result", get_result_html, name="get result"),
    path("save-query", save_query, name="save_query")
]

from django.urls import path
from .views import ChatWithDocumentView, ChatHistoryView

urlpatterns = [
    path("ask/", ChatWithDocumentView.as_view(), name="chat-with-doc"),
    path("history/", ChatHistoryView.as_view(), name="chat-history"),
]

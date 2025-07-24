from django.urls import path
from .views import UploadPDFView, ListUploadedPDFView

urlpatterns = [
    path('upload/', UploadPDFView.as_view(), name='upload-pdf'),
    path('uploaded-files/', ListUploadedPDFView.as_view(), name='list-files'),
]

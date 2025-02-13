from django.urls import path
from .views import S3FileFetchAPIView, S3ImageFetchAPIView
def home_view(request):
    return ({"message": "Welcome to the Django API on AWS Lambda!"})
urlpatterns = [
    # path('' ,home_view),
    path('api/files/<str:class_name>/books/<str:subject>/', S3FileFetchAPIView.as_view(), name='fetch-files'),
    path('api/fetch_images/<str:class_name>/', S3ImageFetchAPIView.as_view(), name='fetch_images'),
]

from django.urls import path

from .views import HealthView, ItemListView

urlpatterns = [
    path("items", ItemListView.as_view(), name="items-list"),
    path("health", HealthView.as_view(), name="health"),
]

from django.urls import path

from .views import hello_word_view, GroupsListView


app_name = "myapiapp"

urlpatterns = [
    path("hello/", hello_word_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
]
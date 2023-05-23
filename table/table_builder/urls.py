from django.urls import path

from table_builder.views import (
    TableBuilderView, TableRowView, TableRowsView, TableAlteringView,
)


urlpatterns = [
    path(r'table/', TableBuilderView.as_view()),
    path(r'table/<str:id>/', TableAlteringView.as_view()),
    path(r'table/<str:id>/row', TableRowView.as_view()),
    path(r'table/<str:id>/rows', TableRowsView.as_view()),
]

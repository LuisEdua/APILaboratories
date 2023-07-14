from django.urls import path
from .views import MeasuresView, SessionView, AdminsView, ManagerView, DispositiveView

urlpatterns=[
    path('measures/', MeasuresView.as_view(), name='measures_list'),
    path('measures/<int:id>', MeasuresView.as_view(), name='measures_process'),
    path('validate/', SessionView.as_view(), name='session_process'),
    path('admin/', AdminsView.as_view(), name='admin_list'),
    path('admin/<int:id>', AdminsView.as_view(), name='admin_process'),
    path('manager/<int:id>', ManagerView.as_view(), name='manager_process'),
    path('dispositive/<int:id>', DispositiveView.as_view(), name='dispositive_process'),
    path('dispositive/', DispositiveView.as_view(), name='dispositive_list')
]
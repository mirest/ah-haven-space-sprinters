from django.urls import path
from .views import (NotificationAPIView,
                    NotificationRetrieveUpdateDestroyAPIView)

urlpatterns = [

    path('notifications', NotificationAPIView.as_view(),
         name='View_app_notifications'),
    path('notifications/<pk>',
         NotificationRetrieveUpdateDestroyAPIView.as_view(),
         name='View_one_notification'),

]

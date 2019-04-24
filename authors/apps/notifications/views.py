from rest_framework import generics, status
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .renderers import NotificationRenderer
from .models import Notification
from django.shortcuts import get_object_or_404


class NotificationAPIView(generics.RetrieveUpdateAPIView):

    serializer_class = NotificationSerializer
    renderer_classes = (NotificationRenderer, )
    permission_classes = (IsAuthenticated, )

    def get(self, request):

        user = request.user
        notifications = Notification.objects.all()
        data = {}

        for notification in notifications:
            if user in notification.notified.all():
                serializer = self.serializer_class(
                    notification, context={'request': request})
                data[notification.id] = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):

        notifications = Notification.objects.all()
        user = request.user
        for notification in notifications:
            if user in notification.notified.all():
                notification.read_by.add(user.id)
                notification.save()
                message = {
                    "message": "You have marked all notifications as read"}
        return Response(message, status=status.HTTP_200_OK)


class NotificationRetrieveUpdateDestroyAPIView(
        generics.RetrieveUpdateDestroyAPIView):

    serializer_class = NotificationSerializer
    renderer_classes = (NotificationRenderer, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):

        notification = get_object_or_404(Notification, pk=pk)
        serializer = self.serializer_class(
            notification, context={'request': request})
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, pk):

        notification = get_object_or_404(Notification, pk=pk)
        user = request.user
        if user in notification.notified.all():
            notification.read_by.add(user.id)
            notification.save()
            message = {"message": "this notification has been marked as read"}
            return Response(message, status=status.HTTP_200_OK)
        else:
            message = {'message': 'this notification is not yours,\
                 cant be marked as read'}
            return Response(message, status.status.HTTP_200_OK)

from rest_framework import generics, permissions
from .models import Task
from .serializers import TaskSerializer

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "owned_farms"):  # Farm Owner
            return Task.objects.filter(farm__owner=user)
        return Task.objects.filter(farm__staff=user)  # Staff member tasks

    def perform_create(self, serializer):
        serializer.save(farm=self.request.user.owned_farms.first())  # Assign farm
        

class TaskRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


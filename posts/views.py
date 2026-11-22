from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer


class PostListView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Post.objects.all()
        language = self.request.query_params.get("language")
        if language:
            queryset = queryset.filter(language=language)
        return queryset

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
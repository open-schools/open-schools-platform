from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Document
from .serializers import DocumentSerializer, DocumentCreateSerializer, DocumentSignSerializer

# POST api/enrollment_agreement/documents/create
class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentCreateSerializer

# GET api/enrollment_agreement/documents/{id}
class DocumentRetrieveView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    lookup_field = 'id'

# POST api/enrollment_agreement/documents/{id}/sign/parent
class DocumentParentSignView(APIView):
    def post(self, request, id):
        document = get_object_or_404(Document, id=id)
        serializer = DocumentSignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signed = serializer.validated_data['signed']
        if signed:
            document.parent_signed = True
            document.save()
        return Response({'parent_signed': document.parent_signed})

# GET api/enrollment_agreement/documents/pending-director-signature
class DocumentsPendingDirectorView(generics.ListAPIView):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        parent_signed = self.request.query_params.get('parent_signed', 'true').lower() == 'true'
        director_signed = self.request.query_params.get('director_signed', 'false').lower() == 'true'
        return Document.objects.filter(parent_signed=parent_signed, director_signed=director_signed)

# POST api/enrollment_agreement/documents/{id}/sign/director
class DocumentDirectorSignView(APIView):
    def post(self, request, id):
        document = get_object_or_404(Document, id=id)
        serializer = DocumentSignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signed = serializer.validated_data['signed']
        if signed:
            document.director_signed = True
            document.save()
        return Response({'director_signed': document.director_signed})

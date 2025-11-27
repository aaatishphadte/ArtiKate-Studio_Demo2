from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import UserSerializer
from backend.knowledge_base.models import Document
from backend.knowledge_base.ingestion import ingest_single_document
from backend.knowledge_base.vectorstore import get_vectorstore
from backend.rag.llm import generate_answer
import jwt
from rest_framework_simplejwt.settings import api_settings


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        from django.contrib.auth import authenticate
        
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"error": "Username and password required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id
        })

class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print("UploadDocumentView reached")
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        document = Document.objects.create(user=request.user, file=file)
        
        # Trigger ingestion
        try:
            ingest_single_document(document.file.path, request.user.id)
            return Response({"message": "Document uploaded and ingested successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class AskQuestionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         question = request.data.get("question", "")
#         if not question:
#             return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # Retrieve similar documents from FAISS with user filter
#         # Note: FAISS filter support depends on the underlying store implementation in LangChain.
#         # For simple FAISS, we might need to filter post-retrieval if direct filtering isn't supported 
#         # Reload vectorstore for the specific user
#         try:
#             vectorstore = get_vectorstore(request.user.id)
#         except FileNotFoundError as e:
#             return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
#         retrieved_docs = vectorstore.similarity_search(
#             question, 
#             k=3
#         )
        
#         if not retrieved_docs:
#              return Response({"answer": "I couldn't find any relevant information in your documents."})

#         context = "\n".join([doc.page_content for doc in retrieved_docs])

#         # Create prompt for local LLM
#         prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

#         # Generate answer using local Hugging Face model
#         answer = generate_answer(prompt)

#         return Response({"answer": answer})

# --------------------------------------------------
#  ASK QUESTION (USER-SPECIFIC RAG)
# --------------------------------------------------
class AskQuestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question")

        if not question:
            return Response({"error": "Question is required"}, status=400)

        
        auth = request.headers.get("Authorization", None)
        if not auth or not auth.startswith("Bearer "):
            return Response(
                {"error": "NUnauthorized"},
                status=401
            )
        token = auth.split()[1]

        from rest_framework_simplejwt.tokens import UntypedToken
        payload = UntypedToken(token)
        claim = api_settings.USER_ID_CLAIM
        print("Claim:", claim)
        user_id = payload[claim]
        print("User ID from token:", user_id)
        # Load user FAISS
        vectorstore = get_vectorstore(user_id)

        if vectorstore is None:
            return Response(
                {"error": "No documents uploaded by this user yet."},
                status=401
            )

        retrieved_docs = vectorstore.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        # Prompt for LLM
        prompt = (
            "Answer the question based strictly on the context below.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )

        answer = generate_answer(prompt)

        # Extract sources
        sources = [doc.metadata.get("source", "Unknown Source") for doc in retrieved_docs]

        return Response({
            "answer": answer,
            "sources": sources
        })
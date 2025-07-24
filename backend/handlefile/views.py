from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UploadedPDFSerializer
from .models import UploadedPDF

import fitz
import openai
from pinecone import Pinecone, ServerlessSpec
import uuid
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Pinecone client
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX")
index = pc.Index(index_name)

class UploadPDFView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            uploaded_files = request.FILES.getlist('files')
            if not uploaded_files:
                return Response({"error": "No files uploaded."}, status=400)

            results = []

            for uploaded_file in uploaded_files:
                serializer = UploadedPDFSerializer(data={'file': uploaded_file})
                if serializer.is_valid():
                    pdf_instance = serializer.save()
                    if not pdf_instance.file:
                        return Response({"error": "No file was uploaded."}, status=400)
                    try:
                        text = self.extract_text_from_pdf(pdf_instance.file.path)
                        chunks = self.chunk_text(text)
                        self.embed_and_store(chunks, pdf_instance.id)

                        results.append({
                            "filename": uploaded_file.name,
                            "file_id": pdf_instance.id,
                            "status": "success"
                        })

                    except Exception as e:
                        results.append({
                            "filename": uploaded_file.name,
                            "status": "error",
                            "error": str(e)
                        })
                else:
                    results.append({
                        "filename": uploaded_file.name,
                        "status": "invalid",
                        "errors": serializer.errors
                    })

            return Response({"results": results}, status=207)

        except Exception as e:
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=500)


    def extract_text_from_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            raise RuntimeError(f"PDF reading failed: {str(e)}")

    def chunk_text(self, text, max_length=500, overlap=50):
        try:
            words = text.split()
            chunks = []
            start = 0
            while start < len(words):
                end = min(start + max_length, len(words))
                chunk = " ".join(words[start:end])
                chunks.append(chunk)
                start += max_length - overlap
            return chunks
        except Exception as e:
            raise RuntimeError(f"Chunking failed: {str(e)}")

    def embed_and_store(self, chunks, doc_id):
        try:
            for i, chunk in enumerate(chunks):
                response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk,
                )
                embedding = response.data[0].embedding
                vector_id = f"{doc_id}_{i}"
                index.upsert([{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "doc_id": str(doc_id)
                    }
                }])
        except Exception as e:
            raise RuntimeError(f"Pinecone upsert or OpenAI embedding failed: {str(e)}")

class ListUploadedPDFView(APIView):
    def get(self, request):
        files = UploadedPDF.objects.all().order_by('-uploaded_at')
        
        # Deduplicate by filename
        seen = set()
        unique_files = []
        for file in files:
            filename = file.file.name.split('/')[-1]
            if filename not in seen:
                seen.add(filename)
                unique_files.append(file)

        serializer = UploadedPDFSerializer(unique_files, many=True)
        return Response(serializer.data)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from .models import ChatMessage
from .serializers import ChatMessageSerializer

from pinecone import Pinecone
import os
import openai

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX"])

openai.api_key = os.environ["OPENAI_API_KEY"]

class ChatWithDocumentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            query = request.data.get("message")
            if not query:
                return Response({"error": "Message is required"}, status=400)

            #Embed the user query
            embed_response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=query,
            )
            query_vector = embed_response.data[0].embedding

            #Search Pinecone
            search_result = index.query(
                vector=query_vector,
                top_k=3,
                include_metadata=True,
            )
            retrieved_chunks = []
            for match in search_result["matches"]:
                text = match["metadata"]["text"].strip()
                if text and text not in retrieved_chunks:  # Deduplicate if needed
                    retrieved_chunks.append(text)
            
            context_text = ""
            for chunk in retrieved_chunks:
                context_text += chunk + "\n\n"
                
            #print("context:",context_text)
            #Send to GPT
            system_prompt = """
            You are an AI assistant providing answers strictly based on the provided document context.

            Guidelines:
            - Carefully analyze the document context and answer with information directly supported by it.
            - If the documents contain related or partial information, synthesize a clear and concise answer while explaining your reasoning.
            - Avoid guessing or adding information not found in the documents.
            - If the documents do not contain relevant information, politely respond: "The document does not contain relevant information for this question."
            - If the question is ambiguous or unclear, ask for clarification: "Can you please explain more about your question?"
            - When multiple possible answers exist, choose the most relevant and explain your choice.
            """

            user_message = (
                f"Document context:\n{context_text}\n"
                f"Question: {query}\n"
                f"Please base your answer solely on the document context above."
            )
            gpt_response = openai.chat.completions.create(
                model="gpt-4.1-nano-2025-04-14",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.4,  
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            answer = gpt_response.choices[0].message.content.strip()

             # Save user message
            ChatMessage.objects.create(message_type="user", message=query)
            # Save AI response
            ChatMessage.objects.create(message_type="ai", message=answer)

            return Response({"answer": answer})

        except Exception as e:
            return Response({"error": f"Chat failed: {str(e)}"}, status=500)

class ChatHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        messages = ChatMessage.objects.all().order_by("time")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

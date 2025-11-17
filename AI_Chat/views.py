from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from openai import AzureOpenAI
from django.conf import settings
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from animals.utils import ask_azure_gpt  # 👈 centralized logic
from datetime import datetime


# ---------------- Azure Client ----------------
client = AzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)


# ---------------- Chat Session List + Create ----------------
class ChatSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        # Each user sees only their own chat sessions
        return ChatSession.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        chat = serializer.save(user=self.request.user)
        topic_hint = self.request.data.get("topic", "").strip()

        try:
            if topic_hint:
                # Use Azure GPT to generate a short chat title
                title_prompt = f"Generate a short 3–5 word title summarizing this topic: '{topic_hint}'"
                title_resp = client.chat.completions.create(
                    model=settings.AZURE_OPENAI_DEPLOYMENT,
                    messages=[{"role": "system", "content": title_prompt}],
                    max_tokens=10,
                )
                chat.title = title_resp.choices[0].message.content.strip().replace('"', "")
            else:
                chat.title = f"New Chat – {datetime.now().strftime('%b %d, %Y %H:%M')}"
        except Exception as e:
            print("Title generation failed:", e)
            chat.title = f"New Chat – {datetime.now().strftime('%b %d, %Y %H:%M')}"
        chat.save()


# ---------------- Chat Message List + Create ----------------
class ChatMessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        chat = ChatSession.objects.filter(id=chat_id, user=request.user).first()
        if not chat:
            return Response({'error': 'Chat not found'}, status=404)

        messages = chat.messages.order_by("created_at")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, chat_id):
        chat = ChatSession.objects.filter(id=chat_id, user=request.user).first()
        if not chat:
            return Response({'error': 'Chat not found'}, status=404)

        user_message = request.data.get("message", "").strip()
        if not user_message:
            return Response({'error': 'Message cannot be empty'}, status=400)

        # Save user message
        ChatMessage.objects.create(chat=chat, role="user", content=user_message)

        # Auto title update if missing
        if not chat.title or chat.title.startswith("New Chat"):
            try:
                title_prompt = f"Generate a short 3–5 word title summarizing this message: '{user_message}'"
                title_resp = client.chat.completions.create(
                    model=settings.AZURE_OPENAI_DEPLOYMENT,
                    messages=[{"role": "system", "content": title_prompt}],
                    max_tokens=10,
                )
                chat.title = title_resp.choices[0].message.content.strip().replace('"', "")
                chat.save(update_fields=["title"])
            except Exception as e:
                print("Title refinement failed:", e)

        # --------- 🧠 Get Chat History for Memory ----------
        history_qs = chat.messages.order_by("created_at").values("role", "content")

        # Convert DB messages into OpenAI format
        message_history = [
            {"role": m["role"], "content": m["content"]} for m in history_qs
        ]

        # Optionally limit messages to reduce token cost (keep last 15 messages)
        message_history = message_history[-15:]

        # --------- 📷 Check for Image Upload ----------
        uploaded_image = request.FILES.get("image")
        query_image_path = None

        if uploaded_image:
            tmp_path = f"/tmp/{uploaded_image.name}"
            with open(tmp_path, "wb+") as f:
                for chunk in uploaded_image.chunks():
                    f.write(chunk)
            query_image_path = tmp_path

        # --------- 🤖 Ask GPT with history included ----------
        try:
            reply = ask_azure_gpt(
                user=request.user,
                user_message=user_message,
                query_image_path=query_image_path,
                history=message_history
            )
        except Exception as e:
            print("Azure GPT API error:", e)
            reply = "I'm sorry, something went wrong while processing your request."

        # Save assistant reply
        ChatMessage.objects.create(chat=chat, role="assistant", content=reply)

        return Response({"reply": reply, "title": chat.title})


# ---------------- Delete Chat Session ----------------
class ChatSessionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, chat_id):
        chat = ChatSession.objects.filter(id=chat_id, user=request.user).first()
        if not chat:
            return Response({'error': 'Chat not found'}, status=404)

        chat.delete()
        return Response({'message': f'Chat {chat_id} deleted successfully.'}, status=204)


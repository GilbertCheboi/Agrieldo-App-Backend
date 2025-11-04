from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from openai import OpenAI
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from datetime import datetime
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 🧠 Chat session list + create (with auto title)
class ChatSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        chat = serializer.save(user=self.request.user)
        topic_hint = self.request.data.get("topic", "").strip()

        try:
            if topic_hint:
                # Generate AI-based title
                title_prompt = f"Generate a short 3–5 word title summarizing this topic: '{topic_hint}'"
                title_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": title_prompt}],
                    max_tokens=10,
                )
                chat.title = title_resp.choices[0].message.content.strip().replace('"', "")
            else:
                # Default title
                chat.title = f"New Chat – {datetime.now().strftime('%b %d, %Y %H:%M')}"
        except Exception as e:
            print("  Title generation failed:", e)
            chat.title = f"New Chat – {datetime.now().strftime('%b %d, %Y %H:%M')}"

        chat.save()
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

        # ✅ Generate or refine chat title if missing
        if not chat.title or chat.title.startswith("New Chat"):
            try:
                title_prompt = f"Generate a short 3–5 word title summarizing this message: '{user_message}'"
                title_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": title_prompt}],
                    max_tokens=10,
                )
                chat.title = title_resp.choices[0].message.content.strip().replace('"', "")
                chat.save(update_fields=["title"])
            except Exception as e:
                print("  Title refinement failed:", e)
        # Build message history
        history = [
            {"role": m.role, "content": m.content}
            for m in chat.messages.order_by("created_at")
        ]

        # AI response
        try:
            ai_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=history,
                max_tokens=200,
            )
            reply = ai_response.choices[0].message.content.strip()
        except Exception as e:
            print("  ChatGPT API error:", e)
            reply = "I'm sorry, something went wrong."

        # Save assistant message
        ChatMessage.objects.create(chat=chat, role="assistant", content=reply)

        return Response({"reply": reply, "title": chat.title})






# 💬 Delete a specific chat session
class ChatSessionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, chat_id):
        chat = ChatSession.objects.filter(id=chat_id, user=request.user).first()
        if not chat:
            return Response({'error': 'Chat not found'}, status=404)

        # Delete all related messages automatically via cascade
        chat.delete()
        return Response({'message': f'Chat {chat_id} deleted successfully.'}, status=204)


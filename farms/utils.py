# farms/utils.py
from django.conf import settings
from pgvector.django import CosineDistance
from openai import AzureOpenAI
from .models import Farm

# ---------------- Azure Client ----------------
client = AzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)

# ---------------- Generic Embedding Helper ----------------
def generate_text_embedding(text: str):
    """
    Generate embedding for any text block using Azure OpenAI.
    """
    try:
        embedding_model = getattr(
            settings, 
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", 
            "text-embedding-3-large"
        )

        response = client.embeddings.create(
            model=embedding_model,
            input=text.strip()
        )

        return response.data[0].embedding

    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return None


# ---------------- Farm Embedding Generator ----------------
def generate_farm_embedding(farm: Farm):
    """
    Generate RAG embedding for a farm.
    """
    text = f"""
    Farm Name: {farm.name}
    Owner: {farm.owner.username if farm.owner else "Unknown Owner"}
    Type: {farm.type}
    Location: {farm.location or "No location specified"}
    Latitude: {farm.latitude or 'N/A'}
    Longitude: {farm.longitude or 'N/A'}
    Google Sheet: {farm.google_sheet_url or "No sheet linked"}
    """

    return generate_text_embedding(text)


# ---------------- Farm Vector Search ----------------
def search_similar_farms(query_embedding, top_k=5):
    """
    Use pgvector cosine similarity to find the closest farms.
    """
    if query_embedding is None:
        return []

    try:
        farms = (
            Farm.objects
            .exclude(embedding=None)
            .annotate(distance=CosineDistance("embedding", query_embedding))
            .order_by("distance")[:top_k]
        )

        return list(farms)

    except Exception as e:
        print("Farm vector similarity search failed:", e)
        return []


# ---------------- Farm Context Builder ----------------
def build_farm_context(farms):
    """
    Convert similar farms into descriptive text blocks for GPT context.
    """
    if not farms:
        return "No similar farms found.\n"

    blocks = ["--- FARM CONTEXT ---"]

    for farm in farms:
        blocks.append(f"""
        Farm Name: {farm.name}
        Owner: {farm.owner.username if farm.owner else "Unknown"}
        Type: {farm.type}
        Location: {farm.location or "No location provided"}
        Coordinates: ({farm.latitude}, {farm.longitude})
        Google Sheet URL: {farm.google_sheet_url or "None"}

        """.strip())

    return "\n".join(blocks) + "\n"


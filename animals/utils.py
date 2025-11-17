from pgvector.django import CosineDistance
from django.utils.timezone import now
from decimal import Decimal
from openai import AzureOpenAI
from .models import (
    Animal, AnimalImage, HealthRecord, ProductionData,
    ReproductiveHistory, FeedManagement, FinancialDetails,
    LactationPeriod, LifetimeStats
)
from django.conf import settings


# ---------------- Azure OpenAI Client ----------------
client = AzureOpenAI(
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
)


# ---------------- Embedding Generation ----------------
def generate_animal_embedding(animal):
    """
    Generate embedding for an animal instance (text description)
    """
    text = f"""
    Animal Tag: {animal.tag}
    Name: {animal.name or 'Unknown'}
    Breed: {animal.breed}
    Gender: {animal.gender}
    Farm: {animal.farm.name if animal.farm else 'No Farm'}
    Assigned Worker: {animal.assigned_worker}
    """

    try:
        embedding_model = getattr(settings, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        response = client.embeddings.create(
            model=embedding_model,
            input=text.strip()
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return None


def generate_image_embedding(image_path):
    """
    Generate embedding for an image file
    """
    try:
        embedding_model = getattr(settings, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        with open(image_path, "rb") as f:
            data = f.read()

        response = client.embeddings.create(
            model=embedding_model,
            input=data
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Image embedding failed: {e}")
        return None


# ---------------- Context Builder ----------------
def build_animal_context(animal):
    """
    Build detailed text context for an animal
    """
    context_lines = [
        f"Animal Tag: {animal.tag}",
        f"Name: {animal.name or 'Unknown'}",
        f"Breed: {animal.breed}",
        f"Gender: {animal.gender}",
        f"Category: {animal.category()}",
        f"Sick: {animal.is_sick}",
        f"Pregnant: {animal.is_pregnant}"
    ]

    # Production Data (last 3 records)
    for p in animal.production_data.order_by('-date')[:3]:
        context_lines.append(
            f"Milk yield: {p.milk_yield}L on {p.date}, Session: {p.session}, "
            f"SCC: {p.scc}, Fat%: {p.fat_percentage}, Protein%: {p.protein_percentage}"
        )

    # Health Records (last 3)
    for h in animal.health_records.order_by('-date')[:3]:
        context_lines.append(
            f"Health Record: {h.type} on {h.date}, Sick: {h.is_sick}, Diagnosis: {h.diagnosis or 'N/A'}"
        )

    # Reproductive History (last 2)
    for r in animal.reproductive_history.order_by('-date')[:2]:
        context_lines.append(f"Reproductive Event: {r.event} on {r.date}")

    # Feed Management (last 2)
    for f in animal.feed_management.order_by('-date')[:2]:
        context_lines.append(
            f"Feed: {f.type} {f.quantity}kg, Cost/unit: {f.cost_per_unit}, Total cost: {f.total_cost}"
        )

    # Financial Summary
    if hasattr(animal, 'financial_details'):
        fd = animal.financial_details
        context_lines.append(
            f"Financials: Feed cost {fd.total_feed_cost}, Vet cost {fd.total_vet_cost}, "
            f"Breeding cost {fd.total_breeding_cost}, Milk revenue {fd.total_revenue_from_milk}, "
            f"Total cost {fd.total_cost}"
        )

    # Lactation Periods
    for l in animal.lactation_periods.order_by('-last_calving_date')[:1]:
        context_lines.append(
            f"Lactation {l.lactation_number}: {l.days_in_milk} DIM, "
            f"Milking: {l.is_milking}, Expected calving: {l.expected_calving_date}"
        )

    # Lifetime Stats
    if hasattr(animal, 'lifetime_stats'):
        ls = animal.lifetime_stats
        context_lines.append(
            f"Lifetime Stats: Total milk {ls.total_milk}L, Avg yield {ls.avg_yield}L, Calves {ls.calves}"
        )

    return "\n".join(context_lines)


# ---------------- RAG Retrieval (user-aware) ----------------
def retrieve_similar_animals(query_text, user=None, top_k=None):
    """
    Retrieve animals relevant to a query.
    If top_k is None, returns ALL animals for the user's farms.
    """
    try:
        if user:
            qs = Animal.objects.filter(farm__owner=user)
        else:
            qs = Animal.objects.all()

        # If you still want to use embeddings for ranking, keep this part:
        embedding_model = getattr(settings, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        query_embedding = client.embeddings.create(
            model=embedding_model,
            input=query_text
        ).data[0].embedding

        qs = qs.annotate(distance=CosineDistance('embedding', query_embedding)).order_by('distance')

        if top_k:
            return qs[:top_k]
        return qs  # Return all animals for this user

    except Exception as e:
        print(f"Error retrieving similar animals: {e}")
        return Animal.objects.none()


def retrieve_similar_images(query_image_path, user, top_k=None):
    """
    Retrieve top K images similar to input image, filtered by user's farms
    """
    query_embedding = generate_image_embedding(query_image_path)
    if not query_embedding:
        return AnimalImage.objects.none()

    farms = user.owned_farms.all()

    return AnimalImage.objects.filter(animal__farm__in=farms).annotate(
        distance=CosineDistance('embedding', query_embedding)
    ).order_by('distance')[:top_k]


# ---------------- Chat Query ----------------
# ---------------- Smart Chat Query ----------------
def ask_azure_gpt(user, user_message, query_image_path=None, history=None):
    """
    Ask Azure OpenAI GPT model with farm RAG context, optional image,
    and full conversation memory support.
    """
    try:
        # Step 1: Retrieve all animals for this user
        animals = Animal.objects.filter(farm__owner=user).order_by("tag")
        total_animals = animals.count()

        if total_animals == 0:
            farm_data = "This user currently has no registered animals."
        else:
            context_lines = [build_animal_context(animal) for animal in animals]

            # Step 2: Handle large farms
            if total_animals > 100:
                from django.db.models import Avg

                summary_text = (
                    f"You have {total_animals} animals in your farm.\n"
                    f"• {animals.filter(is_pregnant=True).count()} pregnant\n"
                    f"• {animals.filter(is_sick=True).count()} sick\n"
                    f"• {animals.filter(is_milking=True).count()} milking\n"
                )

                avg_yield = (
                    ProductionData.objects.filter(animal__farm__owner=user)
                    .aggregate(avg=Avg("milk_yield"))
                    .get("avg")
                )

                if avg_yield:
                    summary_text += f"• Avg milk yield: {round(avg_yield, 2)}L/day\n"
                else:
                    summary_text += "• Milk yield data missing\n"

                summary_text += (
                    "\nFor detailed lists, request e.g. 'Show pregnant cows' or 'List sick animals'."
                )
                farm_data = summary_text
            else:
                farm_data = "\n".join(context_lines)

        # Step 3: Handle image if uploaded
        if query_image_path:
            images = retrieve_similar_images(query_image_path)
            for img in images:
                farm_data += (
                    f"\nImage related to: {img.animal.tag} - "
                    f"Caption: {img.caption or 'No caption'}"
                )

        # ---------------- 🧠 Conversation History ----------------
        if history is None or not isinstance(history, list) or len(history) == 0:
            history = [{"role": "user", "content": user_message}]
        else:
            history.append({"role": "user", "content": user_message})

        # 🚨 IMPORTANT: Insert farm data before the conversation
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful farm management assistant. "
                    "Always answer using the farm information provided."
                ),
            },
            {"role": "system", "content": f"Farm Data:\n{farm_data}"},
        ]

        messages.extend(history)

        # Step 4: Send to Azure GPT
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            max_tokens=900,
            temperature=0.4,
        )

        reply = response.choices[0].message.content.strip()

        # Step 5: Add long farm note when needed
        if total_animals > 100:
            reply += (
                "\n\n🧭 Note: Your farm has over 100 animals. "
                "View full records in the app’s Animal List."
            )

        return reply

    except Exception as e:
        import traceback
        print("🔥 Azure GPT Error:", str(e))
        traceback.print_exc()
        return f"GPT Error: {str(e)}"


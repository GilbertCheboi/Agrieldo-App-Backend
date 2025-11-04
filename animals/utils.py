from datetime import datetime
from django.utils.timezone import now
from django.db.models import F
from pgvector.django import CosineDistance
from sentence_transformers import SentenceTransformer
from .models import Animal


# -------------------- Animal Alerts --------------------
def generate_animal_alerts(animal):
    alerts = []

    # High SCC Detected
    if any(record.scc and record.scc > 200 for record in animal.production_data.all()):
        alerts.append("High SCC Detected")

    # Due for Heat Check
    if animal.reproductive_history.exists():
        last_repro = animal.reproductive_history.latest('date').date
        if (now().date() - last_repro).days > 21:
            alerts.append("Due for Heat Check")

    # Low Milk Production
    if hasattr(animal, 'latest_milk_yield') and animal.latest_milk_yield and animal.latest_milk_yield < 10:
        alerts.append("Low Milk Production (< 10L)")

    # Milk Production Dropping
    production_records = animal.production_data.order_by('-date')[:2]
    if production_records.count() == 2:
        latest = production_records[0].milk_yield
        previous = production_records[1].milk_yield
        if latest < previous - 1:
            alerts.append(f"Milk Production Dropping ({round(previous - latest, 1)}L)")

    # Upcoming Calving
    if hasattr(animal, 'lactation_status') and getattr(animal.lactation_status, "expected_calving_date", None):
        edc = animal.lactation_status.expected_calving_date
        days_until = (edc - now().date()).days
        if 0 < days_until <= 30:
            alerts.append(f"Upcoming Calving in {days_until} days ({edc.strftime('%Y-%m-%d')})")
def get_animal_context(user):
    """
    Build a simple text summary of all animals belonging to this user.
    """
    animals = Animal.objects.filter(farm__owner=user)
    if not animals.exists():
        return "No animals found in this user's farm."

    context_lines = ["Farm Animal Data:"]
    for a in animals[:20]:  # limit to 20 to keep prompt short
        context_lines.append(
            f"- Name: {a.name}, Tag: {a.tag}, Breed: {a.breed}, "
            f"Category: {a.category}, Sick: {a.is_sick}, Pregnant: {a.is_pregnant}"
        )
    return "\n".join(context_lines)


def ask_openai(prompt: str, user, model: str = "gpt-4o-mini", max_tokens: int = 400):
    """
    Sends the user's message to OpenAI with farm data context.
    """
    try:
        animal_context = get_animal_context(user)

        messages = [
            {"role": "system", "content": "You are a helpful farm management assistant."},
            {"role": "system", "content": f"Use the following farm data to answer questions:\n{animal_context}"},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "Sorry, I couldn't process that right now."

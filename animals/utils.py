from datetime import datetime
from django.utils.timezone import now

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
    if animal.latest_milk_yield and animal.latest_milk_yield < 10:
        alerts.append("Low Milk Production (< 10L)")

    # Milk Production Dropping
    production_records = animal.production_data.order_by('-date')[:2]
    if production_records.count() == 2:
        latest = production_records[0].milk_yield
        previous = production_records[1].milk_yield
        if latest < previous - 1:
            alerts.append(f"Milk Production Dropping ({round(previous - latest, 1)}L)")

    # Upcoming Calving
    if hasattr(animal, 'lactation_status') and animal.lactation_status.expected_calving_date:
        edc = animal.lactation_status.expected_calving_date
        days_until = (edc - now().date()).days
        if 0 < days_until <= 30:
            alerts.append(f"Upcoming Calving in {days_until} days ({edc.strftime('%Y-%m-%d')})")

    return alerts


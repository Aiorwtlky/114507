# api/services.py

from .models import Trip, AiVisionLog, User

def is_driver_on_active_trip(user: User) -> bool:
    """
    Checks if a given driver (user) is currently on an active trip.
    An active trip is one that has a start_time but no end_time.
    """
    # .exists() is a highly efficient query that only checks for existence.
    return Trip.objects.filter(personnel=user, end_time__isnull=True).exists()


def calculate_trip_score(trip_id: int):
    """
    Calculates the final score for a given trip based on its dangerous events.
    """
    try:
        trip = Trip.objects.get(id=trip_id)
    except Trip.DoesNotExist:
        print(f"[Scoring Service] Error: Trip with id {trip_id} not found.")
        return None

    dangerous_events = AiVisionLog.objects.filter(trip=trip)
    
    total_deductions = 0
    for event_log in dangerous_events:
        if event_log.event and event_log.event.deduction_points:
            total_deductions += event_log.event.deduction_points
    
    final_score = max(0, 100 - total_deductions)
    
    trip.score = final_score
    trip.save(update_fields=['score'])
    
    print(f"行程 {trip_id} 評分計算完成。最終分數: {final_score}")
    
    return { "final_score": final_score }
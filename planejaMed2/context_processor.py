from shifts.models import Center, Month


def global_context(request):
    """
    Adds global context variables to all templates.
    """
    # Get all centers from the database
    centers = Center.objects.all()
    lck_month_exists = Month.objects.filter(is_locked=True).exists()
    
    # Return the context dictionary
    return {
        'centers': centers,
        'current_month_name': Month.get_current().name,
        'lck_month_exists': lck_month_exists,
    }



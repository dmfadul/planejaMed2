from shifts.models import Center


def global_context(request):
    """
    Adds global context variables to all templates.
    """
    # Get all centers from the database
    centers = Center.objects.all()
    
    # Return the context dictionary
    return {
        'centers': centers,
    }



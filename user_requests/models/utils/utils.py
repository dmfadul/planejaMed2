def get_context(req):
    """Return a context dictionary for rendering a request."""
    from vacations.models import Vacation as V

    if req.request_type in V.VacationType.values:
        ctx = {
            'sender_name':  req.requester.name,
            'start_date':  req.start_date.strftime("%d/%m/%y"),
            'end_date':    req.end_date.strftime("%d/%m/%y"),
            'vacation_type': "Férias" if req.get_request_type_display() == "REGULAR" else "Licença Médica",
        }
    else:
        ctx = {
            'sender_name':      req.requester.name,
            'receiver_id':      req.requestee.id if req.requestee else None,
            'requestee_name':   req.requestee.name if req.requestee else "Admin",
            'center':           req.center.abbreviation if req.center else "N/A",
            'date':             req.date.strftime("%d/%m/%y"),
            'start_hour':       f"{req.start_hour:02d}:00",
            'end_hour':         f"{req.end_hour:02d}:00",
            'target_name':      req.target.name if req.target else "open",
            'request_type':     req.get_request_type_display().upper(),
        }

    return ctx


def get_template_key(req):
    """Return the template key for rendering a request."""
    from user_requests.models import UserRequest as UR
    from vacations.models import Vacation as V
    
    if req.request_type == V.VacationType.REGULAR:
        temp_key = f'request_pending_regular_vacation'
    elif req.request_type == V.VacationType.SICK:
        temp_key = f'request_pending_sick_leave'
    elif req.request_type == UR.RequestType.DONATION and (req.audience == UR.Audience.ALL_USERS):
        temp_key = f'request_pending_open_donation_offered'
    elif req.request_type == UR.RequestType.DONATION and (req.donor and req.donor == req.requester):
        temp_key = f'request_pending_donation_offered'
    elif req.request_type == UR.RequestType.DONATION and (req.donee and req.donee == req.requester):
        temp_key = f'request_pending_donation_asked_for'
    elif req.request_type == UR.RequestType.EXCLUDE:
        temp_key = f'request_pending_exclusion'
    elif req.request_type == UR.RequestType.INCLUDE:
        temp_key = f'request_pending_inclusion'
    else:
        temp_key = f'request_pending_{UR.request_type}'

    return temp_key
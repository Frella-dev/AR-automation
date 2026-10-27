def should_send_upcoming_reminder(days_to_due):
    """
    Send reminder only 14 days before due date
    """
    return days_to_due == 14


def should_send_overdue_reminder(days_overdue):
    """
    Overdue reminder should be handled by DB (last sent tracking),
    so this function only checks if invoice is actually overdue.
    """
    return days_overdue > 0
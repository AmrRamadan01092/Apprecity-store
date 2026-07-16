from .models import Announcement

def announcements_processor(request):
    announcements = Announcement.objects.filter(active=True).order_by('-created_at')
    return {
        'active_announcements': announcements
    }

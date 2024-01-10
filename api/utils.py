from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from .models import Notification
from six import text_type


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, join_team, timestamp):
        return text_type(join_team.accepted) + text_type(join_team.user.pk) + text_type(join_team.team.pk) + text_type(timestamp)


# def send_notification(user, content, url=None, updated_chapter=None):
#     Notification.objects.create(user=user, content=content, url=url, updated_chapter=updated_chapter)


token_generator = AppTokenGenerator()

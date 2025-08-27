from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    interests = models.JSONField(default=dict)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def update_interest(self, category, increment=1, decay_factor=0.95):
        current_score = self.interests.get(category, 0)
        updated_interests = {cat: score * decay_factor for cat, score in self.interests.items()}
        updated_interests[category] = current_score + increment
        self.interests = updated_interests
        self.save()
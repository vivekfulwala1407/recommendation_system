from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    interactions = models.JSONField(default=dict)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def record_interaction(self, user, action):
        user_id = str(user.id)
        if user_id not in self.interactions:
            self.interactions[user_id] = {}
        self.interactions[user_id][action] = self.interactions[user_id].get(action, 0) + 1
        if action == 'like':
            self.likes += 1
        elif action == 'comment':
            self.comments += 1
        elif action == 'share':
            self.shares += 1    
        self.save()
        return True

    def get_user_interaction(self, user, action):
        user_id = str(user.id)
        if user_id in self.interactions:
            return self.interactions[user_id].get(action, 0)
        return 0

    def has_user_interacted(self, user, action):
        return self.get_user_interaction(user, action) > 0

    @property 
    def total_engagement(self):
        return self.likes + (self.comments * 2) + (self.shares * 3)
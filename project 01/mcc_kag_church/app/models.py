from django.db import models
from django.utils import timezone

class FirstTimeVisitor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    how_heard = models.CharField(max_length=100, blank=True)
    questions = models.TextField(blank=True)
    visit_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.visit_date}"

from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True)  # Add this line if missing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"
        
class Leadership(models.Model):
    POSITION_CHOICES = [
        ('pastor', 'Pastor'),
        ('elder', 'Elder'),
        ('deacon', 'Deacon'),
        ('staff', 'Staff'),
    ]
    
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    title = models.CharField(max_length=100)
    bio = models.TextField()
    image = models.ImageField(upload_to='leadership/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"
    
class Belief(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
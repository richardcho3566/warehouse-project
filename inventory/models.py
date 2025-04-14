from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    product_name = models.CharField(max_length=100)
    warehouse = models.CharField(max_length=10)
    shelf_number = models.CharField(max_length=10)
    column = models.CharField(max_length=10)
    level = models.CharField(max_length=10)

    @property
    def location_code(self):
        return f"{self.warehouse}-{self.shelf_number}-{self.column}{self.level}"


class Profile(models.Model):
    GRADE_CHOICES = [
        ('GRADE1', 'Grade 1'),
        ('GRADE2', 'Grade 2'),
        ('GRADE3', 'Grade 3'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, default='GRADE1')

    def __str__(self):
        return f"{self.user.username} - {self.grade}"
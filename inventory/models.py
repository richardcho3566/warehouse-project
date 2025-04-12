from django.db import models

class Product(models.Model):
    product_name = models.CharField()
    warehouse = models.CharField()   # 예: A
    shelf_number = models.CharField()          # 예: 03
    column = models.CharField()       # 예: C
    level = models.CharField()                 # 예: 3

    @property
    def location_code(self):
        return f"{self.warehouse}-{self.shelf_number}-{self.column}{self.level}"


    def __str__(self):
        return self.product_name

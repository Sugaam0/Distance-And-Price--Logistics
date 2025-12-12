from django.db import models
from django.core.validators import MinValueValidator

class DeliveryCalculation(models.Model):
    PACKAGE_TYPES = [
        ('document', 'Document'),
        ('standard', 'Standard Package'),
        ('fragile', 'Fragile Items'),
        ('heavy', 'Heavy Items'),
    ]
    
    pickup_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    length = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    width = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    height = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPES, default='standard')
    is_fragile = models.BooleanField(default=False)
    needs_insurance = models.BooleanField(default=False)
    
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.pickup_location} → {self.delivery_location}"
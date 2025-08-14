from django.db import models


import string, random

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

class URL(models.Model):
    long_url = models.URLField()
    clicks = models.IntegerField(default=0)

    short_code = models.CharField(max_length=6, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = generate_code()
        super().save(*args, **kwargs)


# Create your models here.

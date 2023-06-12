from django.db import models

class TalaCategory(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Tala(models.Model):
    name= models.CharField(max_length=128)
    angas = models.CharField(max_length=512)
    aksharas = models.IntegerField(default=0)
    category = models.ForeignKey(TalaCategory, on_delete= models.CASCADE)

    def __str__(self):
        return self.name

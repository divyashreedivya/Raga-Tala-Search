from django.db import models

class Melakarta(models.Model):
    name = models.CharField(max_length= 128)
    num = models.IntegerField(default =0)
    def __str__(self):
        return self.name

class Raga(models.Model):
    name = models.CharField(max_length= 128)
    arohanam = models.CharField(max_length = 256)
    avarohanam = models.CharField(max_length = 256)
    mela_true = models.BooleanField(default= False)
    mela = models.ForeignKey(Melakarta , on_delete= models.CASCADE)

    def __str__(self):
        return self.name


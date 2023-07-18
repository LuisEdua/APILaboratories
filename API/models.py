from django.db import models


# Create your models here.
class Admin(models.Model):
    name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=200)


class Dispositive(models.Model):
    serial_number = models.CharField(max_length=50)
    alias = models.CharField(max_length=50, null=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, null=True)


class Manager(models.Model):
    name = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    dispositive = models.ForeignKey(Dispositive, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)


class Measures(models.Model):
    date = models.DateTimeField()
    lpg = models.DecimalField(max_digits=10, decimal_places=2)
    co = models.DecimalField(max_digits=10, decimal_places=2)
    hydrogen = models.DecimalField(max_digits=10, decimal_places=2)
    humidity = models.DecimalField(max_digits=4, decimal_places=2)
    temperature = models.DecimalField(max_digits=4, decimal_places=2)
    error = models.IntegerField(default=0)
    serial_number_esp32 = models.CharField(max_length=50)
    dispositive = models.ForeignKey(Dispositive, on_delete=models.CASCADE, null=True)

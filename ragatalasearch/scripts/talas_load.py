import csv

from talas.models import Tala, TalaCategory

def run():
    fhand = open('talas/talas.csv',encoding = 'utf-8')
    reader = csv.reader(fhand)
    next(reader)

    Tala.objects.all().delete()
    for row in reader:
        print(row)
        c, created = TalaCategory.objects.get_or_create(name = row[4])
        t = Tala(name= row[1],angas=row[2],aksharas=row[3],category=c)
        t.save()
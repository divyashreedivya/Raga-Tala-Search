import csv

from ragas.models import Raga, Melakarta

def run():
    fhand = open('ragas/ragas.csv', encoding='utf-8')
    reader = csv.reader(fhand)
    next(reader)

    Melakarta.objects.all().delete()
    Raga.objects.all().delete()
    n = 1
    for row in reader:
        print(row)
        r = row[1]
        mt =False
        if(r[0:2].isdigit()):
            r = r[3:]
            m, created = Melakarta.objects.get_or_create(name = r, num = n)
            mt = True
            n+=1
            
        ra = Raga(name = r, arohanam = row[2], avarohanam= row[3],mela_true= mt,  mela= m) 
        ra.save()   


from pro.models import Employes


class Multiposteur(object):

    def get_employees(self, nb):
        nb = int(nb.replace(" ", ""))
        if nb > 0 and nb <= 9:
            return Employes.objects.get(id=2)
        if nb >= 10 and nb <= 49:
            return Employes.objects.get(id=3)
        if nb >= 50 and nb <= 499:
            return Employes.objects.get(id=4)
        if nb >= 500 and nb <= 999:
            return Employes.objects.get(id=5)
        if nb >= 1000 and nb <= 4999:
            return Employes.objects.get(id=6)
        if nb >= 5000:
            return Employes.objects.get(id=1)

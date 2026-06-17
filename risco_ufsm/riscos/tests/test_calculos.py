from django.test import TestCase
from riscos.models import AvaliacaoRisco

class TesteCalculos(TestCase):
    def test_risco_inerente(self):
        # prob=3, impacto=4 -> inerente=12
        a = AvaliacaoRisco(probabilidade=3, impacto=4, eficacia_controles='MEDIANO')
        a.save()
        self.assertEqual(a.risco_inerente, 12)

    def test_nivel_alto(self):
        self.assertEqual(AvaliacaoRisco.calcular_nivel(12), 'ALTO')
        self.assertEqual(AvaliacaoRisco.calcular_nivel(19), 'ALTO')

    def test_nivel_extremo(self):
        self.assertEqual(AvaliacaoRisco.calcular_nivel(20), 'EXTREMO')

    def test_risco_residual_forte(self):
        a = AvaliacaoRisco(probabilidade=5, impacto=5, eficacia_controles='FORTE')
        a.save()
        # inerente=25, fator=0.2 -> residual=5.0
        self.assertEqual(a.risco_residual, 5.0)
        self.assertEqual(a.nivel_residual, 'MODERADO')
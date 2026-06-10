'''Admin registra plano de risco, identificação, avaliação e tratamento'''

from django.contrib import admin
from .models import PlanoDeRisco, IdentificacaoRisco, AvaliacaoRisco, TratamentoRisco

admin.site.register(PlanoDeRisco)
admin.site.register(IdentificacaoRisco)
admin.site.register(AvaliacaoRisco)
admin.site.register(TratamentoRisco)

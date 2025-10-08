from django.contrib import admin
from Atividades.models import TipoEquipamento

# Register your models here.
@admin.register(TipoEquipamento)
class TipoEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('idEquipamento', 'descricao')
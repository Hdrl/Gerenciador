from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.admin.sites import site
from .models import Viagem, TransacaoFinanceira
import locale
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django import forms
from .relatorio import gerar_relatorio_viagem
from .services import extrair_url_selecionada, extrair_url
from datetime import datetime


locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class TransacaoFinanceiraForm(forms.ModelForm):
    class Meta:
        model = TransacaoFinanceira
        fields = '__all__'
        widgets = {
            # Mantendo sua configuração do accept que funcionou
            'imagem': forms.ClearableFileInput(attrs={'accept': '*/*'})
        }

class TransacaoFinanceiraInline(admin.TabularInline):
    model = TransacaoFinanceira
    fk_name = 'viagem'
    fields = ('valor', 'tipo')
    extra = 1
    verbose_name_plural = "Transações Financeiras"

class UserViagensFilter(admin.SimpleListFilter):
    title = "Viagens"
    parameter_name = "viagem"
    
    def lookups(self, request, model_admin):
        viagens = []
        # Otimizado para filtrar direto na query em vez de loop python
        qs = Viagem.objects.filter(usuario=request.user)
        for viagem in qs:
            viagens.append((viagem.id, str(viagem)))
        return viagens
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(viagem=self.value())
        return queryset
    
class UserFilteredAdmin(admin.ModelAdmin):
    """
    Admin base que filtra objetos pelo usuário logado.
    Superusuários veem tudo.
    """
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            self.exclude = ['usuario']
        return qs.filter(usuario=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        obj.save()

    def has_change_permission(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return True
        return obj.usuario == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return True
        return obj.usuario == request.user
        
@admin.register(Viagem)
class ViagemAdmin(UserFilteredAdmin):
    actions = [gerar_relatorio_viagem]
    inlines = [TransacaoFinanceiraInline,]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, TransacaoFinanceira):
                if not instance.pk or not instance.usuario_id:
                    instance.usuario = request.user
            instance.save()
        formset.save_m2m()  
          
@admin.register(TransacaoFinanceira)
class TransacaoFinanceiraAdmin(UserFilteredAdmin):
        ordering=['-data']
        list_display = ['descricao', 'data', 'valor', 'viagem']
        list_filter = [UserViagensFilter] # Seu filtro customizado
        actions = [extrair_url_selecionada]
        change_list_template = 'admin/viagens/transacaofinanceira/change_list.html'
        exclude = ['usuario']
        form = TransacaoFinanceiraForm

        # --- NOVO MÉTODO ADICIONADO AQUI ---
        def changelist_view(self, request, extra_context=None):
            # Verifica se não há filtros na URL (request.GET vazio)
            # E verifica se não estamos vindo de uma edição/salvamento (para não atrapalhar o fluxo)
            if not request.GET and '/change/' not in request.META.get('HTTP_REFERER', ''):
                
                # Busca a última viagem DO USUÁRIO ATUAL
                if request.user.is_superuser:
                    ultima_viagem = Viagem.objects.order_by('-id').first()
                else:
                    ultima_viagem = Viagem.objects.filter(usuario=request.user).order_by('-id').first()

                if ultima_viagem:
                    # Cria uma cópia dos parâmetros GET para modificar
                    q = request.GET.copy()
                    # Adiciona o filtro da viagem (usando o ID exato)
                    q['viagem'] = ultima_viagem.id
                    
                    # Redireciona para a mesma página, agora com o filtro aplicado
                    return redirect(request.path + '?' + q.urlencode())

            return super().changelist_view(request, extra_context)
        # -----------------------------------

        def get_urls(self):
            urls = super().get_urls()
            custom_urls = [
                path('qrcode/', self.admin_site.admin_view(self.qrcode_view), name='qrcode_view'),
            ]
            return custom_urls + urls
        
        @csrf_exempt
        def qrcode_view(self, request):
            model_admin = site._registry[Viagem]
            context = {
                'opts': Viagem._meta,
                'app_label': Viagem._meta.app_label,
                'has_permission': True,
                'title': 'QR Code das Viagens',
                'media': model_admin.media,
                'cl': None,
            }

            if request.method == "POST":
                url = request.POST.get("url")
                request.session['url_qrcode'] = url
                return redirect('admin:viagens_transacaofinanceira_add')
            return render(request, 'admin/viagens/transacaofinanceira/qrcode.html', context)

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            if db_field.name == "viagem":
                if request.user.is_superuser:
                    kwargs["queryset"] = Viagem.objects.all()
                else:
                    kwargs["queryset"] = Viagem.objects.filter(usuario=request.user)
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        def get_changeform_initial_data(self, request):
            initial = super().get_changeform_initial_data(request)
            
            # Ajustado para pegar a última viagem do usuário logado também
            if request.user.is_superuser:
                ultima_viagem = Viagem.objects.order_by('-id').first()
            else:
                ultima_viagem = Viagem.objects.filter(usuario=request.user).order_by('-id').first()
                
            dados = request.session.pop('url_qrcode', None)
            
            # Removemos a linha "data_criacao = datetime.now" solta que não fazia nada
            
            if ultima_viagem:
                initial['viagem'] = ultima_viagem

            if dados:
                transacao = extrair_url(dados)
                initial['nota_fiscal'] = dados
                initial['descricao'] = transacao.get('descricao', '')
                initial['valor'] = transacao.get('valor', '')
                # Se extrair_url retornar string, certifique-se que o formato é compatível
                initial['data'] = transacao.get('data', '')
            return initial

admin.site.site_header = "Administração Viagem"
admin.site.site_title = "Administração Viagem"
admin.site.index_title = "Bem-vindo ao painel"
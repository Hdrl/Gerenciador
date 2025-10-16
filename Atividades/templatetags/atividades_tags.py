from django import template

register = template.Library()

@register.filter
def get_attribute(obj, attr_name):
    """
    Permite acessar o atributo de um objeto usando uma string com o nome do atributo.
    Exemplo: {{ meu_objeto|get_attribute:"nome" }}
    Retorna '' (string vazia) se o atributo não existir, para evitar erros.
    """
    return getattr(obj, attr_name, '')

@register.filter
def get_display(obj, attr_name):
    """
    Tenta chamar o método get_<attr_name>_display() para campos com 'choices'.
    Se não conseguir, retorna o valor do atributo normalmente.
    """
    # Tenta encontrar o método get_FOO_display
    display_method_name = f'get_{attr_name}_display'
    
    if hasattr(obj, display_method_name):
        # Se encontrou, chama o método e retorna seu valor
        return getattr(obj, display_method_name)()
    else:
        # Se não, retorna o valor do atributo diretamente
        return getattr(obj, attr_name, '')
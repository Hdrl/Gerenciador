class ModelManager:
    def __init__(self, model):
        self.model = model

    def listar(self):
        self.field_list = []
        self.field_headers = []
        for field in self.model._meta.get_fields():
            try:
                self.field_headers.append(field.verbose_name)
                self.field_list.append(field.name)
            except Exception:
                pass

        return {
            'querys': self.model.objects.all(),
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
            'field_headers': self.field_headers,
            'field_names': self.field_list,
            'link_adcionar': '#',
        }
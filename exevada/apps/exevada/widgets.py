from django import forms
from django.contrib.gis.geos import Polygon, MultiPolygon


class AreaInput(forms.MultiWidget):
    """DUMMY DOCSTRING"""

    def __init__(self, attrs=None):
        if attrs:
            attrs['required'] = False
        else:
            attrs = {'required': False}
        print('ATTRS', attrs)
        widgets = [forms.TextInput, forms.ClearableFileInput, forms.Textarea]
        super().__init__(widgets, attrs=attrs)

    def get_context(self, name, value, attrs):
        print(name)
        print(value)
        print(attrs)
        if attrs:
            attrs['required'] = False
        else:
            attrs = {'required': False}
        context = super().get_context(name, value, attrs)
        context['widget']['required'] = False
        print('CONTEXT', context)
        return context

    def decompress(self, value):
        print('VALUE', value)
        return [None, None, value]

    def value_from_datadict(self, data, files, name):
        print(data)
        print(files)
        print(name)
        mp = MultiPolygon([
            Polygon( ((0, 0), (0, 1), (1, 1), (0, 0)) ),
            Polygon( ((1, 1), (1, 2), (2, 2), (1, 1)) ),
        ])
        return mp


class ShapeInput(forms.TextInput):
    """DUMMY DOCSTRING"""
    template_name = 'templates/forms/widgets/shape.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        final_attrs = context['widget']['attrs']
        id_ = context['widget']['attrs'].get('id')

        subwidgets = []
        for index, value_ in enumerate(context['widget']['value']):
            widget_attrs = final_attrs.copy()
            if id_:
                # An ID attribute was given. Add a numeric index as a suffix
                # so that the inputs don't all have the same ID attribute.
                widget_attrs['id'] = '%s_%s' % (id_, index)
            widget = HiddenInput()
            widget.is_required = self.is_required
            subwidgets.append(widget.get_context(name, value_, widget_attrs)['widget'])

        context['widget']['subwidgets'] = subwidgets
        return context

    def value_from_datadict(self, data, files, name):
        try:
            getter = data.getlist
        except AttributeError:
            getter = data.get
        return getter(name)

    def format_value(self, value):
        return [] if value is None else value

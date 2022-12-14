from django import forms
from django.utils.translation import ugettext_lazy as _

from .settings import setting_match_all_default_value


class AdvancedSearchForm(forms.Form):
    _match_all = forms.BooleanField(
        label=_('Match all'), help_text=_(
            'When checked, only results that match all fields will be '
            'returned. When unchecked results that match at least one field '
            'will be returned.'
        ), required=False
    )

    def __init__(self, *args, **kwargs):
        kwargs['data'] = kwargs['data'].copy()
        kwargs['data']['_match_all'] = setting_match_all_default_value.value
        self.search_model = kwargs.pop('search_model')
        super().__init__(*args, **kwargs)

        for search_field in self.search_model.get_search_fields():
            self.fields[search_field.field] = forms.CharField(
                help_text=search_field.get_help_text(),
                label=search_field.label, required=False
            )


class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=128, label=_('Search terms'), required=False
    )

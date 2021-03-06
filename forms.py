# -*- coding: utf-8 -*-
import uuid
import string
from django import forms
from django.conf import settings
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from random import choice
from gfkajax.widgets import GfkCtWidget, GfkFkWidget

def make_GfkAjaxForm(whitelist=None, additional_fields=None):
    """
    Form factory, needed because we have to pass the whitelist to
    the widget.
    """
    class GfkAjaxForm(forms.ModelForm):

        def __init__(self, *args, **kwargs):
            super(GfkAjaxForm, self).__init__(*args, **kwargs)

            # If additional fields needed on form generation, they can
            # be passed. Example: http://code.google.com/p/django-ajax-selects/
            # (see bottom of example section)
            if additional_fields:
                self.fields.update(additional_fields)

            obj = getattr(self, 'instance', None)

            gfk_fields = []

            virtual_fields = getattr(obj.__class__._meta, 'virtual_fields', [])
            for virtual_field  in virtual_fields:
                if isinstance(virtual_field, GenericForeignKey):

                    ct_field_obj = getattr(
                        obj.__class__, virtual_field.ct_field, None
                    )

                    gfk_fields.append({
                        'verbose_name': getattr(ct_field_obj.field, 'verbose_name'),
                        'ct_field': {
                            'name': virtual_field.ct_field,
                            'value': getattr(obj, virtual_field.ct_field)
                        },
                        'fk_field': {
                            'name': virtual_field.fk_field,
                            'value': getattr(obj, virtual_field.fk_field)
                        }
                    })

            self.gfk_fields = gfk_fields

            # Generate pseudo-unique id for this form
            rnd = ''.join([choice(string.letters[:26]) for a in range(8)])
            unique_form_id = 'form_%s' % rnd

            # Now replace widgets
            for field in gfk_fields:

                self.fields[field['ct_field']['name']].widget = GfkCtWidget(
                    whitelist=whitelist,
                    unique_form_id = unique_form_id
                )

                self.fields[field['ct_field']['name']].label = field['verbose_name']

                self.fields[field['fk_field']['name']].widget = GfkFkWidget(
                    unique_form_id = unique_form_id,
                    append_input_name = u'%s_value' % field['ct_field']['name'],
                    append_input_value = field['fk_field']['name'],
                )
                self.fields[field['fk_field']['name']].label = ''
    return GfkAjaxForm


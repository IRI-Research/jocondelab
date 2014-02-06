# -*- coding: utf-8 -*-
#
# Copyright Institut de Recherche et d'Innovation © 2014
#
# contact@iri.centrepompidou.fr
#
# Ce code a été développé pour un premier usage dans JocondeLab, projet du 
# ministère de la culture et de la communication visant à expérimenter la
# recherche sémantique dans la base Joconde
# (http://jocondelab.iri-research.org/).
#
# Ce logiciel est régi par la licence CeCILL-C soumise au droit français et
# respectant les principes de diffusion des logiciels libres. Vous pouvez
# utiliser, modifier et/ou redistribuer ce programme sous les conditions
# de la licence CeCILL-C telle que diffusée par le CEA, le CNRS et l'INRIA 
# sur le site "http://www.cecill.info".
#
# En contrepartie de l'accessibilité au code source et des droits de copie,
# de modification et de redistribution accordés par cette licence, il n'est
# offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
# seule une responsabilité restreinte pèse sur l'auteur du programme,  le
# titulaire des droits patrimoniaux et les concédants successifs.
#
# A cet égard  l'attention de l'utilisateur est attirée sur les risques
# associés au chargement,  à l'utilisation,  à la modification et/ou au
# développement et à la reproduction du logiciel par l'utilisateur étant 
# donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
# manipuler et qui le réserve donc à des développeurs et des professionnels
# avertis possédant  des  connaissances  informatiques approfondies.  Les
# utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
# logiciel à leurs besoins dans des conditions permettant d'assurer la
# sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
# à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 
#
# Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
# pris connaissance de la licence CeCILL-C, et que vous en avez accepté les
# termes.
#
'''
Created on Jun 13, 2013

@author: ymh
'''
from core.models import (Thesaurus, Term, TERM_URL_STATUS_CHOICES_TRANS, 
    TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES_TRANS)
from django.forms import Form, fields, ModelChoiceField
from django.forms.util import flatatt
from django.forms.widgets import (Widget, Select, 
    NullBooleanSelect as DjangoNullBooleanSelect)
from django.utils import formats
from django.utils.encoding import force_text
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ugettext_lazy
from jocondelab import settings
import json


class ThesaurusTreeWidget(Widget):
    
    def _format_value(self, value):
        if self.is_localized:
            return formats.localize_input(value)
        return value

    def render(self, name, value, attrs=None):
        term = None
        if isinstance(value, Term):
            term = value
        elif value and isinstance(value, (int, basestring)):
            terms = list(Term.objects.filter(id=int(value)))  # @UndefinedVariable
            if terms:
                term = terms[0]

        final_attrs = self.build_attrs(attrs, type="hidden", name=name)
        if term is not None:
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_text(self._format_value(term.id))
            final_attrs['data-term_tree_node'] = mark_safe(json.dumps({'id': term.id, 'label': escape(term.label)}).replace("\"", "'"));
        input_res = format_html('<input{0} />', flatatt(final_attrs))
                
        if term is not None:
            dialog_text = term.label
        else:
            dialog_text = _("Open Dialog")
            
        dialog_res = "<div id=\"dialog-link-container\" class=\"ui-state-default ui-corner-all\"><a href=\"#\" id=\"dialog-link\" title=\"%s\">%s</a><span class=\"ui-icon ui-icon-closethick\" id=\"dialog-deselect\"></span></div>" % (_("Open Dialog"),dialog_text)
        
        return input_res + dialog_res

class NullBooleanSelect(DjangoNullBooleanSelect):
    """
    A Select Widget intended to be used with NullBooleanField.
    """
    def __init__(self, attrs=None):
        choices = (('1', ('---')),
                   ('2', ugettext_lazy('yes')),
                   ('3', ugettext_lazy('no')))
        Select.__init__(self, attrs, choices)


class ValidateTermForm(Form):
    term_id = fields.IntegerField(required=True)
    validation_val = fields.BooleanField(required=False)

class WikipediaEditionForm(Form):
    term_id = fields.IntegerField(required=True)
    wikipedia_edition = fields.BooleanField(required=False)
    
class ModifyWpLinkForm(Form):
    term_id = fields.IntegerField(required=True)
    label = fields.CharField(required=True, min_length=1)
    wp_lang = fields.ChoiceField(label=_('Wikipedia version'), required=False, choices=tuple([(k,k) for k in settings.WIKIPEDIA_URLS]))

class LinkSemanticLevelForm(Form):
    term_id = fields.IntegerField(required=True)
    link_semantic_level = fields.IntegerField(required=True)

class RemoveWpLinkForm(Form):
    term_id = fields.IntegerField(required=True)
         
class TermFilterForm(Form):
    thesaurus = ModelChoiceField(label=_("thesaurus"), required=False, queryset=Thesaurus.objects.all().order_by('label'))
    thesaurus_tree = ModelChoiceField(label=_("thesaurus tree"), queryset=Term.objects.all(), required=False, widget=ThesaurusTreeWidget)  # @UndefinedVariable
    label = fields.CharField(label=_("label"), required=False)
    link_status = fields.TypedChoiceField(label=_("link_status"), required=False, empty_value=-1, coerce=int, choices=tuple([(-1,'---------')]+[(v, l) for v,l in TERM_URL_STATUS_CHOICES_TRANS]))
    link_semantic_level = fields.TypedChoiceField(label=_("link_semantic_level"), required=False, empty_value=0, coerce=int, choices=TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES_TRANS)
    wikipedia_edition = fields.NullBooleanField(label=_("wikipedia_edition"), required=False, widget=NullBooleanSelect)
    validated = fields.NullBooleanField(label=_("validated"), required=False, widget=NullBooleanSelect)
    order_by = fields.ChoiceField(label=_("order_by"), required=False, choices=(('normalized_label',_('label')),('nb_notice',_('nb notice')),('level',_('level')),('lft', _('order_lft'))))
    order_dir = fields.ChoiceField(label=_("order_dir"), required=False, choices=(('asc',_('asc')), ('desc',_('desc'))))
    
    def __init__(self, *args, **kwargs):
        super(TermFilterForm, self).__init__(*args, **kwargs)
        if self.data.get('order_by', 'normalized_label') == 'lft':        
            self.fields['order_dir'].widget.attrs['disabled'] = 'disabled'
            
    def clean(self):
        fields_not_empty = any([v for k,v in self.cleaned_data.items() if k not in ('thesaurus','thesaurus_tree', 'link_status', 'order_by', 'order_dir')] + [self.cleaned_data.get('link_status', -1) >= 0])
        self.can_display_level = (not fields_not_empty) and (self.cleaned_data.get('thesaurus',None) is not None) and (self.cleaned_data.get('order_by','normalized_label') == 'lft')
        self.selected_thesaurus = self.cleaned_data.get('thesaurus', None) 
        return super(TermFilterForm, self).clean()
        
    
    def get_filter_qs(self, base_qs=None):
        qs = base_qs
        
        if qs is None:
            qs = Term.objects.all()  # @UndefinedVariable
                
        thes = self.cleaned_data.get('thesaurus',None)
        if thes:
            qs = qs.filter(thesaurus=thes)

        thes_tree = self.cleaned_data.get('thesaurus_tree',None)
        if thes_tree:
            qs = qs & thes_tree.get_descendants()  # @UndefinedVariable

        lk_status = self.cleaned_data.get('link_status',-1)
        if lk_status>=0:
            qs = qs.filter(url_status=lk_status)
            
        lk_semantic_level = self.cleaned_data.get('link_semantic_level', 0)
        if lk_semantic_level:
            qs = qs.filter(link_semantic_level=lk_semantic_level)            
            
        validated = self.cleaned_data.get('validated', None)
        if validated is not None:
            qs = qs.filter(validated=validated)
            
        wikipedia_edition = self.cleaned_data.get('wikipedia_edition', None)
        if wikipedia_edition is not None:
            qs = qs.filter(wikipedia_edition=wikipedia_edition)
            
        label_regexp = self.cleaned_data.get('label', None)
        if label_regexp:
            qs = qs.filter(label__iregex=label_regexp)
        
        order_by = self.cleaned_data.get('order_by', 'normalized_label') or 'normalized_label'
        order_dir = self.cleaned_data.get('order_dir', 'asc') or 'asc'
        if order_dir == 'desc':
            dir_order_by = "-"+order_by
        else:
            dir_order_by = order_by
        if order_by == "normalized_label" or order_by == "label":
            order_by = [dir_order_by, 'nb_notice', 'id']
        elif order_by == "lft":
            order_by = ['tree_id', order_by, 'nb_notice', 'id']
        else:
            order_by = [dir_order_by, 'normalized_label', 'id']
        qs = qs.order_by(*order_by)
        
        return qs
    

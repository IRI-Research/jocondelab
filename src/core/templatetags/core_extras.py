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
Created on Jun 14, 2013

@author: ymh

Reminder :
You need to have the request context processor.

TEMPLATE_CONTEXT_PROCESSORS = (
...
'django.core.context_processors.request',
...
)

'''

from django import template
from .utils import easy_tag

register = template.Library()


class AppendParamNode(template.Node):
    def __init__(self, *params):
        
        self.dict_pairs = {}
        for dict_str in params:        
            if dict_str:
                for pair in dict_str.split(','):
                    pair = pair.split('=')
                    self.dict_pairs[pair[0]] = template.Variable(pair[1])
            
    def render(self, context):
        get = context['request'].GET.copy()

        for key in self.dict_pairs:
            get[key] = self.dict_pairs[key].resolve(context)
        
        path = ""
        if len(get):
            path = get.urlencode()
        
        return "?"+path if path else ""

@register.tag()
@easy_tag
def append_to_param(_tag_name, *params):
    return AppendParamNode(*params)


class HiddenParamFilterForm(template.Node):
    
    def __init__(self, form_var, *excluded_fields):
        self.form = template.Variable(form_var)
        self.excluded_fields = [template.Variable(f) for f in excluded_fields]
        
    def render(self, context):
        form = self.form.resolve(context)
        excluded_fields = [f.resolve(context) for f in self.excluded_fields]
        term_filter_hidden = dict([(k,v) for k,v in context['request'].GET.items() if k not in form.fields and v is not None and k not in excluded_fields])
        form_hidden_inputs = ""
        for name, value in term_filter_hidden.items():
            form_hidden_inputs += "<input type=\"hidden\" name=\"%s\" value=\"%s\"/>" % (name, value.replace("\"", "\\\""))

        return form_hidden_inputs
    
@register.tag()
@easy_tag
def hidden_param_filter(_tag_name, form_var, *excluded_fields):
    return HiddenParamFilterForm(form_var, *excluded_fields)


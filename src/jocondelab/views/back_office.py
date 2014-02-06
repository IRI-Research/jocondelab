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
Created on Jun 12, 2013

@author: ymh
'''

from jocondelab.forms import (ModifyWpLinkForm, ValidateTermForm, RemoveWpLinkForm, 
    TermFilterForm)
from jocondelab.utils import JocondePaginator
from collections import OrderedDict
from core.models import Term, TERM_URL_STATUS_DICT
from core.models.term import (TERM_WK_LINK_SEMANTIC_LEVEL_DICT, 
    TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES)
from core.wp_utils import process_term as wp_process_term
from django.conf import settings
from django.db.models import Count
from django.http.response import HttpResponse, HttpResponseForbidden
from django.views.generic import ListView, DetailView, View
from django.views.generic.list import MultipleObjectMixin
from jocondelab.forms import WikipediaEditionForm, LinkSemanticLevelForm
import json
import logging
import urllib

logger = logging.getLogger(__name__)

class TermListView(ListView):
    
    queryset = Term.objects.select_related()  # @UndefinedVariable
    paginate_by = settings.TERM_LIST_PAGE_SIZE
    paginator_class = JocondePaginator
    template_name = "jocondelab/term_list.html"
    filter_form_class = TermFilterForm
    
    def get_filter_form(self):
        initial = { 'order_by':'label',
                    'order_dir': 'asc',
                    'thesaurus': None,
                    'label': None,
                    'link_status': -1,
                    'validated': None}
        return self.filter_form_class(self.request.GET, initial=initial, auto_id=True)
    
    def get_context_data(self, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        filter_form = self.get_filter_form()
        context['filter_form'] = filter_form
        valid_thesaurus_ids = [entry['thesaurus__id'] for entry in Term.objects.root_nodes().values('thesaurus__id').annotate(root_nodes_count=Count('thesaurus__id')).order_by().filter(root_nodes_count__lt=settings.JOCONDE_TERM_TREE_MAX_ROOT_NODE)]  # @UndefinedVariable
        context['term_tree_valid_thesaurus'] = json.dumps(valid_thesaurus_ids)
        if self.selected_thesaurus and self.can_display_level:
            if self.selected_thesaurus.id in valid_thesaurus_ids:
                context['show_levels'] = True
            else:
                context['show_levels'] = False
        else:
            context['show_level'] = False        
        return context
    
    def get_queryset(self):
        qs = super(TermListView, self).get_queryset()
        filter_form = self.get_filter_form()
        if filter_form.is_valid():
            self.can_display_level = filter_form.can_display_level
            self.selected_thesaurus = filter_form.selected_thesaurus 
            return filter_form.get_filter_qs(qs)
        else:
            self.can_display_level = False            
            self.selected_thesaurus = None
            return None

class TermListTableView(TermListView):
    
    template_name = "jocondelab/partial/term_list_table.html"
    
    

class TermEditView(DetailView, MultipleObjectMixin):
    
    queryset = Term.objects.select_related()  # @UndefinedVariable
    pk_url_kwarg = "term_id"
    context_object_name = "term"
    template_name = "jocondelab/term_edit.html"
    filter_form_class = TermFilterForm
    model = Term
    paginate_by = settings.TERM_LIST_PAGE_SIZE
    paginator_class = JocondePaginator

    def get_object(self, queryset=None):
        
        if queryset is None:
            queryset = self.queryset 
        
        return DetailView.get_object(self, queryset)

    def get_queryset(self):
        qs = self.queryset._clone()
        filter_form = self.get_filter_form()
        if filter_form.is_valid():
            self.can_display_level = filter_form.can_display_level
            self.selected_thesaurus = filter_form.selected_thesaurus
            return filter_form.get_filter_qs(qs)
        else:
            self.can_display_level = False
            self.selected_thesaurus = None
            return None

    
    def get_filter_form(self):
        initial = { 'order_by':'label',
                    'order_dir': 'asc',
                    'thesaurus': None,
                    'label': None,
                    'link_status': -1,
                    'validated': None}
        return self.filter_form_class(self.request.GET, initial=initial, auto_id=True)

    
    def get_context_data(self, **kwargs):        
        
        self.object_list = self.get_queryset()
        if kwargs is None :
            kwargs = {}
        kwargs['object_list'] = self.object_list         

        # Beware: because of multiple inheritance this call MultipleObjectMixin.get_context_data(self, **context)
        context = DetailView.get_context_data(self, **kwargs)
        
        context['notices'] = self.object.notices.select_related().all().prefetch_related('images')[:10]
        context['ancestors'] = self.object.get_ancestors(ascending=True)
                 
        context['filter_form'] = self.get_filter_form()
        context['link_semantic_level_choice'] = TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES
        context['JOCONDE_IMAGE_BASE_URL'] = settings.JOCONDE_IMAGE_BASE_URL
        context['JOCONDE_NOTICE_BASE_URL'] = settings.JOCONDE_NOTICE_BASE_URL
        context['wikipedia_lang_list'] = settings.WIKIPEDIA_URLS.keys()
        context['wikipedia_urls'] = json.dumps(settings.WIKIPEDIA_URLS)
        
        valid_thesaurus_ids = [entry['thesaurus__id'] for entry in Term.objects.root_nodes().values('thesaurus__id').annotate(root_nodes_count=Count('thesaurus__id')).order_by().filter(root_nodes_count__lt=settings.JOCONDE_TERM_TREE_MAX_ROOT_NODE)]  # @UndefinedVariable
        context['term_tree_valid_thesaurus'] = json.dumps(valid_thesaurus_ids)
        if self.selected_thesaurus and self.can_display_level:
            if self.selected_thesaurus.id in valid_thesaurus_ids:
                context['show_levels'] = True
            else:
                context['show_levels'] = False
        else:
            context['show_level'] = False        

        
        field_index = {
            'DOMN' : 1,
            'AUTR' : 3,
            'ECOL' : 4,
            'REPR' : 5,
            'PERI' : 6,
            'EPOQ' : 6,
            'LIEUX': 4,
            'SREP' : 9
        }[self.object.thesaurus.label]
        
        field_name = {
            'SREP' :  u"Source sujet représenté"
        }.get(self.object.thesaurus.label, self.object.thesaurus.label) 

        encoded_label = self.object.label.encode('latin1') if self.object.label is not None else ""
        
        context['encoded_term_label_query_parameter'] = urllib. urlencode({
                'FIELD_%d' % field_index: field_name.encode('latin1'),
                'VALUE_%d' % field_index: encoded_label}).replace('+','%20')
                
        #prev_id, nex_id, prev_page, next_page
        page = context['page_obj']
        
        prev_id = None
        prev_page = 0
        next_id = None
        next_page = 0
        
        
        object_list_ids = [obj.id for obj in list(page.object_list)]
        
        if self.object.id in object_list_ids:
            current_index = object_list_ids.index(self.object.id)

            if current_index > 0:
                prev_id = object_list_ids[current_index-1]
                prev_page = page.number
            elif page.has_previous():
                prev_page = page.previous_page_number()
                prev_id = page.paginator.object_list[page.start_index() - 2].id
    
            if current_index < (len(page)-1):
                next_id = object_list_ids[current_index+1]
                next_page = page.number
            elif page.has_next():
                next_page = page.next_page_number()
                next_id = page.paginator.object_list[page.end_index()].id
        

        context.update({
            'prev_id': prev_id,
            'prev_page': prev_page,
            'next_id': next_id,
            'next_page': next_page
        })
                

        return context 
        
        
    
class TermUpdateView(View):
    
    form_class = None
    http_method_names = ['post']
    
    def __init__(self, **kwargs):
        View.__init__(self, **kwargs)
        self.form = None
        self.form_values = None
        self.term = None
    
    def post(self, request, *args, **kwargs):
        self.form = self.form_class(request.POST)
        if not self.form.is_valid():
            return HttpResponse("Parameters not valid : %s" % (self.form.cleaned_data), status=400)
        
        self.form_values = self.form.cleaned_data
        
        try:
            self.term = Term.objects.get(id=self.form_values['term_id'])  # @UndefinedVariable
        except Term.DoesNotExist:  # @UndefinedVariable
            return HttpResponse("Term %d not found" % self.form_values['term_id'],status=404)

        return self.process_term(request)

    def process_term(self, request):
        raise NotImplemented()


class TermValidate(TermUpdateView):
    
    form_class = ValidateTermForm
    
    def process_term(self, request):
        if self.form_values['validation_val']:
            self.term.validate(request.user)            
        else:
            self.term.unvalidate()

        return HttpResponse(status=204)


class TermRemoveWpLink(TermUpdateView):

    form_class = RemoveWpLinkForm
    
    def process_term(self, request):
                        
        self.term.wp_label = None
        self.term.wp_alternative_label = None
        self.term.alternative_wikipedia_url = None
        self.term.alternative_wikipedia_pageid = None
        self.term.wikipedia_url =None
        self.term.wikipedia_pageid = None
        self.term.dbpedia_uri = None
        self.term.wikipedia_revision_id = None
        self.term.url_status = TERM_URL_STATUS_DICT["unsemantized"]
        self.term.link_semantic_level = TERM_WK_LINK_SEMANTIC_LEVEL_DICT['--']
        
        self.term.save()
                
        return HttpResponse(status=204)



class TermModifyWpLink(TermUpdateView):    
    
    form_class = ModifyWpLinkForm
        
    def process_term(self, request):
        
        label = self.form_values['label']
        wp_lang = self.form_values['wp_lang']
                
        wp_process_term(None, self.term, wp_lang, label=label)
        
        return HttpResponse(status=204)


class TermWikipediaEdition(TermUpdateView):    
    
    form_class = WikipediaEditionForm
        
    def process_term(self, request):
        
        self.term.wikipedia_edition = self.form_values['wikipedia_edition']
        self.term.save()
        
        return HttpResponse(status=204)
 
class TermLinkSemanticLevelEdition(TermUpdateView):

    form_class = LinkSemanticLevelForm
     
    def process_term(self, request):
        
        self.term.link_semantic_level = self.form_values['link_semantic_level']
        self.term.save()
        
        return HttpResponse(status=204)
       
class ThesaurusTree(View):
    http_method_names = ['get']
    
    def get_node_data(self, node, children_count, selected_node_ancestors):
        res = {
        'data' : {
           'title': node.label if node.is_leaf_node() else "%s (%d)"%(node.label, node.get_descendant_count()),
           'attr' : {'id': 'node-term-a-%d' % node.id, 'class': 'term-tree-node'},
           'icon' : 'folder'
          },
          'attr' : { "id" : 'node-term-%d' % node.id, 'rel': 'leaf' if node.is_leaf_node() else 'default'},
          'metadata': {'term_tree_node': {'id': node.id, 'node_id':'node-term-%d' % node.id,'label': node.label, 'children_count': children_count, 'descendants': node.get_descendant_count()}},                      
        }
        
        if node.id in selected_node_ancestors:
            res['state'] = 'open'
            children = node.get_children()
            children_counts = dict([(n.get('id',0),n.get('nb_children',0)) for n in children.values("id").annotate(nb_children=Count("children"))])
            res['children'] = [ self.get_node_data(c,children_counts.get(c.id,0),selected_node_ancestors) for c in children]
        elif not node.is_leaf_node() and children_count <= settings.JOCONDE_TERM_TREE_MAX_CHILDREN:
            res['state'] = 'closed'
        elif not node.is_leaf_node():
            children_with_descendants_count = node.children_with_descendants.count() 
            if children_with_descendants_count > 0 and  children_with_descendants_count <= settings.JOCONDE_TERM_TREE_MAX_CHILDREN:
                res['state'] = 'closed'
        return res
    
    def get(self, request, thes_id):
        
        initial_node_id = int(request.GET.get("initial_node", "-1"))        
        
        if initial_node_id<=0:
            nodes = Term.objects.root_nodes().filter(thesaurus__id=thes_id)  # @UndefinedVariable                            
        else:
            initial_node = Term.objects.get(id=initial_node_id)  # @UndefinedVariable
            if initial_node.get_children().count() <= settings.JOCONDE_TERM_TREE_MAX_CHILDREN:
                nodes = initial_node.get_children()
            else:
                nodes = Term.objects.filter(id__in=initial_node.children_with_descendants)  # @UndefinedVariable
        
        if len(nodes) > settings.JOCONDE_TERM_TREE_MAX_ROOT_NODE:
            return HttpResponseForbidden(u"Too many nodes")
        
        children_counts = dict([(n.get('id',0),n.get('nb_children',0)) for n in nodes.values("id").annotate(nb_children=Count("children"))])
        
        selected_node_id = int(request.GET.get("selected_node", "-1"))
        if selected_node_id>0 :
            selected_node_ancestors = OrderedDict([(t.id, t) for t in Term.objects.get(id=selected_node_id).get_ancestors()])  # @UndefinedVariable
        else:
            selected_node_ancestors = {}
        
        res = [ self.get_node_data(node, children_counts.get(node.id,0), selected_node_ancestors) for node in nodes ]
                
        return HttpResponse(json.dumps(res, encoding="utf-8"), content_type="application/json; charset=utf-8")

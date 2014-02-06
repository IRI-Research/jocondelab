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
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from core import urls as core_urls
from jocondelab.views.ajax import ContributeView, VoteView
from jocondelab.views.back_office import (TermListView, TermEditView, 
    TermModifyWpLink, TermRemoveWpLink, TermValidate, TermWikipediaEdition, 
    TermLinkSemanticLevelEdition, ThesaurusTree, TermListTableView)
from jocondelab.views.front_office import (SearchView, NoticeView, GeoView, 
    FrontTermListView)
from jocondelab.views.i18n import cached_javascript_catalog
from django.views.decorators.cache import cache_page


js_info_dict = {
    'packages': ('core', 'jocondelab'),
}

admin.autodiscover()

urlpatterns = patterns('',    
    url(r'^auth/', include(auth_urls)),
    url(r'^core/', include(core_urls)),    
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='joconde_logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', cached_javascript_catalog, js_info_dict, name="i18n_javascript_catalog"),
    url(r'^bo/$', login_required(TermListView.as_view()), name='bo_home'),
    url(r'^bo/term/list/table$', login_required(TermListTableView.as_view()), name='term_list_table'),
    url(r'^bo/term/(?P<term_id>\d+)/$', login_required(TermEditView.as_view()), name='term'),
    url(r'^bo/term/modify-wp/$', login_required(TermModifyWpLink.as_view()), name='modify_wp_link'),
    url(r'^bo/term/remove-wp/$', login_required(TermRemoveWpLink.as_view()), name='remove_wp_link'),
    url(r'^bo/term/edition-wp/$', login_required(TermWikipediaEdition.as_view()), name='edition_wp_link'),
    url(r'^bo/term/edition-link-level/$', login_required(TermLinkSemanticLevelEdition.as_view()), name='editon_link_semantic_level'),
    url(r'^bo/term/validate/$', login_required(TermValidate.as_view()), name='validate_term'),
    url(r'^bo/tree/(?P<thes_id>\d+)/$', login_required(ThesaurusTree.as_view()), name='term_tree'),
    url(r'^$', cache_page(settings.HOME_CACHE_SECONDS)(SearchView.as_view(template_name="jocondelab/front_home.html")), name='front_home'),
    url(r'^keywords/$', FrontTermListView.as_view(), name='front_termlist'),
    url(r'^search/$', SearchView.as_view(), name='front_search'),
    url(r'^map/$', GeoView.as_view(), name='front_geo'),
    url(r'^timeline/$', TemplateView.as_view(template_name="jocondelab/front_timeline.html"), name='front_timeline'),
    url(r'^about/$', TemplateView.as_view(template_name="jocondelab/front_about.html"), name='front_about'),
    url(r'^credits/$', TemplateView.as_view(template_name="jocondelab/front_credits.html"), name='front_credits'),
    url(r'^legal/$', TemplateView.as_view(template_name="jocondelab/front_legal.html"), name='front_legal'),
    url(r'^students/$', TemplateView.as_view(template_name="jocondelab/front_students.html"), name='front_students'),
    url(r'^students_group/$', TemplateView.as_view(template_name="jocondelab/front_students_group.html"), name='front_students_group'),
    url(r'^notice/(?P<pk>\d+)/$', NoticeView.as_view(), name='front_notice'),
    url(r'^describe/(?P<pk>\d+)/$', NoticeView.as_view(template_name="jocondelab/front_describe.html", show_contributions=True), name='front_describe'),
    url(r'^describe/$', 'jocondelab.views.front_office.describe_view', name='random_describe'),
    url(r'^ajax/terms/$', 'jocondelab.views.ajax.terms', name='ajax_terms'),
    url(r'^ajax/years/$', 'jocondelab.views.ajax.years', name='ajax_years'),
    url(r'^ajax/geocoords/$', 'jocondelab.views.ajax.geo_coords', name='ajax_geo_coords'),
    url(r'^ajax/geosearch/$', 'jocondelab.views.ajax.geo_search', name='ajax_geo_search'),
    url(r'^ajax/contribute/$', ContributeView.as_view(), name='ajax_contribute'),
    url(r'^ajax/upvote/$', VoteView.as_view(vote_value=1), name='ajax_upvote'),
    url(r'^ajax/downvote/$', VoteView.as_view(vote_value=-1), name='ajax_downvote'),
)


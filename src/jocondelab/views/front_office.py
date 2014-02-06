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
Created on Aug 08, 2013

@author: rvelt
'''

import json
import logging
import math
import random

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Sum
from django.db.models.query import EmptyQuerySet
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.utils.translation import ugettext
from django.views.generic import DetailView, TemplateView
from haystack.query import SearchQuerySet
from unidecode import unidecode

from core.models import Notice, Term, TERM_WK_LINK_SEMANTIC_LEVEL_DICT
from core.models.term import Thesaurus
from jocondelab.models import (DbpediaFields, Country, ContributableTerm, 
    TagcloudTerm)
from jocondelab.utils import JocondeFrontPaginator


logger = logging.getLogger(__name__)

def get_terms_by_thesaurus(notices, lang):
    termsbythesaurus = {}
    for n in notices:
        termsbythesaurus[n.pk] = {}
    for nt in Term.objects.select_related('thesaurus__label','notices__pk').filter(noticeterm__notice__in=notices,dbpedia_fields=None, validated=True).filter(  # @UndefinedVariable
                ( Q(thesaurus__label__in=["AUTR","DOMN","ECOL","LIEUX","REPR","SREP"]) & Q(link_semantic_level=TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"]) ) | 
                ( Q(thesaurus__label__in=["EPOQ","PERI"]) & Q(link_semantic_level__in=[TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"], TERM_WK_LINK_SEMANTIC_LEVEL_DICT["BM"]]) ),
                ).order_by('label').distinct().values("thesaurus__label", "dbpedia_uri", "label", "notices__pk"):  # @UndefinedVariable
        term = {
            "thesaurus": nt["thesaurus__label"],
            "dbpedia_uri": nt["dbpedia_uri"],
            "translated": False,
            "label": nt["label"]
        }
        th = termsbythesaurus[nt["notices__pk"]].setdefault(term["thesaurus"], { "translated": [], "untranslated": [] })
        th["untranslated"].append(term)
    # We use "values" because it avoids an other db request for dbpedia_fields.get(language_code = lang).label
    for nt in Term.objects.select_related('thesaurus__label','dbpedia_fields','notices__pk').filter(noticeterm__notice__in=notices, dbpedia_fields__language_code=lang, validated=True).filter(  # @UndefinedVariable
                ( Q(thesaurus__label__in=["AUTR","DOMN","ECOL","LIEUX","REPR","SREP"]) & Q(link_semantic_level=TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"]) ) | 
                ( Q(thesaurus__label__in=["EPOQ","PERI"]) & Q(link_semantic_level__in=[TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"], TERM_WK_LINK_SEMANTIC_LEVEL_DICT["BM"]]) ),
                ).order_by('dbpedia_fields__label').distinct().values("thesaurus__label", "dbpedia_uri", "dbpedia_fields__label", "notices__pk"):  # @UndefinedVariable
        term = {
            "thesaurus": nt["thesaurus__label"],
            "dbpedia_uri": nt["dbpedia_uri"],
            "translated": True,
            "label": nt["dbpedia_fields__label"]
        }
        th = termsbythesaurus[nt["notices__pk"]].setdefault(term["thesaurus"], { "translated": [], "untranslated": [] })
        th["translated"].append(term)
    return termsbythesaurus

class SearchView(TemplateView):
    
    # This view is used for
    # - the home and search pages, displaying random images
    # - search result pages
    # - ajax-fetched results
    
    def get(self, request):
        
        context = {}
        lang = request.GET.get('lang',request.LANGUAGE_CODE)[:2]
        page = request.GET.get('page',1)
        querystr = request.GET.get('q', "")
        is_ajax = request.is_ajax()
        queryterms = [s.strip(" ") for s in querystr.split(";") if s.strip(" ")]
        dbpedia_uri = request.GET.get('dbpedia_uri', "")
        dbpedia_uris = [s.strip(" ") for s in dbpedia_uri.split(";") if s.strip(" ")]
        thesaurus = request.GET.get('thesaurus', None)
        from_year = request.GET.get('from_year', None)
        to_year = request.GET.get('to_year', from_year)
        show_years = request.GET.get('show_years',False)
        emptysearch = ((not queryterms) and (not dbpedia_uri) and (not from_year))
        npp = request.GET.get('count', 12 if emptysearch else 30)
        context["lang"] = lang
        context["current_page"] = page
        context["last_page"] = False
        
        if self.template_name is None:
            if is_ajax and page > 1:
                self.template_name = "jocondelab/partial/notice_list.html"
            elif is_ajax:
                self.template_name = "jocondelab/partial/wrapped_notice_list.html"
            else:
                self.template_name = "jocondelab/front_search.html"
        
        # Get first image url with extra : avoid prefetch on all images 
        qs = Notice.objects.filter(image=True)
        
        if emptysearch:
            
            if not cache.get('notice_count'):
                cache.set('notice_count', qs.count(), settings.DB_QUERY_CACHE_TIME)
            context_count = cache.get('notice_count')
            if not context_count:
                context_count = qs.count()
            context["count"] = context_count
            # Optimize random : order_by('?') is too slow
            # generate_series(1, 100) and not generate_series(1, 12) to be sure we have existing ids
            orm_request = """
SELECT "core_notice"."id", "core_notice"."ref", "core_notice"."adpt", "core_notice"."appl", "core_notice"."aptn", "core_notice"."attr", "core_notice"."autr", "core_notice"."bibl", "core_notice"."comm", "core_notice"."contact", "core_notice"."coor", "core_notice"."copy", "core_notice"."dacq", "core_notice"."data", "core_notice"."dation", "core_notice"."ddpt", "core_notice"."decv", "core_notice"."deno", "core_notice"."depo", "core_notice"."desc", "core_notice"."desy", "core_notice"."dims", "core_notice"."dmaj", "core_notice"."dmis", "core_notice"."domn", "core_notice"."drep", "core_notice"."ecol", "core_notice"."epoq", "core_notice"."etat", "core_notice"."expo", "core_notice"."gene", "core_notice"."geohi", "core_notice"."hist", "core_notice"."image", "core_notice"."insc", "core_notice"."inv", "core_notice"."label", "core_notice"."labo", "core_notice"."lieux", "core_notice"."loca", "core_notice"."loca2", "core_notice"."mill", "core_notice"."milu", "core_notice"."mosa", "core_notice"."msgcom", "core_notice"."museo", "core_notice"."nsda", "core_notice"."onom", "core_notice"."paut", "core_notice"."pdat", "core_notice"."pdec", "core_notice"."peoc", "core_notice"."peri", "core_notice"."peru", "core_notice"."phot", "core_notice"."pins", "core_notice"."plieux", "core_notice"."prep", "core_notice"."puti", "core_notice"."reda", "core_notice"."refim", "core_notice"."repr", "core_notice"."srep", "core_notice"."stat", "core_notice"."tech", "core_notice"."tico", "core_notice"."titr", "core_notice"."util", "core_notice"."video", "core_notice"."www", "core_noticeimage"."relative_url"
FROM  (
    SELECT 1 + floor(random() * %i)::integer AS id
    FROM   generate_series(1, 100) g
    GROUP  BY 1
    ) r
JOIN  "core_notice" USING (id)
INNER JOIN "core_noticeimage" ON ("core_notice"."id" = "core_noticeimage"."notice_id")
WHERE "core_notice"."image" = true  AND "core_noticeimage"."main" = true
LIMIT  12; 
            """
            ns = list(Notice.objects.raw(orm_request % context["count"]))
        else:
            uri_cache = {}
            if from_year:
                queryobj = {'from_year': from_year, 'to_year': to_year}
                searchterms = [u"%s – %s"%(from_year, to_year)]
                qs = qs.filter(years__start_year__lte=to_year, years__end_year__gte=from_year)
            else:
                if dbpedia_uris:
                    queryobj = {'dbpedia_uri': dbpedia_uri}
                    fs = list(DbpediaFields.objects.filter(dbpedia_uri__in=dbpedia_uris, language_code=lang).exclude(label__isnull=True))
                    searchterms = set([fields.label for fields in fs])
                    operator = "and"
                elif queryterms:
                    searchterms = queryterms
                    queryobj = {'q': querystr}
                    label_search = SearchQuerySet().models(DbpediaFields).filter(language_code__exact=lang).auto_query(" ".join([unidecode(q.lower()) for q in queryterms]), "label_trans")[:getattr(settings, 'MAX_TERMS_QUERY', 200)]
                    fs = list(DbpediaFields.objects.filter(id__in=[r.pk for r in label_search], language_code=lang).exclude(label__isnull=True))
                    operator = 'or'
                # If fs is empty, qs has to be empty
                if len(fs)==0:
                    qs = qs.none()

                fields_hash = {}
                for fields in fs:
                    fields_hash.setdefault(fields.dbpedia_uri, set()).add(fields.term_id)
                uri_cache.update(dict([(fields.label.lower() if fields.label else "", fields.dbpedia_uri) for fields in fs]))
                if page == 1 and len(dbpedia_uris) == 1 and len(fs) > 0:
                    context["wkinfo"] = fs[0]
                term_filters = Q()

                for term_ids in fields_hash.values():
                    if operator == "and" :
                        qs = qs.filter(noticeterm__term_id__in=term_ids)
                    else:
                        term_filters |= Q(noticeterm__term_id__in=term_ids)
                if operator == "or" :
                    qs = qs.filter(term_filters)
            
            count_qs = qs
            qs = qs.filter(noticeterm__term__validated=True)
            if thesaurus:
                if thesaurus == 'REPR':
                    qs = qs.filter(noticeterm__term__thesaurus__label__in=['REPR','SREP'], noticeterm__term__link_semantic_level=TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"])
                elif thesaurus == 'LIEUX':
                    qs = qs.filter(noticeterm__term__thesaurus__label__in=['LIEUX','ECOL','REPR'], noticeterm__term__link_semantic_level=TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"])
                elif thesaurus == 'EPOQ' or thesaurus == 'PERI':
                    qs = qs.filter(noticeterm__term__thesaurus__label=thesaurus, noticeterm__term__link_semantic_level__in=[TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"], TERM_WK_LINK_SEMANTIC_LEVEL_DICT["BM"]])
                else:
                    qs = qs.filter(noticeterm__term__thesaurus__label=thesaurus, noticeterm__term__link_semantic_level=TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"])
            else:
                qs = qs.filter(
                    ( Q(noticeterm__term__thesaurus__label__in=["AUTR","DOMN","ECOL","LIEUX","REPR","SREP"]) & Q(noticeterm__term__link_semantic_level=TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"]) ) | 
                    ( Q(noticeterm__term__thesaurus__label__in=["EPOQ","PERI"]) & Q(noticeterm__term__link_semantic_level__in=[TERM_WK_LINK_SEMANTIC_LEVEL_DICT["EE"], TERM_WK_LINK_SEMANTIC_LEVEL_DICT["BM"]]) ),
                    )
            
            context["queryobj"] = json.dumps(queryobj)
            context["querystr"] = urlencode(queryobj)
            context["searchterms_label"] = ugettext(u" ET ").join(searchterms)
            context["searchterms_input"] = u";".join(searchterms)
            context["uri_cache"] = json.dumps(uri_cache)
            
            if isinstance(qs, EmptyQuerySet):
                context["page_count"] = 0
                context["count"] = 0
                ns = []
            else:
                paginator = JocondeFrontPaginator(qs.values_list('id', flat=True).order_by('id').distinct(), npp, count_qs)
                context["page_count"] = paginator.num_pages
                
                ids = paginator.page(min(int(page),paginator.num_pages))
                if paginator.count:
                    count_log = math.log10(paginator.count) 
                    if count_log<=1:
                        context["count"] = paginator.count
                    elif 1 < count_log <= 3 :
                        context["count"] = paginator.count - (paginator.count%10)
                    else:
                        context["count"] = paginator.count - (paginator.count % 10**(int(count_log)-1) )
                else:
                    context["count"] = paginator.count
                
                # Now that we have the list of ids
                ns = Notice.objects.filter(pk__in=ids).extra(select={'relative_url': '"core_noticeimage"."relative_url"'}).filter(image=True).filter(images__main=True).order_by('id')
                # We check if we are in the last page of the "real" notices and not the +/- number of notices.
                if len(ns) < npp:
                    context["last_page"] = True
        
        notices = []
        termsbythesaurus = get_terms_by_thesaurus(ns, lang)
        for n in ns:
            noticedict = {
                "id": n.id,
                "title": n.titr,
                "designation": " | ".join([ v for v in [ n.deno, n.appl] if v ]),
                "image": settings.JOCONDE_IMAGE_BASE_URL + n.relative_url,
                "author": n.autr,
                "terms_by_thesaurus": termsbythesaurus[n.pk],
                "datation": termsbythesaurus[n.pk].get("PERI",{}).get("translated",[]) + termsbythesaurus[n.pk].get("EPOQ",{}).get("translated",[])
            }
            noticedict['image_title'] = noticedict['title'] if noticedict['title'] else noticedict['designation']
            if show_years and n.years.exists():
                noticedict["years"] = [n.years.all()[0].start_year, n.years.all()[0].end_year]
            notices.append(noticedict)
        context["notices"] = notices
        
        return self.render_to_response(context)

class GeoView(TemplateView):
    
    template_name = "jocondelab/front_geo.html"
    
    def get(self, request):
        
        context = {}
        cqs = Country.objects.order_by('-nb_notices')
        context["countries"] = json.dumps([c for c in cqs.values('dbpedia_uri','iso_code_3','nb_notices')])
        
        return self.render_to_response(context)
    
class NoticeView(DetailView):
    
    model = Notice
    template_name = "jocondelab/front_notice.html"
    show_contributions = True
    
    def get_context_data(self, **kwargs):
        
        context = super(NoticeView, self).get_context_data(**kwargs)
        lang = self.request.GET.get('lang',self.request.LANGUAGE_CODE)[:2]
        
        context["title"] = self.object.titr if self.object.titr else self.object.deno
        context["terms_by_thesaurus"] = get_terms_by_thesaurus([self.object], lang)[self.object.pk]
        
        if self.show_contributions:
            cqs = self.object.contribution_set.select_related('term__dbpedia_fields')
            if self.template_name == "jocondelab/front_describe.html":
                # describe mode : get contributions from session history and not from whole database
                contrib_h = self.request.session.setdefault('contribution_history', {})
                notice_id = str(self.object.id)
                if notice_id in contrib_h:
                    contrib_h = contrib_h[notice_id]
                else:
                    contrib_h = []
                
                query = cqs.filter(thesaurus=Thesaurus.objects.get(label="REPR"), 
                                   term__dbpedia_fields__language_code=lang, 
                                   term__dbpedia_uri__in=contrib_h).order_by('-contribution_count')
                vote_mode = False
            else:
                query = cqs.filter(thesaurus=None,term__dbpedia_fields__language_code=lang).order_by('-contribution_count')
                vote_mode = True
            contributions = [{
                    "label": ct.term.dbpedia_fields.get(language_code=lang).label,
                    "dbpedia_uri": ct.term.dbpedia_uri,
                    "contribution_id": ct.id,
                    "li_style": "positive" if ct.contribution_count > 0 else "null",
                    "font_size": "%.1f"%(12. + .5 * max(0., min(12., ct.contribution_count))),
                    "vote_mode": vote_mode
                } for ct in query]
            context["contributions"] = contributions
        
        context['wikipedia_urls'] = json.dumps(settings.WIKIPEDIA_URLS)
        context['JOCONDE_NOTICE_BASE_URL'] = settings.JOCONDE_NOTICE_BASE_URL
        
        # History for describe view
        notice_history = self.request.session.get('notice_history',[])
        if self.object.id in notice_history:
            p = notice_history.index(self.object.id)
            if p < len(notice_history) - 1:
                context['next_notice'] = notice_history[p + 1]
            if p > 0:
                context['prev_notice'] = notice_history[p - 1]
        
        # History for notices
        h = self.request.session.setdefault('history', [])
        if self.object.id not in h:
            h.append(self.object.id)
            self.request.session['history'] = h
        
        return context

def describe_view(request):
    notice_history = request.session.get('notice_history',[])
    all_qs = Notice.objects.filter(image=True, repr='', peri__contains='4e quart 19e siècle', noticeterm__term__id__in=ContributableTerm.objects.values('term__id'))
    qs = all_qs.exclude(id__in=notice_history)
    found_notices = qs.count()
    if not found_notices:
        notice_history = []
        qs = all_qs
        found_notices = qs.count()
    id = qs[random.randint(0, found_notices - 1)].id  # @ReservedAssignment
    notice_history.append(id)
    request.session['notice_history'] = notice_history
    return redirect('front_describe', pk=id)

class FrontTermListView(TemplateView):
    
    template_name = "jocondelab/front_termlist.html"
    
    def image_extra(self, qs):
        return qs.extra(select={
                  'image_url': 'SELECT relative_url FROM core_noticeimage AS JL01 JOIN core_notice AS JL02 ON JL02.id = JL01.notice_id JOIN core_noticeterm AS JL03 ON JL02.id = JL03.notice_id WHERE JL03.term_id = core_term.id LIMIT 1'
              })
    
    def get(self, request):
        
        context = {}
        lang = self.request.GET.get('lang',self.request.LANGUAGE_CODE)[:2]
        letter = self.request.GET.get('letter',None)
        alpha_sort = (letter is not None) or self.request.GET.get('alphabet',False)
        context['alpha_sort'] = alpha_sort
        thesaurus = self.request.GET.get('thesaurus',None)
        context['thesaurus'] = thesaurus
        
        if thesaurus is None:
            wqs = TagcloudTerm.objects.filter(term__dbpedia_fields__language_code=lang).values('term__dbpedia_fields__label','term__dbpedia_uri')
            wqs = wqs.distinct().annotate(sum_notice=Sum('term__nb_illustrated_notice')).order_by('-sum_notice')
            n = wqs.count()
            context['words'] = [{
                     'label': w['term__dbpedia_fields__label'],
                     'uri': w['term__dbpedia_uri'],
                     'font_size': "%.2f"%(1. + float(n-i)/n)
                                 } for i, w in enumerate(wqs)]
            random.shuffle(context['words'])
        else:
            alphabets = [{
                  "languages": [ "fr", "en", "de", "it", "es", "pt", "ca", "br", "eu", "oc" ],
                  "letters": u"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
              }, {
                  "languages": [ "ru" ],
                  "letters": u"АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ"
              }, {
                  "languages": [ "ar" ],
                  "letters": u"ابتثجحخدذرزسشصضطظعغفقكلمنهوي"
            }]
            latinalph = alphabets[0]
            alphabet = None
            for a in alphabets:
                if lang in a["languages"]:
                    alphabet = a
            if alphabet is not None:
                if thesaurus in ['REPR','AUTR']:
                    context["show_alphabet"] = True
                letters = alphabet["letters"]
                context["alphabet"] = letters
                if letter is not None:
                    letterpos = letters.find(letter)
            context["current_letter"] = letter
            if (not alpha_sort) or (thesaurus == 'AUTR' and alphabet == latinalph and letter is not None):
                # When ordering is not by translated label, we query the Term table
                tqs = Term.objects.filter(dbpedia_fields__language_code=lang, nb_illustrated_notice__gt=0, validated=True)  # @UndefinedVariable
                if thesaurus == 'REPR':
                    tqs = tqs.filter(thesaurus__label__in=['REPR','SREP'])
                else:
                    tqs = tqs.filter(thesaurus__label=thesaurus)
                img_dict = {}
                if alpha_sort:
                    # Particular case in which thesaurus == AUTR and the alphabet is latin,
                    # we use original sorting by family name
                    if letterpos >= 0:
                        tqs = tqs.filter(label__gte=letters[letterpos])
                    if letterpos < len(letters)-1:
                        tqs = tqs.filter(label__lt=letters[letterpos+1])
                    tqs = tqs.distinct('label').order_by('label')
                    tqs = self.image_extra(tqs).values('image_url','dbpedia_uri','dbpedia_fields__abstract','label')
                    terms = []
                    known_uris = []
                    for t in tqs:
                        uri = t['dbpedia_uri']
                        if uri not in known_uris:
                            terms.append(t)
                            known_uris.append(uri)
                        if t["image_url"]:
                            img_dict[t["dbpedia_uri"]] = t["image_url"]
                else:
                    # First optimised query with sum of nb of notices
                    terms = tqs.values('dbpedia_uri','dbpedia_fields__abstract','dbpedia_fields__label').annotate(num_not=Sum('nb_illustrated_notice')).order_by('-num_not')[:60]
                    # Second query to get images and create dict dbpedia_uri:image_url
                    img_qs = self.image_extra(Term.objects.filter(dbpedia_uri__in=[t['dbpedia_uri'] for t in terms])).values_list('dbpedia_uri','image_url')  # @UndefinedVariable
                    # Build img_dict by avoiding None values
                    for (uri,img) in img_qs:
                        if img:
                            img_dict[uri] = img
                # Build term list
                terms = [{
                      "dbpedia_uri": t['dbpedia_uri'],
                      "label": t.get('dbpedia_fields__label',t.get('label','')),
                      "abstract": t['dbpedia_fields__abstract'],
                      "image_url": "%s%s"%(settings.JOCONDE_IMAGE_BASE_URL, img_dict.get(t['dbpedia_uri'],''))
                } for t in terms]
                
                context['termcount'] = len(terms)
            else:
                # When ordering is by translated label, we query the DbpediaFields table
                tqs = DbpediaFields.objects.filter(language_code=lang, term__nb_illustrated_notice__gt=0).exclude(label=None)
                if thesaurus == 'REPR':
                    tqs = tqs.filter(term__thesaurus__label__in=['REPR','SREP'])
                else:
                    tqs = tqs.filter(term__thesaurus__label=thesaurus)
                if thesaurus in ['REPR','AUTR'] and letter is not None: #Pagination required for these two thesaura
                    if alphabet is not None:
                        if letterpos >= 0:
                            tqs = tqs.filter(label__gte=letters[letterpos])
                        if letterpos < len(letters)-1:
                            tqs = tqs.filter(label__lt=letters[letterpos+1])
                tqs = tqs.distinct('label').order_by('label')
                terms = self.image_extra(tqs).values('image_url','dbpedia_uri','abstract','label')
                for t in terms:
                    t['image_url'] = "%s%s"%(settings.JOCONDE_IMAGE_BASE_URL, t['image_url'])
                context['termcount'] = terms.count()
            context['terms'] = terms
        
        return self.render_to_response(context)
    
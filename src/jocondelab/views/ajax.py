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
Created on Aug 20, 2013

@author: rvelt
'''

import json
import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models import Sum
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.views.generic import TemplateView
from haystack.query import SearchQuerySet
import requests

from core.models import Notice, Thesaurus
from jocondelab.models import (DbpediaYears, DbpediaGeo, DbpediaFields, 
    ContributedTerm, ContributedFields, Contribution)

logger = logging.getLogger(__name__)

def terms(request):
    
    lang = request.GET.get('lang', request.LANGUAGE_CODE)[:2]
    q = request.GET.get('term', None)
    count = request.GET.get('count', 20)
    
    cachekey = "--".join((q,lang,str(count)))
    res_list = cache.get(cachekey)
    
    if not res_list:

        if lang in [ "fr", "en", "de", "it", "es", "pt", "ca", "br", "eu", "oc" ]:
            fields_index_qs = SearchQuerySet().models(DbpediaFields).filter(language_code__exact=lang).autocomplete(label_edge=q)
        else:
            fields_index_qs = SearchQuerySet().models(DbpediaFields).filter(language_code__exact=lang).autocomplete(label_ngram=q)

        res_dict = {}
        for r in fields_index_qs[:count*5]:
            dbpedia_uri = r.get_stored_fields()['dbpedia_uri']
            label = r.get_stored_fields()['label']
            if not dbpedia_uri:
                continue
            res_entry = res_dict.setdefault(dbpedia_uri, {'label': None, 'score':0, 'uri':dbpedia_uri})
            res_entry['label'] = label if label and not res_entry.get('label', None) else res_entry['label']
            res_entry['score'] += r.score

        res_list = sorted([ res_entry for res_entry in res_dict.values()],key=lambda r: r.get('score',0), reverse=True)
        cache.set(cachekey, res_list)
    return HttpResponse(content=json.dumps([{"dbpedia_uri":r.get('uri'), "label": r.get('label','')} for r in res_list]), mimetype='application/json')

def years(request):
    
    lang = request.GET.get('lang', request.LANGUAGE_CODE)[:2]
    from_year = request.GET.get('from_year', None)
    to_year = request.GET.get('to_year', None)
    count = request.GET.get('count', 20)
    
    qs = DbpediaYears.objects.filter(term__nb_illustrated_notice__gt=0,term__dbpedia_fields__language_code=lang)
    if to_year:
        qs = qs.filter(start_year__lte=to_year)
    if from_year:
        qs = qs.filter(end_year__gte=from_year)
    qs = qs.values('start_year','end_year','term__dbpedia_fields__label','term__dbpedia_uri')
    qs = qs.annotate(sum_notices=Sum('term__nb_illustrated_notice')).order_by('-sum_notices')
    
    qs = qs[:count]
    
    results = [{
                "start_year": y["start_year"],
                "end_year": y["end_year"],
                "label": y["term__dbpedia_fields__label"],
                "sum_notices": y["sum_notices"],
                "dbpedia_uri": y["term__dbpedia_uri"]
                } for y in qs]
    
    return HttpResponse(content=json.dumps(results), mimetype='application/json')

def geo_coords(request):
    
    lang = request.GET.get('lang', request.LANGUAGE_CODE)[:2]
    min_lat = request.GET.get('min_lat', None)
    max_lat = request.GET.get('max_lat', None)
    min_lng = request.GET.get('min_lng', None)
    max_lng = request.GET.get('max_lng', None)
    count = request.GET.get('count', 20)
    
    qs = DbpediaGeo.objects.filter(term__dbpedia_fields__language_code=lang,term__nb_illustrated_notice__gt=0)
    
    if min_lat:
        qs = qs.filter(latitude__gt=min_lat)
    if max_lat:
        qs = qs.filter(latitude__lt=max_lat)
    if min_lng:
        qs = qs.filter(longitude__gt=min_lng)
    if max_lng:
        qs = qs.filter(longitude__lt=max_lng)
    
    qs = qs.values('latitude','longitude','term__dbpedia_fields__label','term__dbpedia_uri')
    qs = qs.annotate(sum_notices=Sum('term__nb_illustrated_notice')).order_by('-sum_notices')
    
    qs = qs[:count]
    
    results = [{
                "latitude": y["latitude"],
                "longitude": y["longitude"],
                "label": y["term__dbpedia_fields__label"],
                "sum_notices": y["sum_notices"],
                "dbpedia_uri": y["term__dbpedia_uri"]
                } for y in qs]
    
    return HttpResponse(content=json.dumps(results), mimetype='application/json')

def geo_search(request):
    
    lang = request.GET.get('lang', request.LANGUAGE_CODE)[:2]
    q = request.GET.get('term', None)
    count = request.GET.get('count', 20)
    
    qs = DbpediaGeo.objects.filter(term__dbpedia_fields__language_code=lang, term__dbpedia_fields__label__icontains=q, term__nb_illustrated_notice__gt=0)
    qs = qs.values('latitude','longitude','term__dbpedia_fields__label','term__dbpedia_uri')
    qs = qs.annotate(sum_notices=Sum('term__nb_illustrated_notice')).order_by('-sum_notices')[:count]
    
    results = [{
                "latitude": y["latitude"],
                "longitude": y["longitude"],
                "label": y["term__dbpedia_fields__label"],
                "sum_notices": y["sum_notices"],
                "dbpedia_uri": y["term__dbpedia_uri"]
                } for y in qs]
    results.sort(key=lambda y: y["label"])
    
    return HttpResponse(content=json.dumps(results), mimetype='application/json')

class BaseContributionView(TemplateView):
    
    template_name = "jocondelab/partial/contributed_item.html"
    
    def render_contribution(self, contribution, request):
        lang = request.LANGUAGE_CODE[:2]
        try:
            label =  contribution.term.dbpedia_fields.get(language_code=lang).label
        except:
            return HttpResponseBadRequest("Label not available")
        termdict = {
            "label": label,
            "dbpedia_uri": contribution.term.dbpedia_uri,
            "contribution_id": contribution.id,
            "li_style": "positive" if contribution.contribution_count > 0 else "null",
            "font_size": "%.1f"%(12. + .5 * max(0., min(12., contribution.contribution_count))),
            "vote_mode": (contribution.thesaurus is None)
        }
        return self.render_to_response({"term": termdict})
    
    def get(self, request):
        contribution_id = int(request.GET.get('contribution_id', 0))
        if not contribution_id:
            return HttpResponseBadRequest("Wrong contribution id")
        return self.render_contribution(Contribution.objects.get(pk=contribution_id), request)

class ContributeView(BaseContributionView):
    
    def post(self, request):
        
        notice_id = request.POST.get('notice_id', None)
        lang = request.LANGUAGE_CODE[:2]
        thesaurus_label = request.POST.get('thesaurus_label', None)
        label = request.POST.get('label', None)
        
        sparqlTpl = """select distinct * where { ?s rdfs:label "%(label)s"@%(lang)s . 
            OPTIONAL { ?s dbpedia-owl:abstract ?a. FILTER(langMatches(lang(?a),"%(lang)s")) }. 
            OPTIONAL { ?s dbpedia-owl:thumbnail ?t }. 
            OPTIONAL { ?s dbpedia-owl:wikiPageRedirects ?r }.  
            OPTIONAL { ?r rdfs:label ?lr. FILTER(langMatches(lang(?lr),"%(lang)s")) }. 
            OPTIONAL { ?r dbpedia-owl:thumbnail ?tr }. 
            OPTIONAL { ?s dbpedia-owl:wikiPageDisambiguates ?d }. 
            OPTIONAL { ?d rdfs:label ?ld FILTER( langMatches(lang(?ld), "%(lang)s") ) }. 
            FILTER(!regex(?s, ":[^/]+$" ) && regex(?s, "^http://[^/]+/resource/")) }"""
        
        # First, test wikipedia_url
        dbpedia_uri = None
        r = requests.get('http://' + lang + '.wikipedia.org/wiki/' + label.replace(" ", "_"))
        if r.status_code == 200:
            # dbpedia FR sparql request
            data = {'query': sparqlTpl % {'label': label, 'lang':lang}, 'format': "application/sparql-results+json"}
            r = requests.get("http://fr.dbpedia.org/sparql", params=data, headers = {'content-type': "application/sparql-results+json"})
            if r.status_code != 200:
                return HttpResponseBadRequest()
            resp = r.json()
            if "results" in resp and "bindings" in resp["results"] and len(resp["results"]["bindings"])>0:
                dbpedia_uri = resp["results"]["bindings"][0]["s"]["value"]
        
        if not dbpedia_uri:
            return HttpResponseBadRequest()
        
        thobj = Thesaurus.objects.get(label=thesaurus_label) if thesaurus_label else None
        notobj = Notice.objects.get(id=notice_id)
        
        # History for the contribution term for this notice
        h = self.request.session.setdefault('contribution_history', {})
        if notice_id not in h:
            h[notice_id] = []
        h[notice_id].append(dbpedia_uri)
        self.request.session['contribution_history'] = h
        
        # Contributed Term is now validated and Dbpedia uris is regenerated by SPARQL Queries
        try:
            termobj, _ = ContributedTerm.objects.get_or_create(dbpedia_uri=dbpedia_uri)
        except:
            return HttpResponseBadRequest()
        controbj, created = Contribution.objects.get_or_create(term=termobj, thesaurus=thobj, notice=notobj, defaults={'contribution_count': 1})
        if not created:
            controbj.contribution_count += 1
            controbj.save()
        
        # Translated labels should also be regenerated from dbpedia.
        # Select labels from dppedia
        sparqlTpl = """select distinct * where { <%(uri)s> rdfs:label ?l . 
            OPTIONAL { <%(uri)s> dbpedia-owl:abstract ?a. FILTER(langMatches(lang(?l), lang(?a))) }. 
            OPTIONAL { <%(uri)s> dbpedia-owl:thumbnail ?t }. 
            OPTIONAL { <%(uri)s> dbpedia-owl:wikiPageRedirects ?r }.   
            OPTIONAL { ?r dbpedia-owl:thumbnail ?tr }. 
            OPTIONAL { <%(uri)s> dbpedia-owl:wikiPageDisambiguates ?d }.  
            FILTER(!regex(<%(uri)s>, ":[^/]+$" ) && regex(<%(uri)s>, "^http://[^/]+/resource/")) }"""
        
        # dbpedia FR sparql request
        data = {'query': sparqlTpl % {'uri': dbpedia_uri}, 'format': "application/sparql-results+json"}
        r = requests.get("http://fr.dbpedia.org/sparql", params=data, headers = {'content-type': "application/sparql-results+json"})
        if r.status_code == 200:
            resp = r.json()
            if "results" in resp and "bindings" in resp["results"] and len(resp["results"]["bindings"])>0:
                lang_list = [k[:2] for k,_ in settings.LANGUAGES]
                # We add label/abstract/thumbnail for all languages found for the dbpedia entry
                for b in resp["results"]["bindings"]:
                    # We assume that label is always here
                    lang = b["l"]["xml:lang"]
                    if lang in lang_list:
                        fieldsobj, created = ContributedFields.objects.get_or_create(term=termobj, dbpedia_uri=dbpedia_uri, language_code=lang, defaults={'label': label})
                        if created:
                            fieldsobj.label = b["l"]["value"]
                            if "t" in b:
                                fieldsobj.thumbnail = b["t"]["value"]
                            elif "tr" in b:
                                fieldsobj.thumbnail = b["tr"]["value"]
                            if "a" in b:
                                fieldsobj.abstract = b["a"]["value"]
                            fieldsobj.save()
                
            else:
                fieldsobj, created = ContributedFields.objects.get_or_create(term=termobj, dbpedia_uri=dbpedia_uri, language_code=lang, defaults={'label': label})
                # thumbnail, label, abstract
                if created:
                    fieldsobj.label = label
                    fieldsobj.save()
        
        return self.render_contribution(controbj, request)
    

class VoteView(BaseContributionView):
    
    vote_value = 0
    
    def post(self, request):
        contribution_id = int(request.POST.get('contribution_id', None))
        controbj = Contribution.objects.get(id=contribution_id)
        controbj.contribution_count += self.vote_value
        controbj.save()
        return self.render_contribution(controbj, request)
    
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


import bz2
import csv
import gc
import gzip
import logging
import re
from functools import reduce
from optparse import make_option

import rdflib
from django.core.management import BaseCommand
from django.core.management.base import CommandError
from django.core.paginator import Paginator
from django.db.models import Q
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DC, RDF, RDFS, SKOS, XSD, Namespace

from core.models import (AutrNoticeTerm, DomnNoticeTerm, EcolNoticeTerm,
                         EpoqNoticeTerm, LieuxNoticeTerm, Notice, NoticeTerm,
                         PeriNoticeTerm, ReprNoticeTerm, SrepNoticeTerm, Term,
                         Thesaurus)
from core.utils import show_progress
from jocondelab.models import ContributedTerm, Contribution

logger = logging.getLogger(__name__)

JOCONDELAB_NS = Namespace("http://jocondelab.iri-research.org/ns/jocondelab/")
JOCONDELAB_DATA_NS = "https://jocondelab.iri-research.org/data/"

GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

PREFIX_REGEXP = re.compile("^@prefix\s+")

fields = [
    "label", "uri", "validated", "wp_label", "wp_alternative_label",
    "thesaurus__label", "thesaurus__uri", "dbpedia_uri", "wikipedia_url",
    "wikipedia_pageid", "wikipedia_revision_id", "alternative_wikipedia_url",
    "alternative_wikipedia_pageid", "url_status", "link_semantic_level",
    "wikipedia_edition"
]

rdf_namespaces = {
    'thesaurus': {
        'skos': SKOS,
        'rdf': RDF,
        'dc': DC,
    },
    'term': {
        'skos': SKOS,
        'rdf': RDF,
        'rdfs': RDFS,
        'dc': DC,
        'xsd': XSD,
        'geo': GEO,
        'jcl': JOCONDELAB_NS
    },
    'notice': {
        'rdf': RDF,
        'rdfs': RDFS,
        'dc': DC,
        'jcl': JOCONDELAB_NS
    },
    'contributed_term': {
        'rdf': RDF,
        'rdfs': RDFS,
        'dc': DC,
        'jcl': JOCONDELAB_NS
    },
    'contribution': {
        'rdf': RDF,
        'rdfs': RDFS,
        'dc': DC,
        'jcl': JOCONDELAB_NS
    }
}

PAGINATION_SIZE = 100

class Command(BaseCommand):
    args = "file_path..."

    help = "Export jocondelab term link in rdf"

    option_list = BaseCommand.option_list + (
        make_option('-l', '--limit',
            dest='limit',
            type='int',
            default=-1,
            help='number of term to export. -1 is all (default)'
        ),
        # make_option('-s', '--skip',
        #     dest='skip',
        #     type='int',
        #     default=0,
        #     help='number of term to skip before export. default 0.'
        # ),
        make_option('-b', '--batch',
            dest='batch',
            type='int',
            default=100,
            help='query batch default 100.'
        ),
        make_option('-j', '--bzip2',
            dest='bzip2',
            action='store_true',
            default=False,
            help='bz2 compress'
        ),
        make_option('-z', '--gzip',
            dest='gzip',
            action='store_true',
            default=False,
            help='gzip compress'
        ),
        make_option('--newline',
            dest='newline',
            action='store_true',
            default=False,
            help='show progress with newlines'
        ),
    )

    def get_fields(self):
        return fields

    def get_query(self):
        return Term.objects.all().select_related(*[field.name for field in Term._meta.fields if isinstance(field, ForeignKey)]).order_by('uri').values_list(*fields)  # @UndefinedVariable

    def process_row(self, r):
        return r

    def get_row_message(self, r):
        return "Exporting term %s" % r[0]  # @IgnorePep8

    def bind_namespaces(self, g, namespaces):
        for k,ns in namespaces.items():
            g.bind(k,ns)

    def define_extensions(self, g):
        self.addN(g, [
            (JOCONDELAB_NS.wikipediaLabel, RDFS.subPropertyOf, SKOS.altLabel),
            (JOCONDELAB_NS.wikipediaAlternativeLabel, RDFS.subPropertyOf, SKOS.altLabel),
            # JOCONDELAB_NS.Thesaurus -> SKOS.ConceptScheme
            # JOCONDELAB_NS.Term -> SKOS.Concept
            # JOCONDELAB_NS.normalizedLabel -> SKOS.hiddenLabel
            # JOCONDELAB_NS.wikipediaPage -> range foaf:Document
            # <owl:ObjectProperty rdf:about="#wikipediaArticle">
            #     <rdfs:comment xml:lang="en">A Wikipedia article of which subject is the resource.</rdfs:comment>
            #     <rdfs:domain rdf:resource="#Feature"/>
            #     <rdfs:label xml:lang="en">wikipedia article</rdfs:label>
            #     <rdfs:range rdf:resource="#WikipediaArticle"/>
            # </owl:ObjectProperty>
            # JOCONDELAB_NS.wikipediaPageID ??
            # JOCONDELAB_NS.wikipediaPageRevision ??
            # JOCONDELAB_NS.alternativeWikipediaPage -> range foaf:Document
            # JOCONDELAB_NS.alternativeWikipediaPageID ??
            # JOCONDELAB_NS.dbpediaResource
            # JOCONDELAB_NS.urlStatus  cf: src/core/models/term.py
            #   (0, "null_result"),
            #   (1, "redirection"),
            #   (2, "homonyme"),
            #   (3, "match"),
            #   (4, "unsematized"),
            # JOCONDELAB_NS.linkSemanticLevel cf: src/core/models/term.py
            #   TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES = (
            #   (0, "--"),
            #   (1, "EE"),
            #   (2, "EI"),
            #   (3, "BM"),
            #   (4, "NM"))
            # JOCONDELAB_NS.linkValidated
            # JOCONDELAB_NS.linkValidationDate
            # JOCONDELAB_NS.linkValidator
            # JOCONDELAB_NS.wikipediaEdition
            # JOCONDELAB_NS.DbpediaField
            # JOCONDELAB_NS.dbpediaField
            # JOCONDELAB_NS.dbpediaFieldThumbnail
            # JOCONDELAB_NS.dbpediaFieldLabel
            # JOCONDELAB_NS.dbpediaFieldAbstract
            # JOCONDELAB_NS.DbpediaYear
            # JOCONDELAB_NS.dbpediaYear
            # JOCONDELAB_NS.dbpediaYearStart
            # JOCONDELAB_NS.dbpediaYearEnd
            # JOCONDELAB_NS.DbpediaGeo
            # JOCONDELAB_NS.dbpediaGeo
            # JOCONDELAB_NS.Notice
            # JOCONDELAB_NS.NoticeImage
            
            # JOCONDELAB_NS.YearInfo
            # JOCONDELAB_NS.YearInfoStart
            # JOCONDELAB_NS.YearInfoEnd

            # JOCONDELAB_NS.noticeRef
            # JOCONDELAB_NS.noticeAdpt
            # JOCONDELAB_NS.noticeAppl
            # JOCONDELAB_NS.noticeAptn
            # JOCONDELAB_NS.noticeAttr
            # JOCONDELAB_NS.noticeAutr
            # JOCONDELAB_NS.noticeAutrTerm
            # JOCONDELAB_NS.noticeBibl
            # JOCONDELAB_NS.noticeComm
            # JOCONDELAB_NS.noticeContact
            # JOCONDELAB_NS.noticeCoor
            # JOCONDELAB_NS.noticeCopy
            # JOCONDELAB_NS.noticeDacq
            # JOCONDELAB_NS.noticeCata
            # JOCONDELAB_NS.noticeDation 
            # JOCONDELAB_NS.noticeDdpt
            # JOCONDELAB_NS.noticeDecv
            # JOCONDELAB_NS.noticeDeno
            # JOCONDELAB_NS.noticeDepo
            # JOCONDELAB_NS.noticeDesc
            # JOCONDELAB_NS.noticeDesy
            # JOCONDELAB_NS.noticeDims
            # JOCONDELAB_NS.noticeDmaj
            # JOCONDELAB_NS.noticeDmis
            # JOCONDELAB_NS.noticeDomn
            # JOCONDELAB_NS.noticeDomnTerm
            # JOCONDELAB_NS.noticeDrep
            # JOCONDELAB_NS.noticeEcol
            # JOCONDELAB_NS.noticeEcolTerm 
            # JOCONDELAB_NS.noticeEpoq
            # JOCONDELAB_NS.noticeEpoqTerm
            # JOCONDELAB_NS.noticeEtat
            # JOCONDELAB_NS.noticeExpo
            # JOCONDELAB_NS.noticeGene
            # JOCONDELAB_NS.noticeGeohi
            # JOCONDELAB_NS.noticeHist
            # JOCONDELAB_NS.noticeImage
            # JOCONDELAB_NS.noticeInsc
            # JOCONDELAB_NS.noticeInv 
            # JOCONDELAB_NS.noticeLabel
            # JOCONDELAB_NS.noticeLabo
            # JOCONDELAB_NS.noticeLieux
            # JOCONDELAB_NS.noticeLieuxTerm
            # JOCONDELAB_NS.noticeLoca
            # JOCONDELAB_NS.noticeLoca2
            # JOCONDELAB_NS.noticeMill
            # JOCONDELAB_NS.noticeMilu
            # JOCONDELAB_NS.noticeMosa
            # JOCONDELAB_NS.noticeMsgcom
            # JOCONDELAB_NS.noticeMuseo
            # JOCONDELAB_NS.noticeNsda
            # JOCONDELAB_NS.noticeOnom
            # JOCONDELAB_NS.noticePaut
            # JOCONDELAB_NS.noticePdat
            # JOCONDELAB_NS.noticePdec
            # JOCONDELAB_NS.noticePeoc
            # JOCONDELAB_NS.noticePeri
            # JOCONDELAB_NS.noticePeriTerm
            # JOCONDELAB_NS.noticePeru
            # JOCONDELAB_NS.noticePhot
            # JOCONDELAB_NS.noticePins
            # JOCONDELAB_NS.noticePlieux
            # JOCONDELAB_NS.noticePrep
            # JOCONDELAB_NS.noticePuti
            # JOCONDELAB_NS.noticeReda
            # JOCONDELAB_NS.noticeRefim
            # JOCONDELAB_NS.noticeRepr
            # JOCONDELAB_NS.noticeReprTerm
            # JOCONDELAB_NS.noticeSrep
            # JOCONDELAB_NS.noticeSrepTerm
            # JOCONDELAB_NS.noticeStat
            # JOCONDELAB_NS.noticeTech
            # JOCONDELAB_NS.noticeTico
            # JOCONDELAB_NS.noticeTitr
            # JOCONDELAB_NS.noticeUtil
            # JOCONDELAB_NS.noticeVideo
            # JOCONDELAB_NS.noticeWww

            # JOCONDELAB_NS.noticeImage
            # JOCONDELAB_NS.noticeImageUrl

            # JOCONDELAB_NS.noticeYear
            # JOCONDELAB_NS.noticeYearStart
            # JOCONDELAB_NS.noticeYearEnd

            # JOCONDELAB_NS.ContributedTerm
            # JOCONDELAB_NS.Contribution
            # JOCONDELAB_NS.contributionTerm
            # JOCONDELAB_NS.contributionThesaurus
            # JOCONDELAB_NS.contributionNotice
            # JOCONDELAB_NS.contributionCount

        ])

    def add_n(self, g, triples):
        for triple in triples:
            g.add(triple)


    def remove_namespace_declarations(self, rdf_str):
        res_str = ""
        for line in rdf_str.splitlines():
            if not PREFIX_REGEXP.match(line):
                res_str += line + "\n"

        return res_str


    def export_namespaces(self, dest_file):
        g = Graph()
        namespaces = reduce(lambda res, k: dict(res, **rdf_namespaces[k]) , rdf_namespaces.keys(), {})
        self.bind_namespaces(g, namespaces)
        g.serialize(dest_file, format='turtle')


    def export_objects(self, query, obj_name, build_object_graph, dest_file):
        
        print("Exporting " + obj_name)
        namespaces = rdf_namespaces.get(obj_name, {})
        progress_writer = None
        obj_query = query
        if self.limit>=0:
            obj_query = query[:self.limit]
        obj_paginator = Paginator(obj_query, PAGINATION_SIZE)
        obj_count = obj_paginator.count
        i = 0
        for page_nb in obj_paginator.page_range:
            for obj in obj_paginator.page(page_nb):
                g = Graph()
                self.bind_namespaces(g, namespaces)
                g = build_object_graph(g, obj)
                i += 1
                progress_writer = show_progress(
                    i,
                    obj_count,
                    "Exporting " + obj_name,
                    40,
                    writer=progress_writer,
                    newline=self.newline
                )
                dest_file.write(self.remove_namespace_declarations(g.serialize(format='turtle')))
            gc.collect()


    def export_thesaurus(self, g, thes):
        thes_ref = URIRef(thes.uri)
        self.add_n(g,[
            (thes_ref, RDF.type, JOCONDELAB_NS.Thesaurus),
            (thes_ref, DC.title, Literal(thes.title, lang="fr")),
            (thes_ref, DC.description, Literal(thes.description, lang="fr")),
            (thes_ref, DC.identifier, Literal(thes.label))
        ])
        return g


    def export_term(self, g, term):

        term_ref = URIRef(term.uri)
        self.add_n(g, [
            (term_ref, RDF.type, JOCONDELAB_NS.Term),
            (term_ref, SKOS.inScheme, URIRef(term.thesaurus.uri)),
            (term_ref, DC.language, Literal(term.lang)),
            (term_ref, SKOS.prefLabel, Literal(term.label, lang=term.lang)),
            (term_ref, JOCONDELAB_NS.normalizedLabel, Literal(term.normalized_label, lang=term.lang)),
            (term_ref, DC.created, Literal(term.created_at)),
            (term_ref, JOCONDELAB_NS.urlStatus, Literal(term.url_status)),
            (term_ref, JOCONDELAB_NS.linkSemanticLevel, Literal(term.link_semantic_level)),
            (term_ref, JOCONDELAB_NS.linkValidated, Literal(term.validated)),
            (term_ref, JOCONDELAB_NS.wikipediaEdition, Literal(term.wikipedia_edition)),
            (term_ref, JOCONDELAB_NS.noticeNb, Literal(term.nb_notice)),
            (term_ref, JOCONDELAB_NS.illusratedNoticeNb, Literal(term.nb_illustrated_notice)),
        ])
        if term.wp_label:
            g.add((term_ref, JOCONDELAB_NS.wikipediaLabel, Literal(term.wp_label, lang=term.lang)))
        if term.wp_alternative_label:
            g.add((term_ref, JOCONDELAB_NS.wikipediaAlternativeLabel, Literal(term.wp_alternative_label, lang=term.lang)))

        if term.wikipedia_url:
            g.add((term_ref, JOCONDELAB_NS.wikipediaPage, URIRef(term.wikipedia_url)))

        if term.wikipedia_pageid:
            g.add((term_ref, JOCONDELAB_NS.wikipediaPageID, Literal(term.wikipedia_pageid)))

        if term.wikipedia_revision_id:
            g.add((term_ref, JOCONDELAB_NS.wikipediaPageRevision, Literal(term.wikipedia_revision_id)))

        if term.alternative_wikipedia_url:
            g.add((term_ref, JOCONDELAB_NS.alternativeWikipediaPage, URIRef(term.alternative_wikipedia_url)))

        if term.alternative_wikipedia_pageid:
            g.add((term_ref, JOCONDELAB_NS.alternativeWikipediaPageID, Literal(term.alternative_wikipedia_pageid)))
        
        if term.dbpedia_uri:
            g.add((term_ref, JOCONDELAB_NS.dbpediaResource, URIRef(term.dbpedia_uri)))

        if term.validation_date:
            g.add((term_ref, JOCONDELAB_NS.linkValidationDate, Literal(term.validation_date)))

        if term.validator:
            g.add((term_ref, JOCONDELAB_NS.linkValidator, Literal(term.validator.username)))

        if term.parent:
            g.add((term_ref, SKOS.broader, URIRef(term.parent.uri)))

        for alt_label in term.alternative_labels.all():
            g.add((term_ref, SKOS.altLabel, Literal(alt_label.label, lang=alt_label.lang)))

        for db_field in term.dbpedia_fields.all():
            dbp_field_bnode = BNode()
            g.add((term_ref, JOCONDELAB_NS.dbpediaField, dbp_field_bnode))
            g.add((dbp_field_bnode, RDF.type, JOCONDELAB_NS.DbpediaField))
            g.add((dbp_field_bnode, DC.language, Literal(db_field.language_code)))
            g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldUri, URIRef(db_field.dbpedia_uri)))
            if db_field.thumbnail:
                g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldThumbnail, URIRef(db_field.thumbnail)))
            if db_field.label:
                g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldLabel, Literal(db_field.label, lang=db_field.language_code)))
            if db_field.abstract:
                g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldAbstract, Literal(db_field.abstract, lang=db_field.language_code)))

        for dbp_year in term.years.all():
            dbp_year_bnode = BNode()
            g.add((term_ref, JOCONDELAB_NS.dbpediaYear, dbp_year_bnode))
            g.add((dbp_year_bnode, RDF.type, JOCONDELAB_NS.YearInfo))
            g.add((dbp_year_bnode, JOCONDELAB_NS.YearInfoStart, Literal(dbp_year.start_year)))
            g.add((dbp_year_bnode, JOCONDELAB_NS.YearInfoEnd, Literal(dbp_year.end_year)))

        for dbp_geo in term.geo.all():
            dbp_geo_bnode = BNode()
            g.add((term_ref, JOCONDELAB_NS.dbpediaGeo, dbp_geo_bnode))
            g.add((dbp_geo_bnode, RDF.type, JOCONDELAB_NS.DbpediaGeo))
            g.add((dbp_geo_bnode, GEO.lat, Literal(str(dbp_geo.latitude), datatype=XSD.double)))
            g.add((dbp_geo_bnode, GEO.long, Literal(str(dbp_geo.longitude), datatype=XSD.double)))
        
        return g


    def get_notice_uri(self, notice):
        return JOCONDELAB_DATA_NS + "notice/" + notice.ref

    def export_notice(self, g, notice):
        notice_uri = self.get_notice_uri(notice)
        notice_ref = URIRef(notice_uri)
        g.add((notice_ref, RDF.type, JOCONDELAB_NS.Notice))
        for fieldName in [
            'ref', 'adpt', 'appl', 'aptn', 'attr', 'autr', 'bibl',
            'comm', 'contact', 'coor', 'copy', 'dacq', 'data',
            'dation', 'ddpt', 'decv', 'deno', 'depo', 'desc', 'desy',
            'dims', 'dmaj', 'dmis', 'domn', 'drep', 'ecol', 'epoq',
            'etat', 'expo', 'gene', 'geohi', 'hist', 'image', 'insc',
            'inv', 'label', 'labo', 'lieux', 'loca', 'loca2', 'mill',
            'milu', 'mosa', 'msgcom', 'museo', 'nsda', 'onom', 'paut',
            'pdat', 'pdec', 'peoc', 'peri', 'peru', 'phot', 'pins',
            'plieux', 'prep', 'puti', 'reda', 'refim', 'repr', 'srep',
            'stat', 'tech', 'tico', 'titr', 'util', 'video', 'www'
        ]:
            fieldValue = getattr(notice, fieldName)
            if fieldValue:
                g.add((notice_ref, getattr(JOCONDELAB_NS, "notice"+fieldName.capitalize()), Literal(fieldValue)))

        termNbs = NoticeTerm.objects.filter(notice=notice).count()
        totalTermNb = 0
        for fieldName in ['autr', 'domn', 'ecol', 'epoq', 'lieux', 'peri', 'repr', 'srep']:
            
            termQuery = getattr(notice, fieldName + "_terms")
            for term in termQuery.all():
                if term.thesaurus.label.lower() == fieldName:
                    totalTermNb += 1
                    g.add((notice_ref, getattr(JOCONDELAB_NS, "notice"+fieldName.capitalize()+"Term"), URIRef(term.uri)))

        if totalTermNb != termNbs:
            logger.critical("Bad term count for notice %s should be %s and is %s", notice_uri, termNbs, totalTermNb)

        for notice_image in notice.images.all():
            notice_image_bnode = BNode()
            g.add((notice_ref, JOCONDELAB_NS.noticeImage, notice_image_bnode))
            g.add((notice_image_bnode, RDF.type, JOCONDELAB_NS.NoticeImage))
            g.add((notice_image_bnode, JOCONDELAB_NS.noticeImageUrl, URIRef(notice_image.url)))
            g.add((notice_image_bnode, JOCONDELAB_NS.noticeImageOrder, Literal(notice_image.order)))
            g.add((notice_image_bnode, JOCONDELAB_NS.noticeImageIsMain, Literal(notice_image.main)))
            g.add((notice_image_bnode, JOCONDELAB_NS.noticeImageIsLarge, Literal(notice_image.large)))

        for notice_year in notice.years.all():
            notice_year_bnode = BNode()
            g.add((notice_ref, JOCONDELAB_NS.noticeYear, notice_year_bnode))
            g.add((notice_year_bnode, RDF.type, JOCONDELAB_NS.YearInfo))
            g.add((notice_year_bnode, JOCONDELAB_NS.YearInfoStart, Literal(notice_year.start_year)))
            g.add((notice_year_bnode, JOCONDELAB_NS.YearInfoEnd, Literal(notice_year.end_year)))

        return g


    def get_contributed_term_uri(self, term):
        return JOCONDELAB_DATA_NS + "contributed_term/" + str(term.id)

    def export_contributed_term(self, g, term):
        
        term_uri = self.get_contributed_term_uri(term)

        term_ref = URIRef(term_uri)
        g.add((term_ref, RDF.type, JOCONDELAB_NS.ContributedTerm))
        g.add((term_ref, JOCONDELAB_NS.dbpediaResource, URIRef(term.dbpedia_uri)))
        if term.dbpedia_language:
            g.add((term_ref, JOCONDELAB_NS.dbpediaLanguage, Literal(term.dbpedia_language)))

        for db_field in term.dbpedia_fields.all():
            dbp_field_bnode = BNode()
            g.add((term_ref, JOCONDELAB_NS.dbpediaField, dbp_field_bnode))
            g.add((dbp_field_bnode, RDF.type, JOCONDELAB_NS.DbpediaField))
            g.add((dbp_field_bnode, DC.language, Literal(db_field.language_code)))
            g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldUri, URIRef(db_field.dbpedia_uri)))
            if db_field.thumbnail:
                g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldThumbnail, URIRef(db_field.thumbnail)))
            if db_field.label:
                g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldLabel, Literal(db_field.label, lang=db_field.language_code)))
            if db_field.abstract:
                g.add((dbp_field_bnode, JOCONDELAB_NS.dbpediaFieldAbstract, Literal(db_field.abstract, lang=db_field.language_code)))

        return g

    def export_contribution(self, g, contribution):

        contribution_uri = JOCONDELAB_DATA_NS + "contribution/" + str(contribution.id)
        contribution_ref = URIRef(contribution_uri)
        g.add((contribution_ref, RDF.type, JOCONDELAB_NS.Contribution))
        g.add((contribution_ref, JOCONDELAB_NS.contributionTerm, URIRef(self.get_contributed_term_uri(contribution.term))))
        if contribution.thesaurus:
            g.add((contribution_ref, JOCONDELAB_NS.contributionThesaurus, URIRef(contribution.thesaurus.uri)))
        g.add((contribution_ref, JOCONDELAB_NS.contributionNotice, URIRef(self.get_notice_uri(contribution.notice))))
        g.add((contribution_ref, JOCONDELAB_NS.contributionCount, Literal(contribution.contribution_count)))

        return g


    def handle(self, *args, **options):

        if len(args) != 1:
            raise CommandError("This command takes exactly one argument")

        self.newline = options.get("newline", False)
        self.limit = options.get("limit", -1)

        filepath = args[0]

        bzip2 = options.get('bzip2', False)
        gzip_opt = options.get('gzip', False)

        if bzip2 and not filepath.endswith(".bz2"):
            filepath += ".bz2"
        elif gzip_opt and not filepath.endswith(".gz"):
            filepath += ".gz"

        open_method = None
        open_args = []

        if bzip2:
            open_method = bz2.BZ2File
            open_args = [filepath, 'wb', 9]
        elif gzip_opt:
            open_method = gzip.GzipFile
            open_args = [filepath, 'wb', 9]
        else:
            #open_method = codecs.open
            open_method = open
            #open_args = [filepath, 'wb', "utf-8"]
            open_args = [filepath, 'wb']

        term_query = Term.objects.select_related('thesaurus', 'alternative_labels', 'dbpedia_fields').order_by('id')

        if self.limit >= 0:
            notice_term_query_filter = Q()
            for klass in [NoticeTerm, AutrNoticeTerm, DomnNoticeTerm, EcolNoticeTerm, EpoqNoticeTerm, LieuxNoticeTerm, PeriNoticeTerm, ReprNoticeTerm, SrepNoticeTerm]:
                notice_term_query = klass.objects.filter(notice__id__in=Notice.objects.order_by('id')[:self.limit].values_list('id', flat=True))
                notice_term_query_filter = notice_term_query_filter | Q(id__in=notice_term_query.values_list('term__id', flat=True))
            term_query = term_query.filter(notice_term_query_filter)


        with open_method(*open_args) as dest_file:
            self.export_namespaces(dest_file)
            for query, namespaces, build_method in [
                (Thesaurus.objects.all(), 'thesaurus', self.export_thesaurus),
                (term_query, 'term', self.export_term),
                (Notice.objects.order_by('id').select_related().all(), 'notice', self.export_notice),
                (ContributedTerm.objects.select_related().order_by('id').all(), 'contributed_term', self.export_contributed_term),
                (Contribution.objects.select_related().order_by('id').all(), 'contribution', self.export_contribution)
            ]:
                self.export_objects(query, namespaces, build_method, dest_file)


# list of objects

# User

# Notice

# Term

# TermLabel

# Thesaurus

# NoticeImage
# NoticeTerm

# Country

# DbpediaFields

# TermLinks

# DbpediaYears
# DbpediaGeo

# ContributedTerm
# ContributedFields
# Contribution
# ContributableTerm
# TagcloudTerm
# NoticeYears

# TERM_URL_STATUS_CHOICES
# TERM_URL_STATUS_CHOICES_TRANS
# TERM_URL_STATUS_DICT
# TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES_TRANS
# TERM_WK_LINK_SEMANTIC_LEVEL_DICT


# export : thesaurus,



# ref
# adpt
# appl
# aptn
# attr
# bibl
# comm
# contact
# coor
# copy
# dacq
# data
# dation
# ddpt
# decv
# deno
# depo
# desc
# desy
# dims
# dmaj
# dmis
# drep
# etat
# expo
# gene
# geohi
# hist
# image
# insc
# inv
# label
# labo
# loca
# loca2
# mill
# milu
# mosa
# msgcom
# museo
# nsda
# onom
# paut
# pdat
# pdec
# peoc
# peru
# phot
# pins
# plieux
# prep
# puti
# reda
# refim
# stat
# tech
# tico
# titr
# util
# video
# www
# autr
# domn
# ecol
# epoq
# lieux
# peri
# repr
# srep


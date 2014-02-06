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
Created on Jun 8, 2013

@author: ymh
'''

from core import settings
from django.db import models
from django.utils.translation import ugettext as _
from mptt.models import MPTTModel, TreeForeignKey
import datetime
import logging
from core.models import User

logger = logging.getLogger(__name__)


TERM_URL_STATUS_CHOICES = (
    (0, "null_result"),
    (1, "redirection"),
    (2, "homonyme"),
    (3, "match"),
    (4, "unsematized"),
)

TERM_URL_STATUS_CHOICES_TRANS = (
    (0, _("null_result")),
    (1, _("redirection")),
    (2, _("homonyme")),
    (3, _("match")),
    (4, _("unsematized")),
)

TERM_URL_STATUS_DICT = {
    "null_result":0,
    "redirection":1,
    "homonyme":2,
    "match":3,
    "unsemantized":4,
}

TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES = (
    (0, "--"),
    (1, "EE"),
    (2, "EI"),
    (3, "BM"),
    (4, "NM")
)

TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES_TRANS = (
    (0, _("--")),
    (1, _("EE")),
    (2, _("EI")),
    (3, _("BM")),
    (4, _("NM"))
)

TERM_WK_LINK_SEMANTIC_LEVEL_DICT = {
    "--" : 0,
    "EE" : 1,
    "EI" : 2,
    "BM" : 3,
    "NM" : 4
}

   
class Thesaurus(models.Model):
    label = models.CharField(max_length=128, unique=True, blank=False, null=False, db_index=True)
    title = models.CharField(max_length=1024, unique=False, blank=False, null=False, db_index=False)
    description = models.TextField(blank=True, null=True)    
    uri = models.URLField(max_length=2048, blank=True, null=True, db_index=True)
    
    class Meta:
        app_label = 'core'
        ordering = ['label']
        
    def __unicode__(self):
        return self.label


class Term(MPTTModel):
    label = models.CharField(max_length=1024, unique=False, blank=False, null=False, db_index=True)
    lang = models.CharField(max_length=128, unique=False, blank=True, null=True, db_index=True)
    uri = models.URLField(max_length=2048, blank=True, null=True, db_index=True)
    normalized_label = models.CharField(max_length=1024, unique=False, blank=False, null=False, db_index=True, editable=False)
    wp_label = models.CharField(max_length=1024, unique=False, blank=True, null=True, db_index=True)
    wp_alternative_label = models.CharField(max_length=1024, unique=False, blank=True, null=True, db_index=True)
    thesaurus = models.ForeignKey(Thesaurus, blank=False, null=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    wikipedia_url = models.URLField(max_length=2048, blank=True, null=True, db_index=True)
    wikipedia_pageid = models.BigIntegerField(unique=False, blank=True, null=True, db_index=True)
    wikipedia_revision_id = models.BigIntegerField(unique=False, blank=True, null=True)
    alternative_wikipedia_url = models.URLField(max_length=2048, blank=True, null=True, db_index=True)
    alternative_wikipedia_pageid = models.BigIntegerField(unique=False, blank=True, null=True, db_index=True)
    url_status = models.IntegerField(choices=TERM_URL_STATUS_CHOICES_TRANS, blank=True, null=True, default=None, db_index=True)
    link_semantic_level = models.IntegerField(choices=TERM_WK_LINK_SEMANTIC_LEVEL_CHOICES_TRANS, blank=True, null=True, default=None, db_index=True)
    dbpedia_uri = models.URLField(max_length=2048, blank=True, null=True, db_index=True)
    validation_date = models.DateTimeField(null=True, blank=True, serialize=False)
    validated = models.BooleanField(default=False, db_index=True)
    validator = models.ForeignKey(User, null=True, blank=True, serialize=False)
    wikipedia_edition = models.BooleanField(default=False, blank=False, null=False)
    
    nb_notice = models.IntegerField(blank=False, null=False, default=0, db_index=True, editable=False)
    notices = models.ManyToManyField('core.Notice', related_name="terms+", through="core.NoticeTerm")
    nb_illustrated_notice = models.IntegerField(blank=False, null=False, default=0, db_index=True, editable=False)
    
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    
    @property
    def children_with_descendants(self):
        return self.children.extra(where=['(rght-lft) > 1'])
    
    @property
    def alternative_labels_str(self):
        return " | ".join([l.label for l in self.alternative_labels.all() if l.label != self.label])
    
    @property
    def alternative_labels_list(self):
        return [l.label for l in self.alternative_labels.all() if l.label != self.label]
    
    @property
    def wikipedia_language_version(self):
        if not self.wikipedia_url:
            return None
        for lang, urls in settings.WIKIPEDIA_URLS.iteritems():  # @UndefinedVariable
            if self.wikipedia_url.startswith(urls['base_url']):
                return lang
        return None
    
    @property
    def wikipedia_revision_permalink(self):
        tmpl_str = settings.WIKIPEDIA_URLS.get(self.wikipedia_language_version, {}).get('permalink_tmpl',None)  # @UndefinedVariable
        if tmpl_str:            
            return tmpl_str % (unicode(self.wikipedia_revision_id))
        else:
            return None
    
    @property
    def url_status_text(self):
        return TERM_URL_STATUS_CHOICES[self.url_status][1]

    @property
    def url_status_text_trans(self):
        return TERM_URL_STATUS_CHOICES_TRANS[self.url_status][1]
        
    def validate(self, user):
        if not self.validated:
            self.validation_date = datetime.datetime.utcnow()
            self.validated = True
            self.validator = user
            self.save()
    
    def unvalidate(self):
        if self.validated:
            self.validated = False
            self.validator = None
            self.validation_date = None
            self.save()
    
    def __unicode__(self):
        return self.label
    
    class Meta:
        app_label = 'core'
        
    class MPTTMeta:
        order_insertion_by = ['normalized_label']

class TermLabel(models.Model):
    label = models.CharField(max_length=1024, unique=False, blank=False, null=False, db_index=True)
    lang = models.CharField(max_length=128, unique=False, blank=True, null=True, db_index=True)
    term = models.ForeignKey(Term, blank=False, null=False, db_index=True, related_name="alternative_labels")
    
    class Meta:
        app_label = 'core'

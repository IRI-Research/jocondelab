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
from django.db import models
from django.db.models import signals
from django.dispatch import receiver

from core import settings
from core.models.term import Term


# Create your models here.
class Notice(models.Model):
    
    ref         = models.CharField(max_length=20, null=True, blank=True, unique=True)
    adpt        = models.TextField(null=True, blank=True)
    appl        = models.CharField(max_length=1024, null=True, blank=True)
    aptn        = models.TextField(null=True, blank=True)
    attr        = models.TextField(null=True, blank=True)
    autr        = models.CharField(max_length=1024, null=True, blank=True)
    autr_terms  = models.ManyToManyField(Term, related_name="autr+", limit_choices_to = {'thesaurus__label': 'autr'}, through='AutrNoticeTerm')
    bibl        = models.TextField(null=True, blank=True)
    comm        = models.TextField(null=True, blank=True)
    contact     = models.CharField(max_length=1024, null=True, blank=True)
    coor        = models.CharField(max_length=1024, null=True, blank=True)
    copy        = models.CharField(max_length=1024, null=True, blank=True)
    dacq        = models.CharField(max_length=1024, null=True, blank=True)
    data        = models.CharField(max_length=512, null=True, blank=True)
    dation      = models.CharField(max_length=512, null=True, blank=True)
    ddpt        = models.CharField(max_length=512, null=True, blank=True)
    decv        = models.CharField(max_length=1024, null=True, blank=True)
    deno        = models.CharField(max_length=1024, null=True, blank=True)
    depo        = models.CharField(max_length=1024, null=True, blank=True)
    desc        = models.TextField(null=True, blank=True)
    desy        = models.CharField(max_length=512, null=True, blank=True)
    dims        = models.CharField(max_length=2048, null=True, blank=True)
    dmaj        = models.DateField(null=True, blank=True)
    dmis        = models.DateField(null=True, blank=True)
    domn        = models.CharField(max_length=512, null=True, blank=True)
    domn_terms  = models.ManyToManyField(Term, related_name="domn+", limit_choices_to = {'thesaurus__label': 'domn'}, through='DomnNoticeTerm') 
    drep        = models.CharField(max_length=1024, null=True, blank=True)
    ecol        = models.CharField(max_length=512, null=True, blank=True)
    ecol_terms  = models.ManyToManyField(Term, related_name="ecol+", limit_choices_to = {'thesaurus__label': 'ecol'}, through='EcolNoticeTerm')
    epoq        = models.CharField(max_length=512, null=True, blank=True)
    epoq_terms  = models.ManyToManyField(Term, related_name="epoq+", limit_choices_to = {'thesaurus__label': 'epoq'}, through='EpoqNoticeTerm')
    etat        = models.TextField(null=True, blank=True)
    expo        = models.TextField(null=True, blank=True)
    gene        = models.CharField(max_length=1024, null=True, blank=True) 
    geohi       = models.CharField(max_length=1024, null=True, blank=True)
    hist        = models.TextField(null=True, blank=True)
    image       = models.BooleanField()
    insc        = models.CharField(max_length=1024, null=True, blank=True)
    inv         = models.CharField(max_length=2048, null=True, blank=True)
    label       = models.CharField(max_length=512, null=True, blank=True)
    labo        = models.CharField(max_length=1024, null=True, blank=True)
    lieux       = models.CharField(max_length=1024, null=True, blank=True)
    lieux_terms = models.ManyToManyField(Term, related_name="lieux+", limit_choices_to = {'thesaurus__label': 'lieux'}, through='LieuxNoticeTerm')
    loca        = models.CharField(max_length=512, null=True, blank=True)
    loca2       = models.CharField(max_length=512, null=True, blank=True)
    mill        = models.CharField(max_length=512, null=True, blank=True)
    milu        = models.CharField(max_length=512, null=True, blank=True)
    mosa        = models.CharField(max_length=512, null=True, blank=True)
    msgcom      = models.TextField(null=True, blank=True)
    museo       = models.CharField(max_length=512, null=True, blank=True)
    nsda        = models.CharField(max_length=512, null=True, blank=True)
    onom        = models.TextField(null=True, blank=True)
    paut        = models.TextField(null=True, blank=True)
    pdat        = models.TextField(null=True, blank=True)
    pdec        = models.TextField(null=True, blank=True)
    peoc        = models.CharField(max_length=512, null=True, blank=True)
    peri        = models.CharField(max_length=512, null=True, blank=True)
    peri_terms  = models.ManyToManyField(Term, related_name="peri+", limit_choices_to = {'thesaurus__label': 'peri'}, through='PeriNoticeTerm')
    peru        = models.CharField(max_length=1024, null=True, blank=True)
    phot        = models.CharField(max_length=1024, null=True, blank=True)
    pins        = models.TextField(null=True, blank=True)
    plieux      = models.TextField(null=True, blank=True)
    prep        = models.TextField(null=True, blank=True)
    puti        = models.TextField(null=True, blank=True)
    reda        = models.CharField(max_length=1024, null=True, blank=True)    
    refim       = models.CharField(max_length=2048, null=True, blank=True)
    repr        = models.TextField(null=True, blank=True)
    repr_terms  = models.ManyToManyField(Term, related_name="repr+", limit_choices_to = {'thesaurus__label': 'repr'}, through='ReprNoticeTerm')
    srep        = models.CharField(max_length=1024, null=True, blank=True)
    srep_terms  = models.ManyToManyField(Term, related_name="srep+", limit_choices_to = {'thesaurus__label': 'srep'}, through='SrepNoticeTerm')
    stat        = models.CharField(max_length=1024, null=True, blank=True)
    tech        = models.CharField(max_length=2048, null=True, blank=True)
    tico        = models.TextField(null=True, blank=True)
    titr        = models.TextField(null=True, blank=True)
    util        = models.CharField(max_length=1024, null=True, blank=True)
    video       = models.CharField(max_length=2048, null=True, blank=True)
    www         = models.CharField(max_length=512, null=True, blank=True)
    
    def thumbnails(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            return [img for img in self.images.all() if img.url.split('.')[-2].endswith("_v")]
                      
        return locals()
       
    thumbnails = property(**thumbnails())
    
    def large_images(): #@NoSelf
        doc = """Docstring""" #@UnusedVariable
       
        def fget(self):
            return [img.url for img in self.images.filter(large=True).order_by('order')]
                      
        return locals()
    
    large_images = property(**large_images())

    class Meta:
        app_label = 'core'

class NoticeImage(models.Model):
    relative_url = models.URLField(max_length='1024', null=False, blank=False, unique=False)
    notice = models.ForeignKey(Notice, related_name="images")
    order = models.IntegerField(default=0, null=True)
    large = models.BooleanField(default=True)
    main = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'core'
        unique_together = (("relative_url", "notice"),)

    
    @property
    def url(self):
        return settings.JOCONDE_IMAGE_BASE_URL + self.relative_url


class NoticeTerm(models.Model):
    
    notice = models.ForeignKey(Notice)
    term   = models.ForeignKey(Term)
    
    #optionnal rdf graph uri describing the relationship
    graph  = models.URLField(max_length=2048, null=True, blank=True)
    
    class Meta:
        app_label = 'core'


class AutrNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'
        
class DomnNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'
        
class EcolNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'
        
class EpoqNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'

class LieuxNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'

class PeriNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'

class ReprNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'

class SrepNoticeTerm(NoticeTerm):
    class Meta:
        app_label = 'core'

def increment_nb_notice(term, inc):
    term.nb_notice = term.nb_notice + inc
    term.save
    
@receiver(signals.post_save, sender=NoticeTerm)
def notice_term_created(sender, **kwargs):
    instance = kwargs.get('instance', None)
    created = kwargs.get('created', None)
    if instance is None or not created:
        return
    increment_nb_notice(instance.term, 1)

@receiver(signals.post_delete, sender=NoticeTerm)
def notice_term_deleted(sender, **kwargs):
    instance = kwargs.get('instance', None)
    if instance is None:
        return
    increment_nb_notice(instance.term, -1)

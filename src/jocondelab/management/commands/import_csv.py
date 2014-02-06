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
Created on Jun 10, 2013

@author: ymh
'''

from core.import_processor import (CharFieldProcessor, DateFieldProcessor, 
    BooleanFieldProcessor, TermProcessor, TrimCharFieldProcessor, 
    VideoFieldProcessor)
from core.models import (Notice, AutrNoticeTerm, DomnNoticeTerm, EcolNoticeTerm, 
    EpoqNoticeTerm, LieuxNoticeTerm, PeriNoticeTerm, ReprNoticeTerm)
from core.models.notice import SrepNoticeTerm
from core.settings import (AUTR_CONTEXT, DOMN_CONTEXT, ECOL_CONTEXT, EPOQ_CONTEXT, 
    LIEUX_CONTEXT, PERI_CONTEXT, REPR_CONTEXT, SREP_CONTEXT)
from core.utils import show_progress
from django.core.management import BaseCommand
from django.db import transaction, reset_queries
from optparse import make_option
import csv
import datetime
import logging
import os.path
import sys

logger = logging.getLogger(__name__)

NOTICE_FIELD_PROCESSORS = {
    'ref'  : TrimCharFieldProcessor('ref'),
    'dmaj' : DateFieldProcessor('dmaj'),
    'dmis' : DateFieldProcessor('dmis'),
    'image': BooleanFieldProcessor('image'),
    'video_list' : VideoFieldProcessor('video'),
    'autr_terms' : TermProcessor('autr' , AUTR_CONTEXT , AutrNoticeTerm),
    'domn_terms' : TermProcessor('domn' , DOMN_CONTEXT , DomnNoticeTerm),
    'ecol_terms' : TermProcessor('ecol' , ECOL_CONTEXT , EcolNoticeTerm),
    'epoq_terms' : TermProcessor('epoq' , EPOQ_CONTEXT , EpoqNoticeTerm),
    'lieux_terms': TermProcessor('lieux', LIEUX_CONTEXT, LieuxNoticeTerm),
    'peri_terms' : TermProcessor('peri' , PERI_CONTEXT , PeriNoticeTerm),    
    'repr_terms' : TermProcessor('repr' , REPR_CONTEXT , ReprNoticeTerm, re_sub = None, re_split = "[\;\,\:\(\)\#]"),
    'srep_terms' : TermProcessor('srep' , SREP_CONTEXT , SrepNoticeTerm, re_sub = None, re_split = "[\;\,\:\(\)\#]"),
}

POST_NOTICE_FIELDS = ['video_list', 'autr_terms','domn_terms','ecol_terms','epoq_terms','lieux_terms','peri_terms','repr_terms', 'srep_terms']
DEFAULT_FIELD_PROCESSOR_KLASS = CharFieldProcessor

class Command(BaseCommand):

    args = "csv_file"
    
    help = "Import Mistral csv file"

    option_list = BaseCommand.option_list + (
        make_option('--check-id',
            action= 'store_true',
            dest= 'check_id',
            default= False,
            help= 'check a notice id before trying to insert it, may be a lot slower' 
        ),
        make_option('-n', '--max-lines',
            dest= 'max_lines',
            type='int',
            default= sys.maxint,
            help= 'max number of line to process, -1 process all file' 
        ),
        make_option('-b', '--batch-size',
            dest= 'batch_size',
            type='int',
            default= 50,
            help= 'number of object to import in bulk operations' 
        ),
        make_option('-e', '--encoding',
            dest= 'encoding',
            default= 'latin1',
            help= 'csv files encoding' 
        ),
        make_option('--skip',
            dest= 'skip',
            type='int',
            default= 0,
            help= 'number of entry to skip' 
        ),
        make_option('--stop',
            dest= 'cont',
            action= 'store_false',
            default= True,
            help= 'stop on error' 
        ),
        make_option('--link',
            dest= 'link_only',
            action= 'store_true',
            default= False,
            help= 'do not import csv' 
        ),
    )

    def __safe_get(self, dict_arg, key, conv = lambda x: x, default= None):
        val = dict_arg.get(key, default)
        return conv(val) if val else default

    def __safe_decode(self, s):
        if not isinstance(s, basestring):
            return s
        try:
            return s.decode('utf8')
        except:
            try:
                return s.decode('latin1')
            except:
                return s.decode('utf8','replace')


    def __init__(self):
        super(Command, self).__init__()
        
    def handle(self, *args, **options):
        
        filepath = os.path.abspath(args[0])
        self.stdout.write("Importing %s" % filepath)
        self.encoding = options.get('encoding', "latin-1")
        self.link_only = options.get('link_only', False)
        
        max_lines = options.get('max_lines', sys.maxint)        
        
        self.stdout.write("Calculating size")
        with open(filepath,'rb') as csv_file:
            dialect = csv.Sniffer().sniff(csv_file.read(1024))
            dialect.doublequote = True
            dialect.delimiter = '\t'
            dialect.quoting = csv.QUOTE_NONE
            csv_file.seek(0)
            
            reader = csv.DictReader(csv_file, dialect=dialect)
            
            for i,_ in enumerate(reader):
                if i >= (max_lines-1):
                    break
                        
        objects_buffer = {}
        nb_lines = min(max_lines, i+1)
        
        self.stdout.write("Importing %d lines" % (nb_lines))
        batch_size = options.get('batch_size', 5000)
        cont_on_error = options.get('cont', True)
        
        if not self.link_only:
            with open(filepath,'rb') as csvfile:
                reader = csv.DictReader(csvfile, dialect=dialect, restkey="EXTRA")
                writer = None
                
                for i,row in enumerate(reader):
                    try:
                        if i+1 > nb_lines:
                            break
                        
                        writer = show_progress(i+1, nb_lines, u"Processing line %s" % (row['REF'].strip()), 50, writer)
                        
                        def safe_decode(val, encoding):
                            if val:
                                return val.decode(encoding)
                            else:
                                return val
                                                            
                        row = dict([(safe_decode(key, self.encoding), safe_decode(value, self.encoding)) for key, value in row.items()])
    
                        notice_obj = Notice()
                        objects_buffer.setdefault(Notice, []).append(notice_obj)
                        
                        for k,v in row.items():
                            processor = NOTICE_FIELD_PROCESSORS.get(k.lower(), DEFAULT_FIELD_PROCESSOR_KLASS(k.lower())) #TODO : put default processor
                            new_objs = processor.process(notice_obj, v) if processor else None
                            if new_objs:
                                objects_buffer.update(new_objs)
                        
                        if not ((i+1)%batch_size):
                            for klass, obj_list in objects_buffer.iteritems():
                                klass.objects.bulk_create(obj_list)
                            objects_buffer = {}
                            reset_queries()
                    except Exception as e:
                        error_msg = "%s - Error treating line %d/%d: id %s : %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),i+1, reader.line_num, row['REF'] if (row and 'REF' in row and row['REF']) else 'n/a', repr(e) )
                        logger.exception(error_msg)
                        if not cont_on_error:
                            raise
                        
            if objects_buffer:
                try:
                    for klass, obj_list in objects_buffer.iteritems():
                        klass.objects.bulk_create(obj_list)
                    objects_buffer = {}
                    reset_queries()
                except Exception as e:
                    error_msg = "%s - Error treating line : %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), repr(e) )
                    logger.exception(error_msg)
                    if not cont_on_error:
                        raise


        transaction.enter_transaction_management()
        transaction.managed()
        
        notice_count = Notice.objects.count()
        
        self.stdout.write("Processing %d notices" % notice_count)

        writer = None        
        for i,notice_obj in enumerate(Notice.objects.all().order_by('ref').iterator()):
            writer = show_progress(i+1, notice_count, u"Processing notice %s" % notice_obj.ref, 50, writer)
            for field in POST_NOTICE_FIELDS:
                processor = NOTICE_FIELD_PROCESSORS.get(field, DEFAULT_FIELD_PROCESSOR_KLASS(field))
                new_objs = processor.process(notice_obj, None) if processor else None
                if new_objs:
                    for k,v in new_objs.iteritems():                        
                        objects_buffer.setdefault(k,[]).extend(v)
            if not ((i+1)%batch_size):
                for _, obj_list in objects_buffer.iteritems():
                    map(lambda o: o.save(), obj_list)
                objects_buffer = {}
                transaction.commit()
                reset_queries()

        if objects_buffer:
            try:
                for _, obj_list in objects_buffer.iteritems():
                    map(lambda o: o.save(), obj_list)
                objects_buffer = {}
                transaction.commit()
                reset_queries()
            except Exception as e:
                error_msg = "%s - Error treating line: %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), repr(e) )
                logger.exception(error_msg)

        transaction.leave_transaction_management()
        
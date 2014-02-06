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
Created on May 29, 2013

@author: ymh
'''
from django.core.management.base import BaseCommand
from django.db import connections
from rdflib import plugin, ConjunctiveGraph
from rdflib.store import Store
from sqlalchemy import and_
import os.path

class Command(BaseCommand):
    args = "<path_to_skos_file path_to_skos_file>..."
    help = "import skos ref in rdflib alchemy store"
    
    def __init__(self):
        super(Command, self).__init__()
        self.ident = "jocondelab"
        #'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        #'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        #'USER': '',
        #'PASSWORD': '',
        #'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        #'PORT': ''
        db_settings = connections['default'].settings_dict
        sa_db_settings = {
            'engine': 'postgresql+psycopg2' if db_settings['ENGINE'] == "django.db.backends.postgresql_psycopg2" else db_settings['ENGINE'],
            'user': db_settings['USER'],
            'password': db_settings['PASSWORD'],
            'port': db_settings['PORT'] if db_settings['PORT'] else "5432",
            'host': db_settings['HOST'] if db_settings['HOST'] else "localhost",
            'name': db_settings['NAME']             
        } 
        self.connect_config = "%(engine)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s"%sa_db_settings 
        self.store = plugin.get("SQLAlchemy", Store)(identifier=self.ident)
        self.graph = ConjunctiveGraph(self.store, identifier=self.ident)
        self.graph.open(self.connect_config, create=True)

    def handle(self, *args, **options):
        #import pydevd #@UnresolvedImport
        #pydevd.settrace(suspend=True)
        
        for skos_path, public_id in zip(args[::2],args[1::2]):
            filepath = os.path.abspath(skos_path)
            self.stdout.write("Importing %s" % filepath)
            
            self.graph.parse(filepath, publicID=public_id, format='xml')
            self.stdout.write("graph size %d" % len(self.graph))
            self.graph.commit()

        self.graph.close()        
        self.store = plugin.get("SQLAlchemy", Store)(identifier=self.ident)
        self.graph = ConjunctiveGraph(self.store, identifier=self.ident)
        self.graph.open(self.connect_config, create=False)
        
        self.stdout.write("correct alt labels")
        litteral_statements = self.store.tables['literal_statements']
        with self.store.engine.connect() as connection:
            q = litteral_statements.select().where(litteral_statements.c.predicate == "http://www.w3.org/2004/02/skos/core#altLabel")
            for row in connection.execute(q):
                if row['object'] and row['object'] != row['object'].strip():                  
                    u_q = litteral_statements.update().where(and_(
                        litteral_statements.c.subject == row['subject'],
                        litteral_statements.c.predicate == row['predicate'],
                        litteral_statements.c.object == row['object'],
                        litteral_statements.c.context == row['context'],
                        litteral_statements.c.termComb == row['termcomb'],
                        litteral_statements.c.objLanguage == row['objlanguage'],
                        litteral_statements.c.objDatatype == row['objdatatype']
                        )).values(object = row['object'].strip() )
                    #u_q_compiled = u_q.compile()
                    #self.stdout.write("UPDATE QUERY for %s : %s : %s - %s" % (row['subject'], row['object'], str(u_q_compiled), repr(u_q_compiled.params)))
                    connection.execute(u_q)

        self.stdout.write("graph size %d" % len(self.graph))
        self.stdout.write("graph contexts %s" % repr([g for g in self.graph.contexts()]))

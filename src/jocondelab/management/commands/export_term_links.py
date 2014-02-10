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
import codecs
import gzip
import logging
from optparse import make_option
import csv

from django.core.management import BaseCommand
from django.core.management.base import CommandError
from django.db.models.fields.related import ForeignKey

from core.utils import show_progress
from core.models.term import Term


logger = logging.getLogger(__name__)


fields = [
    "label", "uri", "validated", "wp_label", "wp_alternative_label",
    "thesaurus__label", "thesaurus__uri", "dbpedia_uri", "wikipedia_url",
    "wikipedia_pageid", "wikipedia_revision_id", "alternative_wikipedia_url",
    "alternative_wikipedia_pageid", "url_status", "link_semantic_level",
    "wikipedia_edition"
]

class Command(BaseCommand):
    args = "file_path..."

    help = "Export jocondelab term link"

    option_list = BaseCommand.option_list + (
        make_option('-l', '--limit',
            dest='limit',
            type='int',
            default=-1,
            help='number of term to export. -1 is all (default)'
        ),
        make_option('-s', '--skip',
            dest='skip',
            type='int',
            default=0,
            help='number of term to skip before export. default 0.'
        ),
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

    def handle(self, *args, **options):

        if len(args) != 1:
            raise CommandError("This command takes exactly one argument")

        filepath = args[0]

        bzip2 = options.get('bzip2', False)
        gzip_opt = options.get('gzip', False)

        if bzip2 and not filepath.endswith(".bz2"):
            filepath += ".bz2"
        elif gzip_opt and not filepath.endswith(".gz"):
            filepath += ".gz"

        limit = options.get("limit", -1)
        skip = options.get("skip", 0)
        batch = options.get("batch", 100)
        newline = options.get("newline", False)

        qs = Term.objects.all().select_related(*[field.name for field in Term._meta.fields if isinstance(field, ForeignKey)]).order_by('uri').values_list(*fields)  # @UndefinedVariable

        if limit >= 0:
            qs = qs[skip:skip + limit]
        else:
            qs = qs[skip:]

        open_method = None
        open_args = []

        if bzip2:
            open_method = bz2.BZ2File
            open_args = [filepath, 'wb', 9]
        elif gzip_opt:
            open_method = gzip.GzipFile
            open_args = [filepath, 'wb', 9]
        else:
            open_method = codecs.open
            open_args = [filepath, 'wb', "utf-8"]

        total_records = qs.count()

        print("Total term to export : %d" % total_records)
        progress_writer = None

        with open_method(*open_args) as dest_file:

            writer = csv.writer(dest_file, dialect=csv.excel_tab)
            writer.writerow(fields)

            for n in range((total_records / batch) + 1):
                for i, r in enumerate(qs[n * batch:((n + 1) * batch)]):
                    progress_writer = show_progress(i + (n * batch) + 1,
                                                    total_records,
                                                    "Exporting term %s" % r[0],  # @IgnorePep8
                                                    40,
                                                    writer=progress_writer,
                                                    newline=newline)
                    writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else s for s in r])

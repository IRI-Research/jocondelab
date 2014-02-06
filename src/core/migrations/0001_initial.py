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
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Thesaurus'
        db.create_table(u'core_thesaurus', (  # @UndefinedVariable
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(db_index=True, max_length=2048, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Thesaurus'])  # @UndefinedVariable

        # Adding model 'Term'
        db.create_table(u'core_term', (  # @UndefinedVariable
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1024, db_index=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(db_index=True, max_length=2048, null=True, blank=True)),
            ('normalized_label', self.gf('django.db.models.fields.CharField')(max_length=1024, db_index=True)),
            ('wp_label', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=1024, null=True, blank=True)),
            ('wp_alternative_label', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=1024, null=True, blank=True)),
            ('thesaurus', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Thesaurus'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('wikipedia_url', self.gf('django.db.models.fields.URLField')(db_index=True, max_length=2048, null=True, blank=True)),
            ('wikipedia_pageid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True, null=True, blank=True)),
            ('wikipedia_revision_id', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('alternative_wikipedia_url', self.gf('django.db.models.fields.URLField')(db_index=True, max_length=2048, null=True, blank=True)),
            ('alternative_wikipedia_pageid', self.gf('django.db.models.fields.BigIntegerField')(db_index=True, null=True, blank=True)),
            ('url_status', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, db_index=True, blank=True)),
            ('dbpedia_uri', self.gf('django.db.models.fields.URLField')(db_index=True, max_length=2048, null=True, blank=True)),
            ('validation_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('validated', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('validator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jocondelab.User'], null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Term'])  # @UndefinedVariable

        # Adding model 'TermLabel'
        db.create_table(u'core_termlabel', (  # @UndefinedVariable
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1024, db_index=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, null=True, blank=True)),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(related_name='alternative_labels', to=orm['core.Term'])),
        ))
        db.send_create_signal('core', ['TermLabel'])  # @UndefinedVariable

        # Adding model 'Notice'
        db.create_table(u'core_notice', (  # @UndefinedVariable
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ref', self.gf('django.db.models.fields.CharField')(max_length=20, unique=True, null=True, blank=True)),
            ('adpt', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('appl', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('aptn', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('attr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('autr', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('bibl', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('comm', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contact', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('coor', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('copy', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('dacq', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('dation', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('ddpt', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('decv', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('deno', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('depo', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('desy', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('dims', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('dmaj', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('dmis', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('domn', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('drep', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('ecol', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('epoq', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('etat', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('expo', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('gene', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('geohi', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('hist', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('insc', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('inv', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('labo', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('lieux', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('loca', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('loca2', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('mill', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('milu', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('mosa', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('msgcom', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('museo', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('nsda', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('onom', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('paut', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pdat', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('pdec', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('peoc', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('peri', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('peru', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('phot', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('pins', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('plieux', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('prep', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('puti', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('reda', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('refim', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('repr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('srep', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('stat', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('tech', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('tico', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('titr', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('util', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True, blank=True)),
            ('video', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('www', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['Notice'])  # @UndefinedVariable

        # Adding model 'NoticeImage'
        db.create_table(u'core_noticeimage', (  # @UndefinedVariable
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('relative_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length='1024')),
            ('notice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['core.Notice'])),
        ))
        db.send_create_signal('core', ['NoticeImage'])  # @UndefinedVariable

        # Adding model 'NoticeTerm'
        db.create_table(u'core_noticeterm', (  # @UndefinedVariable
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('notice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Notice'])),
            ('term', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Term'])),
            ('graph', self.gf('django.db.models.fields.URLField')(max_length=2048, null=True, blank=True)),
        ))
        db.send_create_signal('core', ['NoticeTerm'])  # @UndefinedVariable

        # Adding model 'AutrNoticeTerm'
        db.create_table(u'core_autrnoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['AutrNoticeTerm'])  # @UndefinedVariable

        # Adding model 'DomnNoticeTerm'
        db.create_table(u'core_domnnoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['DomnNoticeTerm'])  # @UndefinedVariable

        # Adding model 'EcolNoticeTerm'
        db.create_table(u'core_ecolnoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['EcolNoticeTerm'])  # @UndefinedVariable

        # Adding model 'EpoqNoticeTerm'
        db.create_table(u'core_epoqnoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['EpoqNoticeTerm'])  # @UndefinedVariable

        # Adding model 'LieuxNoticeTerm'
        db.create_table(u'core_lieuxnoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['LieuxNoticeTerm'])  # @UndefinedVariable

        # Adding model 'PeriNoticeTerm'
        db.create_table(u'core_perinoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['PeriNoticeTerm'])  # @UndefinedVariable

        # Adding model 'ReprNoticeTerm'
        db.create_table(u'core_reprnoticeterm', (  # @UndefinedVariable
            (u'noticeterm_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.NoticeTerm'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('core', ['ReprNoticeTerm'])  # @UndefinedVariable


    def backwards(self, orm):
        # Deleting model 'Thesaurus'
        db.delete_table(u'core_thesaurus')  # @UndefinedVariable

        # Deleting model 'Term'
        db.delete_table(u'core_term')  # @UndefinedVariable

        # Deleting model 'TermLabel'
        db.delete_table(u'core_termlabel')  # @UndefinedVariable

        # Deleting model 'Notice'
        db.delete_table(u'core_notice')  # @UndefinedVariable

        # Deleting model 'NoticeImage'
        db.delete_table(u'core_noticeimage')  # @UndefinedVariable

        # Deleting model 'NoticeTerm'
        db.delete_table(u'core_noticeterm')  # @UndefinedVariable

        # Deleting model 'AutrNoticeTerm'
        db.delete_table(u'core_autrnoticeterm')  # @UndefinedVariable

        # Deleting model 'DomnNoticeTerm'
        db.delete_table(u'core_domnnoticeterm')  # @UndefinedVariable

        # Deleting model 'EcolNoticeTerm'
        db.delete_table(u'core_ecolnoticeterm')  # @UndefinedVariable

        # Deleting model 'EpoqNoticeTerm'
        db.delete_table(u'core_epoqnoticeterm')  # @UndefinedVariable

        # Deleting model 'LieuxNoticeTerm'
        db.delete_table(u'core_lieuxnoticeterm')  # @UndefinedVariable

        # Deleting model 'PeriNoticeTerm'
        db.delete_table(u'core_perinoticeterm')  # @UndefinedVariable

        # Deleting model 'ReprNoticeTerm'
        db.delete_table(u'core_reprnoticeterm')  # @UndefinedVariable


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.autrnoticeterm': {
            'Meta': {'object_name': 'AutrNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.domnnoticeterm': {
            'Meta': {'object_name': 'DomnNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.ecolnoticeterm': {
            'Meta': {'object_name': 'EcolNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.epoqnoticeterm': {
            'Meta': {'object_name': 'EpoqNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.lieuxnoticeterm': {
            'Meta': {'object_name': 'LieuxNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.notice': {
            'Meta': {'object_name': 'Notice'},
            'adpt': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'appl': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'aptn': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'attr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'autr': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'autr_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'autr+'", 'symmetrical': 'False', 'through': "orm['core.AutrNoticeTerm']", 'to': "orm['core.Term']"}),
            'bibl': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'comm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'coor': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'copy': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'dacq': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'dation': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'ddpt': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'decv': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'deno': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'depo': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'desy': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'dims': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'dmaj': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'dmis': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'domn': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'domn_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'domn+'", 'symmetrical': 'False', 'through': "orm['core.DomnNoticeTerm']", 'to': "orm['core.Term']"}),
            'drep': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'ecol': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'ecol_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'ecol+'", 'symmetrical': 'False', 'through': "orm['core.EcolNoticeTerm']", 'to': "orm['core.Term']"}),
            'epoq': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'epoq_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'epoq+'", 'symmetrical': 'False', 'through': "orm['core.EpoqNoticeTerm']", 'to': "orm['core.Term']"}),
            'etat': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'gene': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'geohi': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'hist': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'insc': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'inv': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'labo': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'lieux': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'lieux_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'lieux+'", 'symmetrical': 'False', 'through': "orm['core.LieuxNoticeTerm']", 'to': "orm['core.Term']"}),
            'loca': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'loca2': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'mill': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'milu': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'mosa': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'msgcom': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'museo': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'nsda': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'onom': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paut': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pdat': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pdec': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'peoc': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'peri': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'peri_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'peri+'", 'symmetrical': 'False', 'through': "orm['core.PeriNoticeTerm']", 'to': "orm['core.Term']"}),
            'peru': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'phot': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'pins': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'plieux': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'prep': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'puti': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'reda': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'ref': ('django.db.models.fields.CharField', [], {'max_length': '20', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'refim': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'repr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'repr_terms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'repr+'", 'symmetrical': 'False', 'through': "orm['core.ReprNoticeTerm']", 'to': "orm['core.Term']"}),
            'srep': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'stat': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'tech': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'tico': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'titr': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'util': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'www': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'})
        },
        'core.noticeimage': {
            'Meta': {'object_name': 'NoticeImage'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': "orm['core.Notice']"}),
            'relative_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': "'1024'"})
        },
        'core.noticeterm': {
            'Meta': {'object_name': 'NoticeTerm'},
            'graph': ('django.db.models.fields.URLField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Notice']"}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Term']"})
        },
        'core.perinoticeterm': {
            'Meta': {'object_name': 'PeriNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.reprnoticeterm': {
            'Meta': {'object_name': 'ReprNoticeTerm', '_ormbases': ['core.NoticeTerm']},
            u'noticeterm_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.NoticeTerm']", 'unique': 'True', 'primary_key': 'True'})
        },
        'core.term': {
            'Meta': {'object_name': 'Term'},
            'alternative_wikipedia_pageid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'alternative_wikipedia_url': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dbpedia_uri': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'db_index': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'normalized_label': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'db_index': 'True'}),
            'thesaurus': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.Thesaurus']"}),
            'uri': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'url_status': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'validated': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'validation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'validator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jocondelab.User']", 'null': 'True', 'blank': 'True'}),
            'wikipedia_pageid': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'wikipedia_revision_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'wikipedia_url': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'wp_alternative_label': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'wp_label': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '1024', 'null': 'True', 'blank': 'True'})
        },
        'core.termlabel': {
            'Meta': {'object_name': 'TermLabel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'db_index': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alternative_labels'", 'to': "orm['core.Term']"})
        },
        'core.thesaurus': {
            'Meta': {'object_name': 'Thesaurus'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'uri': ('django.db.models.fields.URLField', [], {'db_index': 'True', 'max_length': '2048', 'null': 'True', 'blank': 'True'})
        },
        u'jocondelab.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['core']
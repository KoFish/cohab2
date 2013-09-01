# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AssignmentView'
        db.create_table(u'hab_assignmentview', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('template', self.gf('django.db.models.fields.related.OneToOneField')(related_name='+', unique=True, to=orm['hab.AssignmentTemplate'])),
        ))
        db.send_create_signal(u'hab', ['AssignmentView'])

        # Adding model 'Verb'
        db.create_table(u'hab_verb', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal(u'hab', ['Verb'])

        # Adding model 'Assignment'
        db.create_table(u'hab_assignment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('verb', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assignments', to=orm['hab.Verb'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assignments_own', null=True, to=orm['auth.User'])),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assignments_assigned', null=True, to=orm['auth.User'])),
            ('importance', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('cleared', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assignments', null=True, on_delete=models.SET_NULL, to=orm['hab.AssignmentTemplate'])),
        ))
        db.send_create_signal(u'hab', ['Assignment'])

        # Adding model 'AssignmentTemplate'
        db.create_table(u'hab_assignmenttemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('verb', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['hab.Verb'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('importance', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('delay', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('single', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('abstract', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'hab', ['AssignmentTemplate'])

        # Adding M2M table for field owners on 'AssignmentTemplate'
        m2m_table_name = db.shorten_name(u'hab_assignmenttemplate_owners')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('assignmenttemplate', models.ForeignKey(orm[u'hab.assignmenttemplate'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['assignmenttemplate_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'AssignmentView'
        db.delete_table(u'hab_assignmentview')

        # Deleting model 'Verb'
        db.delete_table(u'hab_verb')

        # Deleting model 'Assignment'
        db.delete_table(u'hab_assignment')

        # Deleting model 'AssignmentTemplate'
        db.delete_table(u'hab_assignmenttemplate')

        # Removing M2M table for field owners on 'AssignmentTemplate'
        db.delete_table(db.shorten_name(u'hab_assignmenttemplate_owners'))


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
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'hab.assignment': {
            'Meta': {'object_name': 'Assignment'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assignments_assigned'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'cleared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assignments_own'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assignments'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['hab.AssignmentTemplate']"}),
            'verb': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assignments'", 'to': u"orm['hab.Verb']"})
        },
        u'hab.assignmenttemplate': {
            'Meta': {'object_name': 'AssignmentTemplate'},
            'abstract': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deadline': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'delay': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['auth.User']"}),
            'single': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'verb': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['hab.Verb']"})
        },
        u'hab.assignmentview': {
            'Meta': {'object_name': 'AssignmentView'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'template': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'+'", 'unique': 'True', 'to': u"orm['hab.AssignmentTemplate']"})
        },
        u'hab.verb': {
            'Meta': {'object_name': 'Verb'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        }
    }

    complete_apps = ['hab']
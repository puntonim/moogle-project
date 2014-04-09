# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GoogleProfile'
        db.create_table('profiles_googleprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
            ('family_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=50)),
            ('given_name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(blank=True, max_length=101)),
            ('gender', self.gf('django.db.models.fields.CharField')(blank=True, max_length=10)),
            ('email', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75)),
            ('verified_email', self.gf('django.db.models.fields.NullBooleanField')(blank=True, null=True)),
            ('locale', self.gf('django.db.models.fields.CharField')(blank=True, max_length=5)),
            ('google_id', self.gf('django.db.models.fields.CharField')(blank=True, max_length=50)),
            ('link', self.gf('django.db.models.fields.URLField')(blank=True, max_length=200)),
        ))
        db.send_create_signal('profiles', ['GoogleProfile'])


    def backwards(self, orm):
        # Deleting model 'GoogleProfile'
        db.delete_table('profiles_googleprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'related_name': "'user_set'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'related_name': "'user_set'", 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'profiles.googleprofile': {
            'Meta': {'object_name': 'GoogleProfile'},
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'family_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '50'}),
            'gender': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '10'}),
            'given_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '50'}),
            'google_id': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'blank': 'True', 'max_length': '200'}),
            'locale': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '101'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'verified_email': ('django.db.models.fields.NullBooleanField', [], {'blank': 'True', 'null': 'True'})
        }
    }

    complete_apps = ['profiles']
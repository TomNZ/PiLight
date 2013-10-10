# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TransformField.name'
        db.alter_column(u'home_transformfield', 'name', self.gf('django.db.models.fields.CharField')(max_length=15))

    def backwards(self, orm):

        # Changing field 'TransformField.name'
        db.alter_column(u'home_transformfield', 'name', self.gf('django.db.models.fields.CharField')(max_length=10))

    models = {
        u'home.light': {
            'Meta': {'object_name': 'Light'},
            'color': ('pilight.fields.ColorField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Store']", 'null': 'True', 'blank': 'True'})
        },
        u'home.store': {
            'Meta': {'object_name': 'Store'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'home.transform': {
            'Meta': {'object_name': 'Transform'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'})
        },
        u'home.transformfield': {
            'Meta': {'object_name': 'TransformField'},
            'default_value': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'default': "'float'", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'long_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'transform': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Transform']"})
        },
        u'home.transforminstance': {
            'Meta': {'object_name': 'TransformInstance'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'params': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'store': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Store']", 'null': 'True', 'blank': 'True'}),
            'transform': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['home.Transform']"})
        }
    }

    complete_apps = ['home']
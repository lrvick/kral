# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'FacebookStatus.status_id'
        db.alter_column('kral_facebookstatus', 'status_id', self.gf('django.db.models.fields.CharField')(max_length=255))


    def backwards(self, orm):
        
        # Changing field 'FacebookStatus.status_id'
        db.alter_column('kral_facebookstatus', 'status_id', self.gf('django.db.models.fields.IntegerField')())


    models = {
        'kral.facebookstatus': {
            'Meta': {'object_name': 'FacebookStatus'},
            'attribution': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {}),
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kral.FacebookUser']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'status_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'kral.facebookuser': {
            'Meta': {'object_name': 'FacebookUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        },
        'kral.query': {
            'Meta': {'object_name': 'Query'},
            'hits': ('django.db.models.fields.BigIntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'kral.twittertweet': {
            'Meta': {'object_name': 'TwitterTweet'},
            'contributors': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'geo': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'irt_status_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'irt_user_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'irt_user_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '2'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'retweet_count': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sentiment': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '1'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'truncated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tweet_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'user_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['kral.TwitterUser']"})
        },
        'kral.twitteruser': {
            'Meta': {'object_name': 'TwitterUser'},
            'avatar': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'contributors_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'followers': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'following': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'geo_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'listed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'real_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'time_zone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'total_tweets': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'user_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'utc_offset': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'kral.weblink': {
            'Meta': {'object_name': 'WebLink'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hits': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'total_mentions': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4000'})
        }
    }

    complete_apps = ['kral']

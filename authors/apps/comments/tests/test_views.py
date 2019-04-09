from .test_base import BaseTest
from django.urls import reverse
import json

class TestComment(BaseTest):

    def test_comment_creation(self):
        self.create_comment()
        self.assertEqual(self.comment.status_code,201)
    
    def test_all_comments(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(self.comment_url,
                    format='json')
        self.assertEqual(response.status_code,200)

    def test_get_comment_details(self):
        self.create_comment()
        response = self.client.get(
                reverse('comments:specific_comment',kwargs={'slug':self.slug,'comment_pk':self.comment_id}),
                format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_comment(self):
        self.create_comment()
        response = self.client.delete(
                reverse('comments:specific_comment',kwargs={'slug':self.slug,'comment_pk':self.comment_id}),
                format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully deleted comment',str(response.data))

    def test_update_comment(self):
        self.create_comment()
        response = self.client.patch(
                reverse('comments:specific_comment',kwargs={'slug':self.slug,'comment_pk':self.comment_id}),
                data=json.dumps({'comment_body':'it works'}),content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('it works',str(response.data))

    def test_reply_creation(self):
        self.create_reply()
        self.assertEqual(self.reply.status_code,201)

    def test_all_replies(self):
        self.create_comment()
        response = self.client.get(self.reply_url,
                    format='json')
        self.assertEqual(response.status_code,200)

    def test_get_one_reply(self):
        self.create_reply()
        response = self.client.get(
                reverse('comments:specific_reply',kwargs={'slug':self.slug,'comment_pk':self.comment_id,'pk':self.reply_id}),
                format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_reply(self):
        self.create_reply()
        response = self.client.delete(
                reverse('comments:specific_reply',kwargs={'slug':self.slug,'comment_pk':self.comment_id,'pk':self.reply_id}),
                format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Successfully deleted reply',str(response.data))

    def test_update_reply(self):
        self.create_reply()
        response = self.client.patch(
                reverse('comments:specific_reply',kwargs={'slug':self.slug,'comment_pk':self.comment_id,'pk':self.reply_id}),
                data=json.dumps({'body':'it works'}),content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('it works',str(response.data))
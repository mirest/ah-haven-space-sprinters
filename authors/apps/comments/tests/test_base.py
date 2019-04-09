from rest_framework.test import APITestCase,APIClient
from django.urls import reverse
from ...authentication.models import User
from ...articles.models import Article
from ...profiles.models import Profile
from django.core import mail
import json

class BaseTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='sebbss', 
            email='sebbss@sprinters.ug', 
            password='Butt3rfly1'
        )
        Article.objects.create(
            title = 'white shark',
            description = 'yes man',
            body = 'mybody',
            author = Profile.objects.get(user = self.user.id))
        self.article = Article.objects.all().first()
        self.slug = self.article.slug
        self.comment_url =reverse('comments:comments',kwargs={'slug':self.slug})
        self.user_data = {

                "username": "sampleuser",
                "email": "user@sprinters.ug",
                "password": "Butt3rfly1"
        }
        self.client.post(reverse('auth:register'),
                                content_type='application/json', data=json.dumps(self.user_data))
        verification_link = (mail.outbox[0].body.split('\n')).pop(1)
        url = verification_link.split("testserver").pop(1)
        self.client.get(url, content_type='application/json')
        login_resp = self.client.post(reverse('auth:login'), content_type='application/json',
                                data=json.dumps(self.user_data))

        self.test_token = login_resp.data.get("auth_token")
        self.auth_header = 'Bearer {}'.format(self.test_token)

    def create_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.comment = self.client.post(self.comment_url,
                    data=json.dumps({'comment_body':'kawa'}),
                    content_type='application/json')
        self.comment_id = self.comment.data['id']
        self.reply_url = reverse('comments:replies',
                                kwargs={'slug':self.slug,'comment_pk':self.comment_id,})

    def create_reply(self):
        self.create_comment()
        self.reply = self.client.post(self.reply_url,
                    data=json.dumps({'body':'yes sir'}),
                    content_type='application/json')
        self.reply_id = self.reply.data['id']
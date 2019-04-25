import json

from django.urls import reverse
from django.core import mail

from rest_framework import status

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article, ArticleLikes

from .test_base import BaseTestClass
from authors.apps.authentication.tests.test_base import BaseTestClass as BTC


class TestUserRoutes(BaseTestClass):

    def test_create_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_all_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(
            reverse('article:create_article'),
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_one_articles(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.get(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_slug_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.get(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-t-trai-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found.', str(response.data))

    def test_delete_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.delete(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Article has been deleted', str(response.data))

    def test_update_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.put(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            data=self.update_data,
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_article_no_slug(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.delete(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon77"}),
            format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found.', str(response.data))

    def test_update_article_no_slug(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.put(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon88"}),
            data=self.update_data,
            format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Not found.', str(response.data))

    def test_show_read_time(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.get(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['read_time']), "less than 1 min")

    def test_show_read_time_more_than_a_minute(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article,
            format='json')
        response = self.client.get(
            reverse(
                'article:get_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data['read_time']), "4 mins")

    def test_share_facebook_link(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.post(
            reverse(
                'article:share_facebook',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_share_twitter_link(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.post(
            reverse(
                'article:share_twitter',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_share_article_via_mail(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        response = self.client.post(
            reverse(
                'article:share_email',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            data=self.email_share,
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your article has been shared successfully',
                      str(response.data))
        self.assertIn(
            'Your article has been shared successfully', str(
                response.data))

    def test_get_all_tags(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data2,
            format='json')
        resp = self.client.get(
            reverse('articles:get_tags'), format='json')
        self.assertEqual(resp.status_code, 200)

    def test_no_tags_available(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            reverse('article:create_article'),
            data=self.article_data,
            format='json')
        resp = self.client.get(
            reverse('articles:get_tags'), format='json')
        self.assertIn('there are no tags available', str(resp.data))

    def test_post_rating_article_unauthorized(self):
        response = self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.6}))
        error = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response.data)

    def test_post_rating_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        response = self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.6}))
        self.assertEqual(response.status_code, 201)
        self.assertEqual('4.6', response.data['rating'])

    def test_post_rating_article_same_authour(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        response = self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.6}))
        message = {
            'error': ['Rate an article that does not belong to you, Please']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(message, response.data['errors'])

    def test_post_rating_article_exists(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.6}))
        response = self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.7}))
        message = {"error": ['Article rating already exists, Please']
                   }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors'], message)

    def test_get_rated_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.7}))
        response = self.client.get(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('4.7', response.data['rating'])

    def test_get_rated_article_unauthorized(self):
        response = self.client.get(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            format='json')
        error = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response.data)

    def test_updated_rated_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.7}))
        response = self.client.patch(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.8}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual('4.8', response.data['rating'])

    def test_updated_rated_article_unauthorized(self):
        response = self.client.patch(
            reverse(
                'article:rate_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json', data=json.dumps({'rating': 4.6}))
        error = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response.data)

    def test_post_bookmark_article_unauthorized(self):
        response = self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        error = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response.data)

    def test_post_bookmark_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        response = self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(True, response.data['bookmark'])

    def test_post_bookmark_article_error(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        response = self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train4-your-dragon"}),
            content_type='application/json')
        message = {'detail': 'Not found.'}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(message, response.data)

    def test_post_bookmark_article_exists(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        response = self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        message = {"error": ['Article bookmark already exists, Please']}
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['errors'], message)

    def test_get_bookmarked_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        response = self.client.get(
            reverse(
                'article:bookmarked'),
            format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_bookmarked_article_unauthorized(self):
        response = self.client.get(
            reverse(
                'article:bookmarked'),
            format='json')
        error = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response.data)

    def test_un_bookmark_article(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        response = self.client.delete(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(False, response.data['bookmarked'])

    def test_un_bookmark_article_error(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        response = self.client.delete(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        error = {
            "error": [
                "Article bookmark doesnot exists."]
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(error, response.data['errors'])

    def test_un_bookmark_article_not_found(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(reverse('article:create_article'),
                         data=self.article_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=self.auth_header3)
        self.client.post(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        response = self.client.delete(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train7-your-dragon"}),
            content_type='application/json')
        message = {'detail': 'Not found.'}
        self.assertEqual(response.status_code, 404)
        self.assertEqual(message, response.data)

    def test_un_bookmark_article_unauthorized(self):
        response = self.client.delete(
            reverse(
                'article:bookmark_article',
                kwargs={
                    'slug': "how-to-train-your-dragon"}),
            content_type='application/json')
        error = {"detail": "Authentication credentials were not provided."}
        self.assertEqual(response.status_code, 403)
        self.assertEqual(error, response.data)


class TestArticleLikes(BaseTestClass):

    def test_like_article(self):
        response = self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header2)
        like_response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2,
            data=self.like_request,
            format='json'
        )
        self.assertEqual(like_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            like_response.data['message'], 'You have liked an article')

    def test_like_article_doesnot_exist(self):

        like_response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2,
            data=self.like_request,
            format='json'
        )
        self.assertEqual(like_response.status_code, 404)

    def test_like_article_with_non_boolean_value(self):
        response = self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header2)
        like_response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2,
            data={"like_article": "true"},
            format='json'
        )
        expected_response = {
            "errors": [
                "Value of like_article should be a boolean"
            ]
        }
        self.assertEqual(like_response.status_code, 400)
        self.assertEqual(like_response.data, expected_response)

    def test_like_article_with_invalid_request_body(self):
        response = self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header2)
        like_response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2
        )
        expected_response = {
            "errors": [
                "like_article field is required"
            ]
        }
        self.assertEqual(like_response.status_code, 400)
        self.assertEqual(like_response.data, expected_response)

    def test_like_article_already_liked(self):
        response = self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header2)
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2,
            data=self.like_request,
            format='json'
        )
        like_response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2,
            data=self.like_request,
            format='json'
        )
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            like_response.data['message'],
            'You have already liked the article')

    def test_dislike_article(self):
        response = self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header2)
        like_response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            HTTP_AUTHORIZATION=self.auth_header2,
            data=self.dislike_request,
            format='json'
        )
        self.assertEqual(like_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            like_response.data['message'], 'You have disliked an article')

    def test_list_of_users_liked_succeeds(self):
        """Tests an endpoint that lists users that liked/disliked"""

        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.like_request),
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.get(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(["sampleuser"],
                             response.data.get("likes"))

    def test_get_like_article(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.url, data=self.article, format='json')
        slug = response.data.get('slug')
        like_url = reverse("article:article_likes", args=[slug])
        self.client.put(like_url, format='json')
        get_like_url = reverse("article:article_likes", args=[slug])
        get_like_response = self.client.get(get_like_url, format='json')
        self.assertEqual(get_like_response.status_code, status.HTTP_200_OK)

    def test_unlike_an_article_succeeds(self):
        """Unlike an already liked article by the same user"""
        self.client.credentials(
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.url, data=self.article, format='json')
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.like_request),
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.delete(
            self.like_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("You have unliked an article", response.data["message"])

    def test_dislike_an_article_succeeds(self):
        """Tests an endpoint that dislikes an article"""
        self.client.credentials(
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.url, data=self.article, format='json')
        response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.dislike_request),
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("You have disliked an article", response.data["message"])

    def test_dislike_after_dislike_succeeds(self):
        """Dislike an already disliked article by the same user"""
        self.client.credentials(
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.url, data=self.article, format='json')
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.dislike_request),
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.put(
            self.like_url,
            content_type='application/json',
            data=json.dumps(self.dislike_request),
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("You have already disliked the article",
                      response.data["message"])

    def test_undislike_an_article_succeeds(self):
        """Remove a dislike from a disliked article by the same user"""
        self.client.credentials(
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.url, data=self.article, format='json')
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.dislike_request),
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.delete(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("You have un-disliked an article",
                      response.data["message"])

    def test_like_after_dislike_an_article_succeeds(self):
        """like a formerly a disliked article by the same user"""
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.dislike_request),
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.like_request),
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("You have liked an article", response.data["message"])

    def test_dislike_after_like_an_article_succeeds(self):
        """Dislike a formerly a liked article by the same user"""
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.like_request),
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.put(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            data=json.dumps(self.dislike_request),
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("You have disliked an article", response.data["message"])

    def test_remove_like_dislike_nonexixtent(self):
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.delete(
            '/api/articles/how-to-train-your-dragon/likes/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth_header)
        expected_response = {
            "errors": [
                "There is no like or dislike to remove"
            ]
        }
        self.assertEqual(response.data, expected_response)

    def test_report_creation(self):
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.report_url, data={'reason': 'anything'}, format='json',
            HTTP_AUTHORIZATION=self.auth_header3)
        self.assertIn(
            f"You have successfully reported article {self.slug}", str(response.data))

    def test_report_on_article_again(self):
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            self.report_url, data={'reason': 'anything'}, format='json',
            HTTP_AUTHORIZATION=self.auth_header3)
        response = self.client.post(
            self.report_url, data={'reason': 'anything'}, format='json',
            HTTP_AUTHORIZATION=self.auth_header3)
        self.assertIn('you already reported this article', str(response.data))

    def test_report_your_own_article(self):
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        response = self.client.post(
            self.report_url, data={'reason': 'anything'}, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn("you cannot report your own article", str(response.data))

    def test_get_reports_admin(self):
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.client.post(
            self.report_url, data={'reason': 'anything'}, format='json',
            HTTP_AUTHORIZATION=self.auth_header3)
        user = User.objects.create_superuser(
            username='samleuser',
            email='use@sprinters.ug',
            password='Butt3rfly1')
        self.client.force_authenticate(user=user)
        resp = self.client.get(reverse('article:get_reports'))
        self.assertEqual(resp.status_code, 200)

    def test_get_reports_non_admin(self):
        self.client.post(
            self.url, data=self.article, format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        resp = self.client.get(
            reverse('article:get_reports'), format='json',
            HTTP_AUTHORIZATION=self.auth_header)
        self.assertIn('permission denied login as admin', str(resp.data))

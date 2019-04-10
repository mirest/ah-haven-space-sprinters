from authors.apps.articles.tests.test_base import BaseTestClass
from authors.apps.articles.models import Article


class ArticleModelTest(BaseTestClass):
    def test_article_representation(self):
        """
         Tests the return datatype of the article elements
         """
        self.assertIsInstance(self.article_data, dict)

    def test_article_model(self):
        """
        This function validates the internal state of the model to ensure
        it returns the correct values
        """
        self.assertEqual(
            self.article_data['title'], "how to train your dragon")
        self.assertEqual(
            self.article_data['description'], "ever wonder how to do that?")
        self.assertEqual(self.article_data['body'], "you have to beleive")

    def test_str_returns_correct_string_representation(self):
        """
        Tests that __str__ generates a correct string representation of
        article title
        """
        article = Article(title="Hello today",
                          description="Today is beautiful",
                          body="This is the body")
        self.assertEqual(
            str(self.article_data['title']), "how to train your dragon")

from django.test import Client, TestCase
from django.urls import reverse


class PageSmokeTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST="localhost")

    def test_contact_page_renders(self):
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)

    def test_contact_post_redirects(self):
        response = self.client.post(reverse("contact"), {"message": "hello"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("contact"))

    def test_mobilenet_metrics_page_renders(self):
        response = self.client.get(reverse("mobilenet_metrics"))
        self.assertEqual(response.status_code, 200)

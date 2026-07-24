from django.test import TestCase, Client
from django.urls import reverse
from products.models import Category, Product


class AgeGateAndCategoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_soft = Category.objects.create(name='Soft Drinks', slug='soft-drinks')
        self.cat_cold = Category.objects.create(name='Cold Drinks', slug='cold-drinks')
        self.cat_tea = Category.objects.create(name='Tea', slug='tea')
        self.cat_coffee = Category.objects.create(name='Coffee', slug='coffee')
        self.cat_wine = Category.objects.create(name='Wines', slug='wines')

        self.prod_soft = Product.objects.create(
            category=self.cat_soft, name='Cola', slug='cola', brand='BrandX', price=50, description='Soda'
        )
        self.prod_tea = Product.objects.create(
            category=self.cat_tea, name='Green Tea', slug='green-tea', brand='BrandY', price=80, description='Tea'
        )
        self.prod_wine = Product.objects.create(
            category=self.cat_wine, name='Cabernet', slug='cabernet', brand='BrandZ', price=500, description='Wine', alcohol_percentage=13.5
        )

    def test_soft_cold_category_unrestricted(self):
        url = reverse('products:list_by_category', kwargs={'category_slug': 'soft-cold-drinks'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cola')

    def test_tea_coffee_category_unrestricted(self):
        url = reverse('products:list_by_category', kwargs={'category_slug': 'tea-coffee'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Green Tea')

    def test_wines_direct_access_redirects_unverified_user(self):
        url = reverse('products:list_by_category', kwargs={'category_slug': 'wines'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('age_gate=wines', response.url)

    def test_age_verification_endpoint_over18(self):
        verify_url = reverse('products:verify_age')
        post_data = {'choice': 'over18'}
        response = self.client.post(verify_url, data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('verified'))
        self.assertTrue(self.client.session.get('age_verified'))

        # Now wines page should be accessible
        wine_url = reverse('products:list_by_category', kwargs={'category_slug': 'wines'})
        wine_response = self.client.get(wine_url)
        self.assertEqual(wine_response.status_code, 200)
        self.assertContains(wine_response, 'Cabernet')

    def test_age_verification_endpoint_under18(self):
        verify_url = reverse('products:verify_age')
        post_data = {'choice': 'under18'}
        response = self.client.post(verify_url, data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json().get('verified'))
        self.assertFalse(self.client.session.get('age_verified'))

        # Wines page should still be blocked
        wine_url = reverse('products:list_by_category', kwargs={'category_slug': 'wines'})
        wine_response = self.client.get(wine_url)
        self.assertEqual(wine_response.status_code, 302)

from django.test import TestCase, Client
from django.urls import reverse
from products.models import Category, Product


class CategoryBrowsingTests(TestCase):
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

    def test_wines_category_direct_access(self):
        url = reverse('products:list_by_category', kwargs={'category_slug': 'wines'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cabernet')

    def test_wine_detail_direct_access(self):
        url = reverse('products:detail', kwargs={'slug': 'cabernet'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cabernet')

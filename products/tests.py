"""
Tests for products app.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from .models import Product, Category, ProductTag

User = get_user_model()


class CategoryModelTests(TestCase):
    """Tests for the Category model."""
    
    def test_create_category(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.slug, 'electronics')
    
    def test_category_str(self):
        """Test category string representation."""
        category = Category.objects.create(name='Test Category')
        self.assertEqual(str(category), 'Test Category')


class ProductModelTests(TestCase):
    """Tests for the Product model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='seller@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
    
    def test_create_product(self):
        """Test creating a product."""
        product = Product.objects.create(
            seller=self.user,
            name='Wireless Headphones',
            description='Premium wireless headphones',
            price=89.99,
            stock_quantity=100,
            category=self.category
        )
        
        self.assertEqual(product.name, 'Wireless Headphones')
        self.assertEqual(product.price, 89.99)
        self.assertEqual(product.seller, self.user)
        self.assertEqual(product.status, 'draft')
    
    def test_product_str(self):
        """Test product string representation."""
        product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            price=10.00
        )
        self.assertEqual(str(product), 'Test Product')
    
    def test_product_slug_generated(self):
        """Test that slug is auto-generated."""
        product = Product.objects.create(
            seller=self.user,
            name='My Test Product',
            price=10.00
        )
        self.assertEqual(product.slug, 'my-test-product')
    
    def test_product_default_status(self):
        """Test product default status is draft."""
        product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            price=10.00
        )
        self.assertEqual(product.status, 'draft')
    
    def test_product_in_stock(self):
        """Test product in stock property."""
        product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            price=10.00,
            stock_quantity=10
        )
        self.assertTrue(product.in_stock)
        
        product.stock_quantity = 0
        product.save()
        self.assertFalse(product.in_stock)


class ProductAPITests(APITestCase):
    """Tests for the Product API."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='seller@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
    
    def test_list_products(self):
        """Test listing products."""
        Product.objects.create(
            seller=self.user,
            name='Product 1',
            price=10.00
        )
        Product.objects.create(
            seller=self.user,
            name='Product 2',
            price=20.00
        )
        
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_product(self):
        """Test creating a product."""
        data = {
            'name': 'New Product',
            'description': 'Product description',
            'price': '99.99',
            'stock_quantity': 50,
            'category': self.category.id
        }
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Product')
        self.assertEqual(float(response.data['price']), 99.99)
    
    def test_create_product_unauthenticated(self):
        """Test that unauthenticated requests are rejected."""
        data = {
            'name': 'New Product',
            'price': '99.99'
        }
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_product_detail(self):
        """Test getting product details."""
        product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            price=10.00
        )
        
        response = self.client.get(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
    
    def test_update_product(self):
        """Test updating a product."""
        product = Product.objects.create(
            seller=self.user,
            name='Original Name',
            price=10.00
        )
        
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Updated Name'}
        response = self.client.patch(f'/api/products/{product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        product.refresh_from_db()
        self.assertEqual(product.name, 'Updated Name')
    
    def test_delete_product(self):
        """Test deleting a product."""
        product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            price=10.00
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/products/{product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())
    
    def test_filter_products_by_status(self):
        """Test filtering products by status."""
        Product.objects.create(
            seller=self.user,
            name='Draft Product',
            price=10.00,
            status='draft'
        )
        Product.objects.create(
            seller=self.user,
            name='Active Product',
            price=20.00,
            status='active'
        )
        
        response = self.client.get('/api/products/?status=active')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Active Product')


class ProductAITests(APITestCase):
    """Tests for AI-powered product features."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='seller@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            seller=self.user,
            name='Test Product',
            price=10.00,
            description='A test product description'
        )
    
    def test_generate_description(self):
        """Test generating product description with AI."""
        self.client.force_authenticate(user=self.user)
        
        data = {'product_id': self.product.id}
        response = self.client.post('/api/ai/generate/description/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('description', response.data)
    
    def test_generate_hashtags(self):
        """Test generating hashtags with AI."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'product_id': self.product.id,
            'platform': 'instagram'
        }
        response = self.client.post('/api/ai/generate/hashtags/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hashtags', response.data)
    
    def test_generate_social_post(self):
        """Test generating social media post with AI."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'product_id': self.product.id,
            'platform': 'instagram'
        }
        response = self.client.post('/api/ai/generate/social-post/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('post', response.data)


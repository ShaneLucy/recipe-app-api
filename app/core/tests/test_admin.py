from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    # creating a test client, user and logging user into client
    # creating an unauthorised user also 
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='test@gmail.com',
            password='password123'
        )
        #logs a user in
        self.client.force_login(self.admin_user)
        #user to be displayed on admin page
        self.user = get_user_model().objects.create_user(
            email = 'anothertest@gmail.com',
            password = 'password123',
            name = 'Not Authenticated'
        )
    
    def test_users_listed(self):
        """Test users are listed on admin page"""
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)
    
    def test_user_change_page(self):
        """Test that user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        # url example /admin/core/user/12
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
    
    def test_create_user_page(self):
        """Test that the create user page works"""
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, 200)





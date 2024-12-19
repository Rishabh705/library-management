import unittest
import json
from app import app, db
from app.models import User, Book, Member

class LibraryManagementSystemTests(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(username='testuser', password='password')
        db.session.add(self.user)
        db.session.commit()

        self.book = Book(title="Test Book", author="Test Author", year=2021)
        self.member = Member(name="Test Member", email="testmember@example.com")
        db.session.add(self.book)
        db.session.add(self.member)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user(self):
        response = self.app.post('/register', data=json.dumps({
            'username': 'newuser',
            'password': 'password123'
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'User registered successfully')

    def test_login_user(self):
        response = self.app.post('/login', data=json.dumps({
            'username': 'testuser',
            'password': 'password'
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('token' in data)

    def test_add_book(self):
        response = self.app.post('/books', data=json.dumps({
            'title': 'New Book',
            'author': 'New Author',
            'year': 2022
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Book added successfully')

    def test_get_books(self):
        response = self.app.get('/books')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Test Book')

    def test_update_book(self):
        response = self.app.put(f'/books/{self.book.id}', data=json.dumps({
            'title': 'Updated Test Book',
            'author': 'Updated Author',
            'year': 2023
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Book updated successfully')

    def test_delete_book(self):
        response = self.app.delete(f'/books/{self.book.id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Book deleted successfully')

    def test_add_member(self):
        response = self.app.post('/members', data=json.dumps({
            'name': 'New Member',
            'email': 'newmember@example.com'
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Member added successfully')

    def test_get_members(self):
        response = self.app.get('/members')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Member')

    def test_update_member(self):
        response = self.app.put(f'/members/{self.member.id}', data=json.dumps({
            'name': 'Updated Member',
            'email': 'updatedmember@example.com'
        }), content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Member updated successfully')

    def test_delete_member(self):
        response = self.app.delete(f'/members/{self.member.id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Member deleted successfully')

if __name__ == '__main__':
    unittest.main()

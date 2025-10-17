"""
Pytest configuration and shared fixtures.
"""
import pytest
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def app_config():
    """Application configuration for testing."""
    return {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test-key'
    }


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv('FLASK_ENV', 'testing')
    monkeypatch.setenv('SUPABASE_URL', 'https://test.supabase.co')
    monkeypatch.setenv('SUPABASE_KEY', 'test-key')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')


@pytest.fixture
def mock_supabase(monkeypatch):
    """Mock Supabase client for testing."""
    class MockSupabase:
        def __init__(self):
            self.table_data = {}
        
        def table(self, table_name):
            return MockTable(table_name, self.table_data)
    
    class MockTable:
        def __init__(self, name, data):
            self.name = name
            self.data = data
        
        def select(self, *args):
            return MockQuery(self.name, self.data)
        
        def insert(self, data):
            return MockQuery(self.name, self.data, insert_data=data)
        
        def update(self, data):
            return MockQuery(self.name, self.data, update_data=data)
        
        def delete(self):
            return MockQuery(self.name, self.data, delete=True)
    
    class MockQuery:
        def __init__(self, table_name, data, insert_data=None, update_data=None, delete=False):
            self.table_name = table_name
            self.data = data
            self.insert_data = insert_data
            self.update_data = update_data
            self.delete = delete
        
        def execute(self):
            return MockResponse([])
        
        def eq(self, column, value):
            return self
        
        def order(self, column):
            return self
        
        def limit(self, count):
            return self
    
    class MockResponse:
        def __init__(self, data):
            self.data = data
    
    mock_client = MockSupabase()
    monkeypatch.setattr('app.supabase', mock_client)
    return mock_client
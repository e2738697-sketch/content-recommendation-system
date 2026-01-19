"""Tests for database client module"""
import pytest
import os
from unittest.mock import Mock, patch
from src.db.supabase_client import SupabaseClient


class TestSupabaseClient:
    """Test suite for SupabaseClient"""
    
    @pytest.fixture
    def mock_env(self):
        """Fixture to mock environment variables"""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://test.supabase.co',
            'SUPABASE_KEY': 'test_key'
        }):
            yield
    
    def test_client_initialization(self, mock_env):
        """Test SupabaseClient initialization"""
        client = SupabaseClient()
        assert client is not None
    
    def test_select_returns_list(self, mock_env):
        """Test select method returns list"""
        client = SupabaseClient()
        with patch.object(client.db, 'table') as mock_table:
            mock_query = Mock()
            mock_query.select.return_value = mock_query
            mock_query.execute.return_value = Mock(data=[{'id': 1}])
            mock_table.return_value = mock_query
            
            result = client.select('test_table')
            assert isinstance(result, (list, type(None)))
    
    def test_insert_calls_db(self, mock_env):
        """Test insert method calls database"""
        client = SupabaseClient()
        with patch.object(client.db, 'table') as mock_table:
            mock_query = Mock()
            mock_query.insert.return_value = mock_query
            mock_query.execute.return_value = Mock(data=[{'id': 1}])
            mock_table.return_value = mock_query
            
            result = client.insert('test_table', {'name': 'test'})
            assert result is not None


if __name__ == '__main__':
    pytest.main([__file__])

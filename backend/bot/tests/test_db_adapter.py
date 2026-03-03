"""
Unit Tests for Database Adapter
Tests session save/load and database operations
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest.mock import Mock, MagicMock, patch
import psycopg2
from db_adapter import DatabaseAdapter


@pytest.fixture
def mock_connection():
    """Mock database connection"""
    conn = MagicMock()
    conn.autocommit = True
    
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.rowcount = 0
    cursor.__enter__ = Mock(return_value=cursor)
    cursor.__exit__ = Mock(return_value=False)
    
    conn.cursor.return_value = cursor
    
    return conn, cursor


class TestDatabaseAdapterInit:
    """Test DatabaseAdapter initialization"""
    
    @patch('psycopg2.connect')
    def test_init_with_url(self, mock_connect):
        """Test initialization with database URL"""
        mock_connect.return_value = MagicMock()
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        
        assert db.database_url == "postgresql://test:test@localhost/testdb"
        assert mock_connect.called
    
    @patch.dict('os.environ', {'DATABASE_URL': 'postgresql://env:env@localhost/envdb'})
    @patch('psycopg2.connect')
    def test_init_from_env(self, mock_connect):
        """Test initialization from environment variable"""
        mock_connect.return_value = MagicMock()
        
        db = DatabaseAdapter()
        
        assert db.database_url == "postgresql://env:env@localhost/envdb"
    
    def test_init_without_url_raises_error(self):
        """Test initialization without URL raises error"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="DATABASE_URL not set"):
                DatabaseAdapter()


class TestSessionManagement:
    """Test session save/load operations"""
    
    @patch('psycopg2.connect')
    def test_get_session_exists(self, mock_connect, mock_connection):
        """Test retrieving existing session"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        # Mock session data
        from datetime import datetime
        cursor.fetchone.return_value = {
            'session_data': {
                'user_id': 123456789,
                'current_question': 5,
                'answers': {'gender_identity': 'Female'}
            },
            'last_active': datetime(2025, 2, 21, 12, 0, 0)
        }
        cursor.rowcount = 1
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        session = db.get_session(123456789)
        
        assert session is not None
        assert session['user_id'] == 123456789
        assert session['current_question'] == 5
        assert 'gender_identity' in session['answers']
    
    @patch('psycopg2.connect')
    def test_get_session_not_exists(self, mock_connect, mock_connection):
        """Test retrieving non-existent session"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        cursor.fetchone.return_value = None
        cursor.rowcount = 0
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        session = db.get_session(123456789)
        
        assert session is None
    
    @patch('psycopg2.connect')
    def test_save_session(self, mock_connect, mock_connection):
        """Test saving session"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        
        session = {
            'user_id': 123456789,
            'current_question': 5,
            'answers': {'gender_identity': 'Female'},
            'skip_questions': []
        }
        
        db.save_session(session)
        
        # Should execute INSERT query
        assert cursor.execute.called
        
        # Check that execute was called with INSERT query
        call_args = cursor.execute.call_args[0]
        assert 'INSERT' in call_args[0]
        assert 'conversation_state' in call_args[0]
    
    @patch('psycopg2.connect')
    def test_clear_session(self, mock_connect, mock_connection):
        """Test clearing session"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        db.clear_session(123456789)
        
        # Should execute DELETE query
        assert cursor.execute.called
        call_args = cursor.execute.call_args[0]
        assert 'DELETE' in call_args[0]


class TestUserOperations:
    """Test user CRUD operations"""
    
    @patch('psycopg2.connect')
    def test_get_user_exists(self, mock_connect, mock_connection):
        """Test getting existing user"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        cursor.fetchone.return_value = {
            'telegram_id': 123456789,
            'username': 'test_user',
            'first_name': 'Test',
            'gender_identity': 'Female'
        }
        cursor.rowcount = 1
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        user = db.get_user(123456789)
        
        assert user is not None
        assert user['telegram_id'] == 123456789
        assert user['username'] == 'test_user'
    
    @patch('psycopg2.connect')
    def test_get_user_not_exists(self, mock_connect, mock_connection):
        """Test getting non-existent user"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        cursor.fetchone.return_value = None
        cursor.rowcount = 0
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        user = db.get_user(123456789)
        
        assert user is None
    
    @patch('psycopg2.connect')
    def test_create_user(self, mock_connect, mock_connection):
        """Test creating new user"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        db.create_user(123456789, "test_user", "Test")
        
        # Should execute INSERT query
        assert cursor.execute.called
        call_args = cursor.execute.call_args[0]
        assert 'INSERT' in call_args[0]
        assert 'users' in call_args[0]


@pytest.mark.asyncio
class TestSaveAnswer:
    """Test saving answers to database"""
    
    @patch('psycopg2.connect')
    async def test_save_to_users_table(self, mock_connect, mock_connection):
        """Test saving answer to users table"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        await db.save_answer(123456789, 'users', 'gender_identity', 'Female')
        
        # Should execute UPDATE query
        assert cursor.execute.called
        call_args = cursor.execute.call_args[0]
        assert 'UPDATE' in call_args[0]
        assert 'users' in call_args[0]
    
    @patch('psycopg2.connect')
    async def test_save_to_preferences_table(self, mock_connect, mock_connection):
        """Test saving answer to preferences table"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        await db.save_answer(123456789, 'preferences', 'smoking', 'Never')
        
        # Should execute INSERT and UPDATE queries
        assert cursor.execute.called
    
    @patch('psycopg2.connect')
    async def test_save_to_personality_table(self, mock_connect, mock_connection):
        """Test saving answer to personality/signals table"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        await db.save_answer(123456789, 'personality', 'myers_briggs', 'INTJ')
        
        # Should execute queries
        assert cursor.execute.called


class TestPhotoOperations:
    """Test photo storage operations"""
    
    @patch('psycopg2.connect')
    def test_save_photo_url(self, mock_connect, mock_connection):
        """Test saving photo URL"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        db.save_photo_url(123456789, "https://example.com/photo.jpg", "profile")
        
        # Should execute INSERT query
        assert cursor.execute.called
        call_args = cursor.execute.call_args[0]
        assert 'INSERT' in call_args[0]
        assert 'user_photos' in call_args[0]
    
    @patch('psycopg2.connect')
    def test_get_photos(self, mock_connect, mock_connection):
        """Test retrieving photos"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        from datetime import datetime
        photo_data = [
            {
                'photo_url': 'https://example.com/photo1.jpg',
                'photo_type': 'profile',
                'uploaded_at': datetime.now()
            }
        ]
        
        # Mock both fetchall and the execute to return photos
        cursor.fetchall.return_value = photo_data
        cursor.rowcount = 1
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        
        # Override the cursor to return photo data
        with patch.object(db, '_execute', return_value=photo_data):
            photos = db.get_photos(123456789)
        
        assert len(photos) == 1
        assert photos[0]['photo_type'] == 'profile'


class TestProfileCompletion:
    """Test profile completion calculation"""
    
    @patch('psycopg2.connect')
    def test_profile_completion_empty(self, mock_connect, mock_connection):
        """Test completion for empty profile"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        cursor.fetchone.return_value = None
        cursor.rowcount = 0
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        completion = db.get_profile_completion(123456789)
        
        assert completion['completion'] == 0
        assert len(completion['missing']) == 0
    
    @patch('psycopg2.connect')
    def test_profile_completion_partial(self, mock_connect, mock_connection):
        """Test completion for partially filled profile"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        # User with some fields filled
        cursor.fetchone.return_value = {
            'telegram_id': 123456789,
            'gender_identity': 'Female',
            'looking_for_gender': 'Male',
            'date_of_birth': '1995-06-15',
            # Missing other required fields
            'city_current': None,
            'religion': None
        }
        cursor.rowcount = 1
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        completion = db.get_profile_completion(123456789)
        
        # Should be between 0 and 100
        assert 0 <= completion['completion'] <= 100
        
        # Should have missing fields
        assert len(completion['missing']) > 0
    
    @patch('psycopg2.connect')
    def test_profile_completion_full(self, mock_connect, mock_connection):
        """Test completion for fully filled profile"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        # User with all tier 1 fields filled
        cursor.fetchone.return_value = {
            'telegram_id': 123456789,
            'gender_identity': 'Female',
            'looking_for_gender': 'Male',
            'date_of_birth': '1995-06-15',
            'city_current': 'Mumbai',
            'religion': 'Hindu',
            'children_intent': 'Maybe',
            'marital_status': 'Never married',
            'smoking': 'Never',
            'drinking': 'Socially',
            'relationship_intent': 'Marriage'
        }
        cursor.rowcount = 1
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        completion = db.get_profile_completion(123456789)
        
        # Should be 100% or close
        assert completion['completion'] >= 90
        
        # Should have no or few missing fields
        assert len(completion['missing']) <= 1


class TestErrorHandling:
    """Test error handling and reconnection"""
    
    @patch('psycopg2.connect')
    def test_execute_with_error_and_reconnect(self, mock_connect, mock_connection):
        """Test error handling with reconnection"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        # Simulate error on first call, success on retry
        cursor.execute.side_effect = [
            psycopg2.OperationalError("Connection lost"),
            None  # Success on reconnect
        ]
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        
        # Should raise error (but try to reconnect)
        with pytest.raises(psycopg2.OperationalError):
            db._execute("SELECT 1")
    
    @patch('psycopg2.connect')
    def test_close_connection(self, mock_connect, mock_connection):
        """Test closing connection"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        db.close()
        
        # Should close connection
        assert conn.close.called


class TestJSONBOperations:
    """Test JSONB operations for preferences and signals"""
    
    @patch('psycopg2.connect')
    async def test_save_to_jsonb_creates_row(self, mock_connect, mock_connection):
        """Test saving to JSONB creates row if needed"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        await db._save_to_jsonb_table('user_preferences', 123456789, 'smoking', 'Never')
        
        # Should execute INSERT query (to create row) and UPDATE query
        assert cursor.execute.call_count >= 1
    
    @patch('psycopg2.connect')
    async def test_save_to_jsonb_updates_field(self, mock_connect, mock_connection):
        """Test saving to JSONB updates field"""
        conn, cursor = mock_connection
        mock_connect.return_value = conn

        # Mock the user lookup to return a user_id
        cursor.fetchone.return_value = {'id': 42}

        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        await db._save_to_jsonb_table('user_signals', 123456789, 'communication_style', 'Direct')

        # Should execute queries (SELECT + INSERT + UPDATE)
        assert cursor.execute.called

        # Check that UPDATE query contains jsonb operation
        calls = cursor.execute.call_args_list
        update_call = [c for c in calls if 'UPDATE' in str(c)]
        assert len(update_call) > 0


class TestConnectionManagement:
    """Test connection lifecycle"""
    
    @patch('psycopg2.connect')
    def test_connection_established_on_init(self, mock_connect):
        """Test connection is established on initialization"""
        mock_connect.return_value = MagicMock()
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        
        assert mock_connect.called
        assert db.conn is not None
    
    @patch('psycopg2.connect')
    def test_autocommit_enabled(self, mock_connect):
        """Test autocommit is enabled"""
        conn = MagicMock()
        mock_connect.return_value = conn
        
        db = DatabaseAdapter("postgresql://test:test@localhost/testdb")
        
        # Should set autocommit
        assert conn.autocommit is True

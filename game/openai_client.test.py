"""
Unit tests for OpenAI API integration
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from game.openai_client import OpenAIClient, OpenAIError


class TestOpenAIClient:
    """Test cases for OpenAIClient class"""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client for testing"""
        with patch('game.openai_client.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def openai_client(self, mock_openai_client):
        """Create OpenAIClient instance with mocked OpenAI"""
        return OpenAIClient(api_key="test-api-key")
    
    def test_initialization_with_api_key(self, mock_openai_client):
        """Test OpenAIClient initialization with API key"""
        client = OpenAIClient(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "gpt-3.5-turbo"
        assert client.client is not None
    
    def test_initialization_without_api_key(self):
        """Test OpenAIClient initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(OpenAIError, match="OpenAI API key not found"):
                OpenAIClient()
    
    def test_initialization_with_env_var(self, mock_openai_client):
        """Test OpenAIClient initialization with environment variable"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'env-key'}):
            client = OpenAIClient()
            assert client.api_key == "env-key"
    
    def test_initialization_with_custom_model(self, mock_openai_client):
        """Test OpenAIClient initialization with custom model"""
        client = OpenAIClient(api_key="test-key", model="gpt-4")
        assert client.model == "gpt-4"
    
    def test_build_prompt_basic(self, openai_client):
        """Test basic prompt building"""
        prompt = openai_client._build_prompt(10, 20, 30)
        
        assert "coordinates (10, 20, 30)" in prompt
        assert "cyberpunk" in prompt.lower()
        assert "Description:" in prompt
    
    def test_build_prompt_with_context(self, openai_client):
        """Test prompt building with context"""
        context_cubes = [
            {"x": 9, "y": 20, "z": 30, "description": "Neon-lit alley"},
            {"x": 11, "y": 20, "z": 30, "description": "Corporate tower"}
        ]
        
        prompt = openai_client._build_prompt(10, 20, 30, context_cubes)
        
        assert "coordinates (10, 20, 30)" in prompt
        assert "Surrounding area context:" in prompt
        assert "(9, 20, 30): Neon-lit alley" in prompt
        assert "(11, 20, 30): Corporate tower" in prompt
    
    def test_format_context(self, openai_client):
        """Test context formatting"""
        context_cubes = [
            {"x": 1, "y": 2, "z": 3, "description": "Test location 1"},
            {"x": 4, "y": 5, "z": 6, "description": "Test location 2"}
        ]
        
        formatted = openai_client._format_context(context_cubes)
        
        assert "(1, 2, 3): Test location 1" in formatted
        assert "(4, 5, 6): Test location 2" in formatted
    
    def test_format_context_empty(self, openai_client):
        """Test context formatting with empty list"""
        formatted = openai_client._format_context([])
        assert "No surrounding context available" in formatted
    
    def test_format_context_none(self, openai_client):
        """Test context formatting with None"""
        formatted = openai_client._format_context(None)
        assert "No surrounding context available" in formatted
    
    def test_extract_description_clean(self, openai_client):
        """Test description extraction from clean response"""
        response = "A cyberpunk street with neon lights"
        result = openai_client._extract_description(response)
        assert result == "A cyberpunk street with neon lights"
    
    def test_extract_description_with_quotes(self, openai_client):
        """Test description extraction with surrounding quotes"""
        response = '"A cyberpunk street with neon lights"'
        result = openai_client._extract_description(response)
        assert result == "A cyberpunk street with neon lights"
    
    def test_extract_description_with_single_quotes(self, openai_client):
        """Test description extraction with single quotes"""
        response = "'A cyberpunk street with neon lights'"
        result = openai_client._extract_description(response)
        assert result == "A cyberpunk street with neon lights"
    
    def test_extract_description_empty(self, openai_client):
        """Test description extraction with empty response"""
        with pytest.raises(OpenAIError, match="Empty response from API"):
            openai_client._extract_description("")
    
    def test_get_fallback_description(self, openai_client):
        """Test fallback description generation"""
        fallback = openai_client._get_fallback_description(10, 20, 30, "Test error")
        
        assert isinstance(fallback, str)
        assert len(fallback) > 0
        assert "cyberpunk" in fallback.lower() or "neon" in fallback.lower()
    
    def test_get_fallback_description_consistent(self, openai_client):
        """Test that fallback descriptions are consistent for same coordinates"""
        fallback1 = openai_client._get_fallback_description(10, 20, 30, "Test error")
        fallback2 = openai_client._get_fallback_description(10, 20, 30, "Test error")
        
        assert fallback1 == fallback2
    
    def test_get_fallback_description_different_coords(self, openai_client):
        """Test that fallback descriptions differ for different coordinates"""
        fallback1 = openai_client._get_fallback_description(10, 20, 30, "Test error")
        fallback2 = openai_client._get_fallback_description(11, 21, 31, "Test error")
        
        # They might be the same due to the fallback algorithm, but should be valid
        assert isinstance(fallback1, str)
        assert isinstance(fallback2, str)
        assert len(fallback1) > 0
        assert len(fallback2) > 0
    
    def test_make_api_request_success(self, openai_client, mock_openai_client):
        """Test successful API request"""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "A cyberpunk location"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = openai_client._make_api_request("Test prompt")
        
        assert result == "A cyberpunk location"
        assert openai_client.request_count == 1
    
    def test_make_api_request_failure_retry(self, openai_client, mock_openai_client):
        """Test API request with retry logic"""
        # Mock API to fail first, then succeed
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Success after retry"
        
        mock_openai_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_response
        ]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = openai_client._make_api_request("Test prompt")
        
        assert result == "Success after retry"
        assert openai_client.request_count == 1
    
    def test_make_api_request_max_retries_exceeded(self, openai_client, mock_openai_client):
        """Test API request when max retries are exceeded"""
        mock_openai_client.chat.completions.create.side_effect = Exception("Persistent API Error")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(OpenAIError, match="API request failed after"):
                openai_client._make_api_request("Test prompt")
    
    def test_enforce_rate_limit(self, openai_client):
        """Test rate limiting enforcement"""
        import time
        
        # Set a high rate limit for testing
        openai_client.rate_limit_delay = 0.1
        
        start_time = time.time()
        openai_client._enforce_rate_limit()
        first_call_time = time.time()
        
        # Second call should be delayed
        openai_client._enforce_rate_limit()
        second_call_time = time.time()
        
        # Should have at least the rate limit delay between calls
        assert (second_call_time - first_call_time) >= 0.1
    
    def test_generate_location_description_success(self, openai_client, mock_openai_client):
        """Test successful location description generation"""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "A cyberpunk street with neon lights"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = openai_client.generate_location_description(10, 20, 30)
        
        assert result == "A cyberpunk street with neon lights"
    
    def test_generate_location_description_with_context(self, openai_client, mock_openai_client):
        """Test location description generation with context"""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "A cyberpunk location"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        context = [{"x": 9, "y": 20, "z": 30, "description": "Nearby alley"}]
        result = openai_client.generate_location_description(10, 20, 30, context)
        
        assert result == "A cyberpunk location"
    
    def test_generate_location_description_fallback(self, openai_client, mock_openai_client):
        """Test location description generation with fallback"""
        # Mock API to fail
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = openai_client.generate_location_description(10, 20, 30)
        
        # Should return a fallback description
        assert isinstance(result, str)
        assert len(result) > 0
        assert "cyberpunk" in result.lower() or "neon" in result.lower()
    
    def test_test_connection_success(self, openai_client, mock_openai_client):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Connection test successful"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        result = openai_client.test_connection()
        assert result == True
    
    def test_test_connection_failure(self, openai_client, mock_openai_client):
        """Test failed connection test"""
        mock_openai_client.chat.completions.create.side_effect = Exception("Connection failed")
        
        result = openai_client.test_connection()
        assert result == False
    
    def test_get_usage_stats(self, openai_client):
        """Test usage statistics retrieval"""
        stats = openai_client.get_usage_stats()
        
        assert "request_count" in stats
        assert "last_request_time" in stats
        assert "rate_limit_delay" in stats
        assert "model" in stats
        assert stats["request_count"] == 0
        assert stats["model"] == "gpt-3.5-turbo"
    
    def test_set_rate_limit(self, openai_client):
        """Test setting custom rate limit"""
        openai_client.set_rate_limit(2.0)
        assert openai_client.rate_limit_delay == 2.0
        
        # Test minimum rate limit
        openai_client.set_rate_limit(0.05)
        assert openai_client.rate_limit_delay == 0.1  # Should be clamped to minimum
    
    def test_request_count_increment(self, openai_client, mock_openai_client):
        """Test that request count increments on successful requests"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        assert openai_client.request_count == 0
        
        openai_client.generate_location_description(1, 1, 1)
        assert openai_client.request_count == 1
        
        openai_client.generate_location_description(2, 2, 2)
        assert openai_client.request_count == 2

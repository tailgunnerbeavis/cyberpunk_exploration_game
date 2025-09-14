"""
OpenAI API integration for content generation in Cyberpunk Exploration Game
"""

import os
import time
import random
from typing import Optional, Dict, Any, List
from openai import OpenAI
from config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, 
    OPENAI_TEMPERATURE, MAX_RETRIES, RETRY_DELAY
)


class OpenAIClient:
    """Manages OpenAI API integration for generating cyberpunk location descriptions"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = OPENAI_MODEL):
        """
        Initialize OpenAI client
        
        Args:
            api_key (str, optional): OpenAI API key. If None, uses config or environment variable
            model (str): OpenAI model to use
        """
        self.model = model
        self.api_key = api_key or OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise OpenAIError("OpenAI API key not found. Set OPENAI_API_KEY in config.py or environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_delay = 1.0  # Minimum delay between requests
    
    def generate_location_description(self, x: int, y: int, z: int, 
                                    context_cubes: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Generate a cyberpunk-themed location description
        
        Args:
            x, y, z (int): Coordinates of the location
            context_cubes (list, optional): List of surrounding cube data for context
            
        Returns:
            str: Generated location description
        """
        try:
            prompt = self._build_prompt(x, y, z, context_cubes)
            response = self._make_api_request(prompt)
            return self._extract_description(response)
            
        except Exception as e:
            return self._get_fallback_description(x, y, z, str(e))
    
    def _build_prompt(self, x: int, y: int, z: int, 
                     context_cubes: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Build the prompt for OpenAI API
        
        Args:
            x, y, z (int): Coordinates
            context_cubes (list, optional): Context information
            
        Returns:
            str: Formatted prompt
        """
        base_prompt = f"""You are a cyberpunk world generator. Create a vivid, immersive description for a location at coordinates ({x}, {y}, {z}) in a 100x100x100 cube world.

The description should be:
- You should never mention the coordinates in the description.
- Cyberpunk themed (neon lights, technology, urban decay, corporate control)
- 2-3 sentences long
- Atmospheric and immersive
- Unique to this specific location
- Include sensory details (sights, sounds, smells)
- Include details about the different directions that could be traveled to from this location (to the left, right, up, down, forward, backward is a brief description of the nearby cubes)

Location coordinates: ({x}, {y}, {z})"""

        if context_cubes:
            context_info = self._format_context(context_cubes)
            base_prompt += f"\n\nSurrounding area context:\n{context_info}"
            base_prompt += "\n\nWhen generating the description make sure the hint from the nearby cubes is consistent with this new location."
            base_prompt += "\n\nDo not copy direction descriptions from nearby cubes instead use the description of that cube as the hint for that direction from this location."
            base_prompt += "\n\nUse this context to make the description consistent with the surrounding area while still being unique to this specific location."
            base_prompt += "\n\nInclude details from the nearby cubes. (to the left, right, up, down, forward, backward is the context of that nearby cubes)"

        base_prompt += "\n\nDescription:"
        return base_prompt
    
    def _format_context(self, context_cubes: List[Dict[str, Any]]) -> str:
        """
        Format context cubes into readable text
        
        Args:
            context_cubes (list): List of cube data dictionaries
            
        Returns:
            str: Formatted context string
        """
        if not context_cubes:
            return "No surrounding context available."
        
        context_lines = []
        for cube in context_cubes:
            coords = f"({cube['x']}, {cube['y']}, {cube['z']})"
            desc = cube.get('description', 'Unknown location')
            context_lines.append(f"- {coords}: {desc}")
        
        return "\n".join(context_lines)
    
    def _make_api_request(self, prompt: str) -> str:
        """
        Make API request to OpenAI with rate limiting and retry logic
        
        Args:
            prompt (str): The prompt to send
            
        Returns:
            str: API response content
        """
        self._enforce_rate_limit()
        
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a creative cyberpunk world generator. Generate immersive, atmospheric descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=OPENAI_MAX_TOKENS,
                    temperature=OPENAI_TEMPERATURE
                )
                
                self.request_count += 1
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise OpenAIError(f"API request failed after {MAX_RETRIES} attempts: {e}")
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _extract_description(self, response: str) -> str:
        """
        Extract and clean the description from API response
        
        Args:
            response (str): Raw API response
            
        Returns:
            str: Cleaned description
        """
        # Remove any leading/trailing whitespace and quotes
        description = response.strip()
        
        # Remove surrounding quotes if present
        if description.startswith('"') and description.endswith('"'):
            description = description[1:-1]
        elif description.startswith("'") and description.endswith("'"):
            description = description[1:-1]
        
        # Ensure it's not empty
        if not description:
            raise OpenAIError("Empty response from API")
        
        return description
    
    def _get_fallback_description(self, x: int, y: int, z: int, error: str) -> str:
        """
        Generate fallback description when API fails
        
        Args:
            x, y, z (int): Coordinates
            error (str): Error message for logging
            
        Returns:
            str: Fallback description
        """
        # Log the error (in a real implementation, you'd use proper logging)
        print(f"Warning: API failed for ({x}, {y}, {z}): {error}")
        
        # Generate contextual fallback based on coordinates
        fallback_templates = [
            "A dimly lit cyberpunk alleyway with flickering neon signs casting eerie shadows on the wet pavement.",
            "An abandoned tech facility with exposed wiring and broken holographic displays scattered across the floor.",
            "A corporate plaza dominated by towering megacorp buildings, their windows reflecting the neon glow of the city below.",
            "A underground data hub with rows of humming servers and the constant buzz of electronic equipment.",
            "A rooftop garden oasis in the urban sprawl, where nature fights to reclaim space from the concrete jungle.",
            "A bustling street market where vendors sell black-market tech and illegal neural implants.",
            "A derelict subway station with flickering lights and the distant sound of trains echoing through the tunnels.",
            "A high-security corporate lobby with armed guards and biometric scanners at every entrance.",
            "A hacker's den filled with multiple monitors, energy drinks, and the glow of code scrolling across screens.",
            "A polluted canal where toxic waste mixes with rainwater, creating an otherworldly luminescent effect."
        ]
        
        # Use coordinates to select a consistent fallback
        seed = (x * 10000 + y * 100 + z) % len(fallback_templates)
        base_description = fallback_templates[seed]
        
        # Add coordinate-specific details
        if x < 25:
            location_context = "in the industrial district"
        elif x < 75:
            location_context = "in the central business district"
        else:
            location_context = "in the residential sector"
        
        if y < 25:
            height_context = "at street level"
        elif y < 75:
            height_context = "on the mid-level walkways"
        else:
            height_context = "on the upper levels"
        
        return f"{base_description} This location is {location_context} {height_context}."
    
    def test_connection(self) -> bool:
        """
        Test the OpenAI API connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'Connection test successful'"}],
                max_tokens=10,
                temperature=0
            )
            return "successful" in response.choices[0].message.content.lower()
        except Exception:
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for the client
        
        Returns:
            dict: Usage statistics
        """
        return {
            "request_count": self.request_count,
            "last_request_time": self.last_request_time,
            "rate_limit_delay": self.rate_limit_delay,
            "model": self.model
        }
    
    def set_rate_limit(self, delay: float):
        """
        Set custom rate limit delay
        
        Args:
            delay (float): Delay in seconds between requests
        """
        self.rate_limit_delay = max(0.1, delay)  # Minimum 0.1 second delay


class OpenAIError(Exception):
    """Custom exception for OpenAI API related errors"""
    pass

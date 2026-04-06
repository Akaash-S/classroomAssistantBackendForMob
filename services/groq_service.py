import os
import logging
import json
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.model = 'llama-3.3-70b-versatile'
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
        
    def is_available(self) -> bool:
        """Check if the service is available"""
        return bool(self.api_key and self.client)
    
    def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a summary of the given text using Groq SDK
        """
        try:
            if not self.is_available():
                logger.error("Groq service not available - check GROQ_API_KEY")
                return None
            
            logger.info(f"Generating summary with Groq using model {self.model}")
            
            prompt = f"""Please provide a concise summary of the following lecture transcript in no more than {max_length} words.
Focus on the main points and key concepts. Make it clear and easy to understand.

Lecture Transcript:
{text}

Summary:"""
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates clear and concise summaries of lecture transcripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
                top_p=0.95,
            )
            
            if completion.choices:
                summary = completion.choices[0].message.content.strip()
                logger.info(f"Summary generated successfully using Groq SDK, length: {len(summary)}")
                return summary
            
            logger.error("Groq SDK returned no choices in completion")
            return None
                
        except Exception as e:
            logger.error(f"Error generating summary with Groq SDK: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def extract_key_points(self, text: str, max_points: int = 10) -> Optional[List[str]]:
        """
        Extract key points from the given text using Groq SDK
        """
        try:
            if not self.is_available():
                logger.error("Groq service not available")
                return None
            
            prompt = f"""Extract the {max_points} most important key points from the following lecture transcript.
Return them as a JSON array of strings, each point should be concise and clear.

Lecture Transcript:
{text}

Return ONLY a valid JSON array of strings, no additional text."""
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts key points from lecture transcripts. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            
            if completion.choices:
                content = completion.choices[0].message.content.strip()
                try:
                    # Clean the response text
                    if content.startswith('```json'):
                        content = content[7:]
                    elif content.startswith('```'):
                        content = content[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    key_points = json.loads(content)
                    if isinstance(key_points, list):
                        return key_points
                except json.JSONDecodeError:
                    # Fallback to newline splitting if JSON fails
                    return [p.strip() for p in content.split('\n') if p.strip()]
            
            return []
                
        except Exception as e:
            logger.error(f"Error extracting key points with Groq SDK: {str(e)}")
            return []

    def extract_tasks(self, text: str) -> Optional[List[Dict[str, str]]]:
        """
        Extract tasks from the given text using Groq SDK
        """
        try:
            if not self.is_available():
                logger.error("Groq service not available")
                return None
            
            prompt = f"""Analyze the following lecture transcript and extract any tasks, assignments, or action items.
Lecture Transcript:
{text}

Return ONLY a valid JSON array of objects with the fields: title, description, priority (high/medium/low), due_date (YYYY-MM-DD or null)."""
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts tasks. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048,
            )
            
            if completion.choices:
                content = completion.choices[0].message.content.strip()
                logger.info(f"Raw task extraction content: {content[:100]}...")
                try:
                    if content.startswith('```json'):
                        content = content[7:]
                    elif content.startswith('```'):
                        content = content[3:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    tasks = json.loads(content)
                    return tasks if isinstance(tasks, list) else []
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON response for tasks")
            
            return []
                
        except Exception as e:
            logger.error(f"Error extracting tasks with Groq SDK: {str(e)}")
            return []

import os
import logging
import json
import requests
from typing import Optional, List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = 'https://api.groq.com/openai/v1'
        self.model = 'mixtral-8x7b-32768'  # Fast and capable model
        
    def is_available(self) -> bool:
        """Check if the service is available"""
        return bool(self.api_key)
    
    def extract_tasks(self, text: str) -> Optional[List[Dict[str, str]]]:
        """
        Extract tasks and assignments from the given text using Groq API
        
        Args:
            text: Text to extract tasks from
            
        Returns:
            List of task dictionaries or None if failed
        """
        try:
            if not self.api_key:
                logger.error("Groq API key not available")
                return None
            
            url = f"{self.base_url}/chat/completions"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            prompt = f"""Analyze the following lecture transcript and extract any tasks, assignments, homework, or action items mentioned.

For each task found, provide:
- title: A clear, concise title for the task (max 100 characters)
- description: A detailed description of what needs to be done (max 500 characters)
- priority: One of "high", "medium", or "low" based on urgency and importance
- due_date: If a specific date is mentioned, extract it in ISO format (YYYY-MM-DD), otherwise use null

Guidelines:
- Look for explicit assignments, homework, readings, projects, or study tasks
- Look for phrases like "for next class", "by tomorrow", "due on", "submit by", etc.
- If no specific date is mentioned but urgency is implied (e.g., "for next class"), estimate a reasonable due date
- Prioritize based on: deadlines mentioned (high), importance emphasized (medium), general tasks (low)
- Only extract actual tasks, not general lecture content
- If no tasks are found, return an empty array

Lecture Transcript:
{text}

Return ONLY a valid JSON array of objects with the fields: title, description, priority, due_date.
Example format:
[
  {{
    "title": "Complete Chapter 5 Exercises",
    "description": "Solve problems 1-10 from Chapter 5 on data structures",
    "priority": "high",
    "due_date": "2024-11-20"
  }}
]

JSON Response:"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts tasks and assignments from lecture transcripts. Always respond with valid JSON only, no additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2048,
                "top_p": 0.95,
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    
                    try:
                        # Clean the response text
                        content = content.strip()
                        
                        # Remove markdown code blocks if present
                        if content.startswith('```json'):
                            content = content[7:]
                        elif content.startswith('```'):
                            content = content[3:]
                        
                        if content.endswith('```'):
                            content = content[:-3]
                        
                        content = content.strip()
                        
                        # Parse JSON
                        tasks = json.loads(content)
                        
                        if isinstance(tasks, list):
                            # Validate and clean task data
                            validated_tasks = []
                            for task in tasks:
                                if isinstance(task, dict) and 'title' in task and 'description' in task:
                                    # Ensure all required fields exist
                                    validated_task = {
                                        'title': str(task.get('title', 'Untitled Task'))[:100],
                                        'description': str(task.get('description', ''))[:500],
                                        'priority': task.get('priority', 'medium').lower(),
                                        'due_date': task.get('due_date')
                                    }
                                    
                                    # Validate priority
                                    if validated_task['priority'] not in ['high', 'medium', 'low']:
                                        validated_task['priority'] = 'medium'
                                    
                                    # Validate due_date format
                                    if validated_task['due_date']:
                                        try:
                                            # Try to parse the date to validate format
                                            datetime.fromisoformat(str(validated_task['due_date']))
                                        except (ValueError, TypeError):
                                            # If invalid, set to None
                                            validated_task['due_date'] = None
                                    
                                    validated_tasks.append(validated_task)
                            
                            logger.info(f"Extracted {len(validated_tasks)} tasks using Groq API")
                            return validated_tasks if validated_tasks else []
                        else:
                            logger.error("Invalid response format - expected array")
                            return []
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Raw response: {content}")
                        return []
                else:
                    logger.error("No choices in response")
                    return []
            else:
                logger.error(f"Groq API request failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during task extraction: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error extracting tasks with Groq: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a summary of the given text using Groq API
        
        Args:
            text: Text to summarize
            max_length: Maximum length of the summary in words
            
        Returns:
            Generated summary or None if failed
        """
        try:
            if not self.api_key:
                logger.error("Groq API key not available")
                return None
            
            url = f"{self.base_url}/chat/completions"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            prompt = f"""Please provide a concise summary of the following lecture transcript in no more than {max_length} words.
Focus on the main points and key concepts. Make it clear and easy to understand.

Lecture Transcript:
{text}

Summary:"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates clear and concise summaries of lecture transcripts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
                "top_p": 0.95,
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    summary = result['choices'][0]['message']['content'].strip()
                    logger.info(f"Summary generated successfully using Groq API, length: {len(summary)}")
                    return summary
                else:
                    logger.error("No choices in response")
                    return None
            else:
                logger.error(f"Groq API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during summarization: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating summary with Groq: {str(e)}")
            return None
    
    def extract_key_points(self, text: str, max_points: int = 10) -> Optional[List[str]]:
        """
        Extract key points from the given text using Groq API
        
        Args:
            text: Text to extract key points from
            max_points: Maximum number of key points to extract
            
        Returns:
            List of key points or None if failed
        """
        try:
            if not self.api_key:
                logger.error("Groq API key not available")
                return None
            
            url = f"{self.base_url}/chat/completions"
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            }
            
            prompt = f"""Extract the {max_points} most important key points from the following lecture transcript.
Return them as a JSON array of strings, each point should be concise and clear.

Lecture Transcript:
{text}

Return ONLY a valid JSON array of strings, no additional text.
Example: ["Point 1", "Point 2", "Point 3"]

JSON Response:"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts key points from lecture transcripts. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
                "top_p": 0.95,
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    
                    try:
                        # Clean the response text
                        content = content.strip()
                        if content.startswith('```json'):
                            content = content[7:]
                        elif content.startswith('```'):
                            content = content[3:]
                        if content.endswith('```'):
                            content = content[:-3]
                        content = content.strip()
                        
                        key_points = json.loads(content)
                        if isinstance(key_points, list):
                            logger.info(f"Extracted {len(key_points)} key points using Groq API")
                            return key_points
                        else:
                            logger.error("Invalid response format - expected array")
                            return []
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract points from text
                        points = [point.strip() for point in content.split('\n') if point.strip()]
                        logger.info(f"Extracted {len(points)} key points using fallback method")
                        return points
                else:
                    logger.error("No choices in response")
                    return []
            else:
                logger.error(f"Groq API request failed: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during key points extraction: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error extracting key points with Groq: {str(e)}")
            return []

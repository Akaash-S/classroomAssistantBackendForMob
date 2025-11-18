import google.generativeai as genai
import os
import logging
import json
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = 'gemini-2.0-flash'
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models'
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use the specific model endpoint
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return bool(self.api_key and self.model)
    
    def generate_summary(self, text: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a summary of the given text using Gemini 2.0 Flash
        
        Args:
            text: Text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Generated summary or None if failed
        """
        try:
            if not self.api_key:
                logger.error("Gemini API key not available")
                return None
            
            # Use direct API call to Gemini 2.0 Flash
            url = f"{self.base_url}/{self.model_name}:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            prompt = f"""
            Please provide a concise summary of the following lecture transcript in no more than {max_length} words.
            Focus on the main points and key concepts. Make it clear and easy to understand.
            
            Lecture Transcript: {text}
            """
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params={'key': self.api_key},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    summary = result['candidates'][0]['content']['parts'][0]['text']
                    summary = summary.strip()
                    logger.info(f"Summary generated successfully using Gemini 2.0 Flash, length: {len(summary)}")
                    return summary
                else:
                    logger.error("No candidates in response")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during summarization: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None
    
    def extract_key_points(self, text: str, max_points: int = 10) -> Optional[List[str]]:
        """
        Extract key points from the given text using Gemini 2.0 Flash
        
        Args:
            text: Text to extract key points from
            max_points: Maximum number of key points to extract
            
        Returns:
            List of key points or None if failed
        """
        try:
            if not self.api_key:
                logger.error("Gemini API key not available")
                return None
            
            # Use direct API call to Gemini 2.0 Flash
            url = f"{self.base_url}/{self.model_name}:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            prompt = f"""
            Extract the {max_points} most important key points from the following lecture transcript.
            Return them as a JSON array of strings, each point should be concise and clear.
            
            Lecture Transcript: {text}
            
            Return only the JSON array, no additional text.
            """
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params={'key': self.api_key},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    try:
                        # Clean the response text
                        content = content.strip()
                        if content.startswith('```json'):
                            content = content[7:]
                        if content.endswith('```'):
                            content = content[:-3]
                        content = content.strip()
                        
                        key_points = json.loads(content)
                        if isinstance(key_points, list):
                            logger.info(f"Extracted {len(key_points)} key points using Gemini 2.0 Flash")
                            return key_points
                        else:
                            logger.error("Invalid response format - expected array")
                            return None
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract points from text
                        points = [point.strip() for point in content.split('\n') if point.strip()]
                        logger.info(f"Extracted {len(points)} key points using fallback method")
                        return points
                else:
                    logger.error("No candidates in response")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during key points extraction: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return None
    
    def extract_tasks(self, text: str) -> Optional[List[Dict[str, str]]]:
        """
        Extract tasks and assignments from the given text using Gemini 2.0 Flash
        
        Args:
            text: Text to extract tasks from
            
        Returns:
            List of task dictionaries or None if failed
        """
        try:
            if not self.api_key:
                logger.error("Gemini API key not available")
                return None
            
            # Use direct API call to Gemini 2.0 Flash
            url = f"{self.base_url}/{self.model_name}:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            prompt = f"""
            Analyze the following lecture transcript and extract any tasks, assignments, or action items mentioned.
            
            For each task found, provide:
            - title: A clear, concise title for the task
            - description: A detailed description of what needs to be done
            - priority: One of "high", "medium", or "low" based on urgency and importance
            - due_date: If mentioned, extract the due date in ISO format, otherwise null
            
            Return the results as a JSON array of objects with these fields.
            If no tasks are found, return an empty array.
            
            Lecture Transcript: {text}
            
            Return only the JSON array, no additional text.
            """
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params={'key': self.api_key},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    try:
                        # Clean the response text
                        content = content.strip()
                        if content.startswith('```json'):
                            content = content[7:]
                        if content.endswith('```'):
                            content = content[:-3]
                        content = content.strip()
                        
                        tasks = json.loads(content)
                        if isinstance(tasks, list):
                            logger.info(f"Extracted {len(tasks)} tasks using Gemini 2.0 Flash")
                            return tasks
                        else:
                            logger.error("Invalid response format - expected array")
                            return None
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Raw response: {content}")
                        return None
                else:
                    logger.error("No candidates in response")
                    return None
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during task extraction: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error extracting tasks: {str(e)}")
            return None
    
    def generate_quiz_questions(self, text: str, num_questions: int = 5) -> Optional[List[Dict[str, str]]]:
        """
        Generate quiz questions based on the given text using Gemini
        
        Args:
            text: Text to generate questions from
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries or None if failed
        """
        try:
            if not self.model:
                logger.error("Gemini model not available")
                return None
            
            prompt = f"""
            Generate {num_questions} quiz questions based on the following text.
            For each question, provide:
            - question: The question text
            - options: An array of 4 multiple choice options
            - correct_answer: The index (0-3) of the correct option
            - explanation: A brief explanation of why this is the correct answer
            
            Return the results as a JSON array of objects with these fields.
            
            Text: {text}
            
            Return only the JSON array, no additional text.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                try:
                    questions = json.loads(response.text.strip())
                    if isinstance(questions, list):
                        logger.info(f"Generated {len(questions)} quiz questions")
                        return questions
                    else:
                        logger.error("Invalid response format - expected array")
                        return None
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON response for quiz generation")
                    return None
            else:
                logger.error("Failed to generate quiz questions - no response from Gemini")
                return None
                
        except Exception as e:
            logger.error(f"Error generating quiz questions: {str(e)}")
            return None
    
    def analyze_sentiment(self, text: str) -> Optional[Dict[str, str]]:
        """
        Analyze the sentiment of the given text using Gemini
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis result or None if failed
        """
        try:
            if not self.model:
                logger.error("Gemini model not available")
                return None
            
            prompt = f"""
            Analyze the sentiment of the following text and provide:
            - sentiment: One of "positive", "negative", or "neutral"
            - confidence: A number between 0 and 1 indicating confidence
            - explanation: A brief explanation of the sentiment analysis
            
            Text: {text}
            
            Return the results as a JSON object with these fields.
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                try:
                    sentiment = json.loads(response.text.strip())
                    if isinstance(sentiment, dict):
                        logger.info("Sentiment analysis completed")
                        return sentiment
                    else:
                        logger.error("Invalid response format - expected object")
                        return None
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON response for sentiment analysis")
                    return None
            else:
                logger.error("Failed to analyze sentiment - no response from Gemini")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None

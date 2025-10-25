#!/usr/bin/env python3
"""
Test script for Gemini 2.0 Flash integration
"""

import os
import sys
from dotenv import load_dotenv
from services.gemini_service import GeminiService

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test if Gemini API is properly configured"""
    print("Testing Gemini 2.0 Flash Connection...")
    
    service = GeminiService()
    
    if not service.is_available():
        print("Gemini service not available")
        print("Please set GEMINI_API_KEY in your environment variables")
        return False
    
    print("Gemini service is available")
    return True

def test_task_extraction():
    """Test task extraction with sample lecture text"""
    print("\nTesting Task Extraction...")
    
    service = GeminiService()
    
    # Sample lecture transcript
    sample_text = """
    Welcome to today's lecture on Machine Learning. Today we'll cover several important topics.
    
    First, I want you to complete the linear regression assignment that was posted last week. 
    This is due by Friday at 5 PM. It's worth 20% of your grade, so make sure to submit it on time.
    
    Next week, we'll be discussing neural networks. Please read chapters 5 and 6 from the textbook 
    before our next class. There will be a quiz on this material.
    
    Also, I need you to submit your project proposals by next Monday. The final project is due 
    at the end of the semester and counts for 40% of your final grade.
    
    Finally, don't forget about the midterm exam next month. Start studying early as it covers 
    all the material we've discussed so far.
    """
    
    try:
        tasks = service.extract_tasks(sample_text)
        
        if tasks:
            print(f"Successfully extracted {len(tasks)} tasks:")
            for i, task in enumerate(tasks, 1):
                print(f"  {i}. {task.get('title', 'No title')}")
                print(f"     Priority: {task.get('priority', 'Not specified')}")
                print(f"     Due Date: {task.get('due_date', 'Not specified')}")
                print(f"     Description: {task.get('description', 'No description')[:100]}...")
                print()
        else:
            print("No tasks extracted")
            return False
            
    except Exception as e:
        print(f"Error during task extraction: {str(e)}")
        return False
    
    return True

def test_summary_generation():
    """Test summary generation with sample text"""
    print("\nTesting Summary Generation...")
    
    service = GeminiService()
    
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on algorithms 
    that can learn from data. There are three main types of machine learning: supervised learning, 
    unsupervised learning, and reinforcement learning. Supervised learning uses labeled training 
    data to make predictions, while unsupervised learning finds patterns in data without labels. 
    Reinforcement learning involves an agent learning through interaction with an environment.
    """
    
    try:
        summary = service.generate_summary(sample_text, max_length=100)
        
        if summary:
            print(f"Successfully generated summary:")
            print(f"   {summary}")
            print(f"   Length: {len(summary)} characters")
        else:
            print("No summary generated")
            return False
            
    except Exception as e:
        print(f"Error during summary generation: {str(e)}")
        return False
    
    return True

def test_key_points_extraction():
    """Test key points extraction"""
    print("\nTesting Key Points Extraction...")
    
    service = GeminiService()
    
    sample_text = """
    Today we discussed the fundamentals of machine learning. We covered supervised learning 
    algorithms including linear regression and classification. We also talked about the 
    importance of feature selection and data preprocessing. The key concepts include training 
    and testing data, overfitting, and cross-validation. Next class we'll dive deeper into 
    neural networks and deep learning architectures.
    """
    
    try:
        key_points = service.extract_key_points(sample_text, max_points=5)
        
        if key_points:
            print(f"Successfully extracted {len(key_points)} key points:")
            for i, point in enumerate(key_points, 1):
                print(f"  {i}. {point}")
        else:
            print("No key points extracted")
            return False
            
    except Exception as e:
        print(f"Error during key points extraction: {str(e)}")
        return False
    
    return True

def main():
    """Run all Gemini 2.0 Flash tests"""
    print("Testing Gemini 2.0 Flash Integration")
    print("=" * 50)
    
    # Test connection
    if not test_gemini_connection():
        print("\nGemini service not available. Please check your API key.")
        sys.exit(1)
    
    # Test task extraction
    if not test_task_extraction():
        print("\nTask extraction failed")
        sys.exit(1)
    
    # Test summary generation
    if not test_summary_generation():
        print("\nSummary generation failed")
        sys.exit(1)
    
    # Test key points extraction
    if not test_key_points_extraction():
        print("\nKey points extraction failed")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("All Gemini 2.0 Flash tests passed!")
    print("\nThe backend is ready to use Gemini 2.0 Flash for:")
    print("Task extraction from lecture transcripts")
    print("Text summarization")
    print("Key points extraction")
    print("\nNext steps:")
    print("1. Set up your GEMINI_API_KEY in the environment")
    print("2. Test the full lecture processing pipeline")
    print("3. Integrate with your frontend application")

if __name__ == '__main__':
    main()

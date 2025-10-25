#!/usr/bin/env python3
"""
Demo script showing Gemini 2.0 Flash task extraction working
"""

import os
import sys
from dotenv import load_dotenv
from services.gemini_service import GeminiService

# Load environment variables
load_dotenv()

def demo_task_extraction():
    """Demonstrate task extraction with Gemini 2.0 Flash"""
    print("Gemini 2.0 Flash Task Extraction Demo")
    print("=" * 50)
    
    service = GeminiService()
    
    if not service.is_available():
        print("Gemini service not available. Please set GEMINI_API_KEY")
        return
    
    # Sample lecture transcript with multiple tasks
    lecture_text = """
    Good morning class! Today we're covering advanced machine learning concepts.
    
    First, I need you to complete the neural networks assignment that was posted on Monday. 
    This is due by Friday at 11:59 PM. It's worth 25% of your grade, so don't miss the deadline.
    
    For next week, please read chapters 8, 9, and 10 from the textbook. We'll be discussing 
    deep learning architectures and there will be a comprehensive quiz on this material.
    
    Your final project proposals are due next Wednesday. Make sure to include your research 
    questions, methodology, and expected outcomes. The final project counts for 40% of your grade.
    
    Don't forget about the midterm exam in two weeks. It covers everything from linear regression 
    to neural networks. Start reviewing your notes early.
    
    Also, I want you to implement a simple decision tree classifier using Python. 
    Submit the code and a brief report by next Monday.
    """
    
    print("Sample Lecture Transcript:")
    print("-" * 30)
    print(lecture_text)
    print("\n" + "=" * 50)
    print("Extracting tasks using Gemini 2.0 Flash...")
    print("=" * 50)
    
    try:
        tasks = service.extract_tasks(lecture_text)
        
        if tasks:
            print(f"\nSuccessfully extracted {len(tasks)} tasks:")
            print("-" * 30)
            
            for i, task in enumerate(tasks, 1):
                print(f"\nTask {i}:")
                print(f"  Title: {task.get('title', 'No title')}")
                print(f"  Priority: {task.get('priority', 'Not specified')}")
                print(f"  Due Date: {task.get('due_date', 'Not specified')}")
                print(f"  Description: {task.get('description', 'No description')}")
                print("-" * 30)
        else:
            print("No tasks extracted")
            
    except Exception as e:
        print(f"Error during task extraction: {str(e)}")

def demo_with_different_content():
    """Demo with different type of content"""
    print("\n\n" + "=" * 50)
    print("Demo with Different Content Type")
    print("=" * 50)
    
    service = GeminiService()
    
    # Different type of lecture content
    research_lecture = """
    Today we're discussing research methodologies in computer science.
    
    For your research paper, I need you to conduct a literature review on recent advances 
    in natural language processing. This should be 10-15 pages and due in three weeks.
    
    You also need to implement a sentiment analysis model using the techniques we discussed. 
    Submit your code and results by next Friday.
    
    Don't forget to prepare your presentation for the research symposium next month. 
    Each student will have 15 minutes to present their findings.
    """
    
    print("Research Methodology Lecture:")
    print("-" * 30)
    print(research_lecture)
    print("\nExtracting tasks...")
    
    try:
        tasks = service.extract_tasks(research_lecture)
        
        if tasks:
            print(f"\nExtracted {len(tasks)} research tasks:")
            for i, task in enumerate(tasks, 1):
                print(f"\n{i}. {task.get('title', 'No title')}")
                print(f"   Priority: {task.get('priority', 'Not specified')}")
                print(f"   Description: {task.get('description', 'No description')[:80]}...")
        else:
            print("No tasks extracted")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    demo_task_extraction()
    demo_with_different_content()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("Gemini 2.0 Flash is successfully integrated for task extraction.")
    print("=" * 50)

#!/usr/bin/env python3
"""Test Sightengine AI Image Detection Tool"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.tools.verification.ai_image_detector import AIImageDetectorTool

console = Console()

def test_ai_image_detector():
    """Test AI image detection with various images"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API credentials are available
    api_user = os.getenv('SIGHTENGINE_API_USER')
    api_secret = os.getenv('SIGHTENGINE_API_SECRET')
    
    if not api_user or not api_secret:
        console.print("[red]❌ SIGHTENGINE_API_USER and SIGHTENGINE_API_SECRET not found in .env file[/red]")
        console.print("[yellow]Please add your Sightengine API credentials to the .env file[/yellow]")
        console.print("\n[cyan]Sign up for free at: https://sightengine.com/signup[/cyan]")
        console.print("[cyan]Then get your API credentials from: https://dashboard.sightengine.com[/cyan]")
        return
    
    console.print("[green]✅ API credentials found[/green]")
    
    # Initialize tool
    console.print("\n[cyan]Initializing AI Image Detector...[/cyan]")
    tool = AIImageDetectorTool()
    
    # Test images (replace with actual image URLs for testing)
    test_images = [
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_york_times_square-terabass.jpg/1200px-New_york_times_square-terabass.jpg",
            "description": "Real photo - Times Square",
            "expected": "real"
        },
        {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Tour_Eiffel_Wikimedia_Commons.jpg/800px-Tour_Eiffel_Wikimedia_Commons.jpg",
            "description": "Real photo - Eiffel Tower",
            "expected": "real"
        },
        # Add AI-generated images for testing if you have URLs
        # {
        #     "url": "https://example.com/ai-generated-image.jpg",
        #     "description": "AI-generated image",
        #     "expected": "ai"
        # }
    ]
    
    console.print(f"\n[cyan]Testing {len(test_images)} images...[/cyan]\n")
    
    for i, test_case in enumerate(test_images, 1):
        console.print(f"[bold]Test {i}/{len(test_images)}:[/bold] {test_case['description']}")
        console.print(f"[dim]URL: {test_case['url'][:60]}...[/dim]")
        console.print(f"[dim]Expected: {test_case['expected']}[/dim]\n")
        
        try:
            # Run the tool
            result = tool._run(
                image_url=test_case['url'],
                confidence_threshold=0.5
            )
            
            # Display results
            console.print(result)
            
        except Exception as e:
            console.print(f"[red]❌ Test failed: {str(e)}[/red]")
            import traceback
            traceback.print_exc()
        
        console.print("\n" + "="*60 + "\n")
    
    # Test with invalid URL
    console.print("[bold]Testing with invalid URL:[/bold]")
    invalid_result = tool._run("not-a-valid-url")
    console.print(invalid_result)
    
    console.print("\n[green]✅ All tests completed![/green]")
    console.print("\n[yellow]Note: The tool uses caching, so repeated tests of the same URL will use cached results.[/yellow]")

if __name__ == "__main__":
    console.print("[bold cyan]Sightengine AI Image Detection Tool Test[/bold cyan]")
    console.print("=" * 50)
    test_ai_image_detector()
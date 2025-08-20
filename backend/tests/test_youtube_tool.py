#!/usr/bin/env python3
"""Test YouTube Comment Analysis Tool"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.tools.community.youtube_tool import YouTubeTool

console = Console()

def test_youtube_tool():
    """Test YouTube search and comment analysis"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        console.print("[red]❌ GOOGLE_API_KEY or YOUTUBE_API_KEY not found in .env file[/red]")
        console.print("[yellow]Please add your Google API key to the .env file[/yellow]")
        return
    
    console.print("[green]✅ API key found[/green]")
    
    # Initialize tool
    console.print("\n[cyan]Initializing YouTube tool...[/cyan]")
    tool = YouTubeTool()
    
    # Test query
    test_query = "2024년 한국 경제 전망"
    console.print(f"\n[cyan]Testing with query: '{test_query}'[/cyan]")
    console.print("[yellow]Searching YouTube videos and analyzing comments...[/yellow]\n")
    
    try:
        # Run the tool
        result = tool._run(
            query=test_query,
            max_videos=2,  # Limit to 2 videos for testing
            max_comments=30,  # Get top 30 comments per video
            language="ko"
        )
        
        # Display results
        console.print("[green]✅ Test successful![/green]\n")
        console.print(result)
        
    except Exception as e:
        console.print(f"[red]❌ Test failed: {str(e)}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    console.print("[bold cyan]YouTube Comment Analysis Tool Test[/bold cyan]")
    console.print("=" * 50)
    test_youtube_tool()
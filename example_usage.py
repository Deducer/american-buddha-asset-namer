#!/usr/bin/env python3
"""
Example usage of American Buddha Asset Namer
This shows how to use the tool programmatically without the GUI
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, 'src')

from utils.config import Config
from processors.ai_analyzer import AIAnalyzer
from processors.file_processor import FileProcessor

def main():
    # Load configuration
    config = Config()
    
    # Initialize components
    ai_analyzer = AIAnalyzer()
    file_processor = FileProcessor(config, ai_analyzer)
    
    # Example 1: Process a single directory
    print("Example 1: Processing a directory")
    print("-" * 50)
    
    # Specify the directory to process
    directory = Path.home() / "Pictures" / "test_folder"  # Change this to your folder
    
    if directory.exists():
        # Scan for media files
        files = file_processor.scan_directory(directory)
        print(f"Found {len(files)} media files")
        
        # Process files with default naming pattern
        results = file_processor.process_files(
            files,
            pattern_name="documentary",  # or "default", "location_based", etc.
            progress_callback=lambda current, total: print(f"Processing {current}/{total}...")
        )
        
        print(f"\nProcessing complete:")
        print(f"- Processed: {results['processed']}")
        print(f"- Errors: {results['errors']}")
        
        # Show suggestions
        print("\nSuggested renames:")
        for suggestion in results['suggestions'][:5]:  # Show first 5
            print(f"  {suggestion['original_name']} -> {suggestion['new_name']}")
        
        # To apply the renames (uncomment to actually rename files):
        # apply_results = file_processor.apply_renames(results['suggestions'])
        # print(f"\nRenamed {apply_results['renamed']} files")
    
    # Example 2: Custom naming pattern
    print("\n\nExample 2: Custom naming pattern")
    print("-" * 50)
    
    custom_pattern = "{date}_DOC_{description}_{sequence}"
    
    # You can process with a custom pattern
    # results = file_processor.process_files(
    #     files,
    #     custom_pattern=custom_pattern
    # )
    
    # Example 3: Analyze a single image
    print("\n\nExample 3: Analyzing a single image")
    print("-" * 50)
    
    image_path = Path("example.jpg")  # Change to your image
    if image_path.exists():
        analysis = ai_analyzer.analyze_image(image_path)
        print(f"Analysis for {image_path.name}:")
        print(f"- Description: {analysis.get('description')}")
        print(f"- Scene Type: {analysis.get('scene_type')}")
        print(f"- Subjects: {', '.join(analysis.get('subjects', []))}")
        print(f"- AI Analyzed: {analysis.get('ai_analyzed')}")

if __name__ == "__main__":
    main()
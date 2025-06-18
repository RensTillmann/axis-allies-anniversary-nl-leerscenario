#!/usr/bin/env python3
"""
Example script showing how to load the modular campaign structure.
"""

import json
import os

def load_campaign_index(index_path='campaign.json'):
    """Load the campaign index file"""
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_campaign_component(filepath):
    """Load a specific campaign component"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Load the index
    print("Loading campaign index...")
    index = load_campaign_index()
    
    print(f"\nCampaign format version: {index['_format_version']}")
    print(f"Created: {index['_created']}")
    
    # Load metadata
    print("\nLoading campaign metadata...")
    metadata = load_campaign_component(index['metadata_file'])
    print(f"Campaign title: {metadata['campaign_metadata']['title']}")
    print(f"Timeline: {metadata['campaign_metadata']['timeline']}")
    print(f"Total chapters: {metadata['campaign_metadata']['chapters']}")
    
    # Load initial setup
    print("\nLoading initial setup...")
    setup = load_campaign_component(index['initial_setup_file'])
    if 'turn_order' in setup:
        print(f"Starting nations: {', '.join(setup['turn_order'])}")
    else:
        print(f"Setup includes: {', '.join(list(setup.keys())[:5])}...")
    
    # List available chapters
    print("\nAvailable chapters:")
    for i, chapter in enumerate(index['chapters'], 1):
        print(f"  {i}. {chapter['name']} - {chapter['file']}")
    
    # Example: Load a specific chapter
    chapter_to_load = 0  # Load first chapter
    if chapter_to_load < len(index['chapters']):
        chapter_info = index['chapters'][chapter_to_load]
        print(f"\nLoading {chapter_info['name']}...")
        chapter_data = load_campaign_component(chapter_info['file'])
        
        # Show chapter overview
        if 'overview' in chapter_data:
            print(f"Chapter overview: {chapter_data['overview']['🎯_chapter_focus']}")
            print(f"Learning goals: {', '.join(chapter_data['overview']['🎓_what_you_learn'])}")

if __name__ == "__main__":
    main()
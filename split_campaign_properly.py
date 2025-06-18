#!/usr/bin/env python3
"""
Split campaign.json into modular structure with separate chapter files.
This version properly handles the actual campaign.json structure.
"""

import json
import os
import shutil
from datetime import datetime
from collections import OrderedDict

def load_campaign_data(filepath):
    """Load the campaign.json file"""
    print(f"Loading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=OrderedDict)

def save_json(data, filepath, indent=2):
    """Save data as JSON with proper formatting"""
    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, separators=(',', ': '))
        f.write('\n')  # Add newline at end
    print(f"Created: {filepath} ({len(json.dumps(data))} bytes)")

def create_backup(filepath):
    """Create a timestamped backup of the original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def split_campaign(data):
    """Split campaign data into logical components"""
    
    # Create metadata file
    metadata = OrderedDict()
    metadata_keys = ['campaign_metadata', 'learning_progression', 
                     'campaign_verification_summary', 'quick_learning_reference']
    
    for key in metadata_keys:
        if key in data:
            metadata[key] = data[key]
    
    # Extract initial setup
    initial_setup = None
    if 'initial_setup_1941' in data:
        initial_setup = data['initial_setup_1941']
    
    # Extract chapters and their end states
    chapters = OrderedDict()
    chapter_patterns = [
        ('chapter_1_june_22_23_1941', 'chapter_1_june_22_23_1941_end_state'),
        ('chapter_2_october_1941', 'chapter_2_october_1941_end_state'),
        ('chapter_3_december_1941', 'chapter_3_december_1941_end_state'),
        ('chapter_4_december_7_1941', 'chapter_4_december_7_1941_end_state'),
        ('chapter_5_spring_1942', 'chapter_5_spring_1942_end_state'),
        ('chapter_6_summer_1942', 'chapter_6_summer_1942_end_state'),
        ('chapter_7_autumn_1942', 'chapter_7_autumn_1942_end_state'),
        ('chapter_8_winter_1942_43', 'chapter_8_winter_1942_43_end_state'),
        ('chapter_9_spring_1943', 'chapter_9_spring_1943_end_state'),
        ('chapter_10_china_theater', None)  # No end state for final chapter
    ]
    
    for chapter_key, end_state_key in chapter_patterns:
        if chapter_key in data:
            chapter_data = OrderedDict()
            chapter_data[chapter_key] = data[chapter_key]
            
            # Include the end state in the same file
            if end_state_key and end_state_key in data:
                chapter_data[f"{chapter_key}_end_state"] = data[end_state_key]
            
            chapters[chapter_key] = chapter_data
    
    return metadata, initial_setup, chapters

def create_index_file(chapter_info):
    """Create the new campaign.json index file"""
    index = OrderedDict()
    
    index['_description'] = 'Axis & Allies Anniversary Campaign - Modular Index'
    index['_created'] = datetime.now().isoformat()
    index['_format_version'] = '2.0'
    index['_note'] = 'Load this index first, then load referenced files as needed'
    
    index['campaign_structure'] = OrderedDict()
    index['campaign_structure']['metadata'] = 'chapters/metadata.json'
    index['campaign_structure']['initial_setup'] = 'chapters/initial_setup_1941.json'
    
    index['campaign_structure']['chapters'] = []
    for num, (key, filename) in enumerate(chapter_info, 1):
        chapter_entry = OrderedDict()
        chapter_entry['number'] = num
        chapter_entry['key'] = key
        chapter_entry['file'] = f'chapters/{filename}'
        
        # Add descriptive names
        if 'june_22_23_1941' in key:
            chapter_entry['title'] = 'Operation Barbarossa - The Blitzkrieg Lesson'
        elif 'october_1941' in key:
            chapter_entry['title'] = 'The Moscow Offensive - Quality vs Quantity'
        elif 'december_1941' in key and 'december_7' not in key:
            chapter_entry['title'] = 'Battle of Britain - Strategic Bombing'
        elif 'december_7_1941' in key:
            chapter_entry['title'] = 'Pearl Harbor - The Pacific War Begins'
        elif 'spring_1942' in key:
            chapter_entry['title'] = 'Global Conflict - Shore Bombardment & Tank Blitzing'
        elif 'summer_1942' in key:
            chapter_entry['title'] = 'Technology Race - Research & Development'
        elif 'autumn_1942' in key:
            chapter_entry['title'] = 'Atlantic Crisis - Canal Control & Convoy Raids'
        elif 'winter_1942_43' in key:
            chapter_entry['title'] = 'Submarine Warfare - Neutral Invasion Consequences'
        elif 'spring_1943' in key:
            chapter_entry['title'] = 'The Counter-Attack - Coalition Victory'
        elif 'china_theater' in key:
            chapter_entry['title'] = 'China Theater - Special Rules & Victory'
        
        index['campaign_structure']['chapters'].append(chapter_entry)
    
    index['loading_instructions'] = OrderedDict()
    index['loading_instructions']['full_campaign'] = 'Load all files in sequence'
    index['loading_instructions']['single_chapter'] = 'Load metadata.json, initial_setup_1941.json, and desired chapter file'
    index['loading_instructions']['continue_game'] = 'Load metadata.json and chapter files from current position onward'
    
    return index

def main():
    """Main function to split campaign.json"""
    campaign_file = 'campaign_full.json'  # Using the full backup
    output_file = 'campaign.json'
    chapters_dir = 'chapters'
    
    # Check if campaign file exists
    if not os.path.exists(campaign_file):
        print(f"Error: {campaign_file} not found!")
        return
    
    # Load the campaign data
    data = load_campaign_data(campaign_file)
    
    # Create chapters directory
    if not os.path.exists(chapters_dir):
        os.makedirs(chapters_dir)
        print(f"Created directory: {chapters_dir}")
    
    # Split the campaign
    metadata, initial_setup, chapters = split_campaign(data)
    
    # Save metadata
    save_json(metadata, os.path.join(chapters_dir, 'metadata.json'))
    
    # Save initial setup
    if initial_setup:
        save_json(initial_setup, os.path.join(chapters_dir, 'initial_setup_1941.json'))
    
    # Save chapters
    chapter_info = []
    for chapter_key, chapter_data in chapters.items():
        # Create friendly filename
        if 'june_22_23_1941' in chapter_key:
            filename = 'chapter_01_barbarossa.json'
        elif 'october_1941' in chapter_key and 'december_7' not in chapter_key:
            filename = 'chapter_02_moscow.json'
        elif 'december_1941' in chapter_key and 'december_7' not in chapter_key:
            filename = 'chapter_03_britain.json'
        elif 'december_7_1941' in chapter_key:
            filename = 'chapter_04_pearl_harbor.json'
        elif 'spring_1942' in chapter_key:
            filename = 'chapter_05_global_conflict.json'
        elif 'summer_1942' in chapter_key:
            filename = 'chapter_06_technology.json'
        elif 'autumn_1942' in chapter_key:
            filename = 'chapter_07_atlantic.json'
        elif 'winter_1942_43' in chapter_key:
            filename = 'chapter_08_submarines.json'
        elif 'spring_1943' in chapter_key:
            filename = 'chapter_09_victory.json'
        elif 'china_theater' in chapter_key:
            filename = 'chapter_10_china.json'
        else:
            filename = f"{chapter_key}.json"
        
        filepath = os.path.join(chapters_dir, filename)
        save_json(chapter_data, filepath)
        chapter_info.append((chapter_key, filename))
    
    # Create the new index file
    index_data = create_index_file(chapter_info)
    save_json(index_data, output_file)
    
    # Summary
    print("\n" + "="*60)
    print("CAMPAIGN SPLIT SUMMARY")
    print("="*60)
    print(f"✅ Created {len(chapters)} chapter files in {chapters_dir}/")
    print(f"✅ Created metadata.json with campaign info and learning progression")
    print(f"✅ Created initial_setup_1941.json with game setup")
    print(f"✅ Created new campaign.json as modular index")
    print(f"\nOriginal file size: {os.path.getsize(campaign_file):,} bytes")
    
    # Calculate new total size
    total_size = os.path.getsize(output_file)
    for file in os.listdir(chapters_dir):
        if file.endswith('.json'):
            total_size += os.path.getsize(os.path.join(chapters_dir, file))
    
    print(f"New total size: {total_size:,} bytes")
    print(f"Average chapter size: {total_size // (len(chapters) + 2):,} bytes")
    
    print("\n📁 File Structure:")
    print(f"   campaign.json (index)")
    print(f"   chapters/")
    print(f"      metadata.json")
    print(f"      initial_setup_1941.json")
    for _, filename in sorted(chapter_info):
        print(f"      {filename}")

if __name__ == "__main__":
    main()
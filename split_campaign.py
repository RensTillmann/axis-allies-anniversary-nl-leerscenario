#!/usr/bin/env python3
"""
Split campaign.json into modular structure with separate chapter files.
Creates backups and verifies no data is lost.
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
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, separators=(',', ': '))
    print(f"Created: {filepath}")

def create_backup(filepath):
    """Create a timestamped backup of the original file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def extract_metadata(data):
    """Extract metadata and learning progression"""
    metadata = OrderedDict()
    
    # Extract campaign metadata
    if 'campaign_metadata' in data:
        metadata['campaign_metadata'] = data['campaign_metadata']
    
    # Extract learning progression
    if 'learning_progression' in data:
        metadata['learning_progression'] = data['learning_progression']
    
    # Extract verification summary
    if 'campaign_verification_summary' in data:
        metadata['campaign_verification_summary'] = data['campaign_verification_summary']
    
    # Extract quick learning reference
    if 'quick_learning_reference' in data:
        metadata['quick_learning_reference'] = data['quick_learning_reference']
    
    return metadata

def extract_initial_setup(data):
    """Extract initial setup 1941"""
    if 'initial_setup_1941' in data:
        return data['initial_setup_1941']
    return None

def extract_chapters(data):
    """Extract all chapter data"""
    chapters = OrderedDict()
    
    # Define the chapter keys and their friendly names
    chapter_mappings = [
        ('chapter_1_june_22_23_1941', 'chapter_1_barbarossa'),
        ('chapter_2_october_1941', 'chapter_2_moscow'),
        ('chapter_3_december_1941', 'chapter_3_pearl_harbor_prep'),
        ('chapter_4_december_7_1941', 'chapter_4_pearl_harbor'),
        ('chapter_5_spring_1942', 'chapter_5_global_conflict'),
        ('chapter_6_summer_1942', 'chapter_6_technology_race'),
        ('chapter_7_autumn_1942', 'chapter_7_strategic_chokepoints'),
        ('chapter_8_winter_1942_43', 'chapter_8_submarine_warfare'),
        ('chapter_9_spring_1943', 'chapter_9_endgame'),
        ('chapter_10_china_theater', 'chapter_10_china_rules')
    ]
    
    # Extract each chapter
    for old_key, new_key in chapter_mappings:
        if old_key in data:
            chapters[new_key] = data[old_key]
    
    return chapters

def create_index_file(chapter_files):
    """Create the new campaign.json index file"""
    index = OrderedDict()
    
    index['_description'] = 'Campaign index file - points to modular chapter files'
    index['_created'] = datetime.now().isoformat()
    index['_format_version'] = '2.0'
    
    index['metadata_file'] = 'chapters/metadata.json'
    index['initial_setup_file'] = 'chapters/initial_setup_1941.json'
    
    index['chapters'] = []
    for filename, friendly_name in chapter_files:
        index['chapters'].append({
            'file': f'chapters/{filename}',
            'name': friendly_name
        })
    
    index['usage'] = {
        'description': 'This index file points to all campaign components',
        'loading': 'Load this file first, then load referenced files as needed',
        'backwards_compatible': 'Original campaign.json backed up with timestamp'
    }
    
    return index

def verify_data_integrity(original_data, chapters_dir):
    """Verify that no data was lost during the split"""
    print("\nVerifying data integrity...")
    
    # Load all split files
    reconstructed = OrderedDict()
    
    # Load metadata
    with open(os.path.join(chapters_dir, 'metadata.json'), 'r', encoding='utf-8') as f:
        metadata = json.load(f, object_pairs_hook=OrderedDict)
        reconstructed.update(metadata)
    
    # Load initial setup
    with open(os.path.join(chapters_dir, 'initial_setup_1941.json'), 'r', encoding='utf-8') as f:
        reconstructed['initial_setup_1941'] = json.load(f, object_pairs_hook=OrderedDict)
    
    # Load chapters
    chapter_files = [f for f in os.listdir(chapters_dir) if f.startswith('chapter_') and f.endswith('.json')]
    for chapter_file in sorted(chapter_files):
        with open(os.path.join(chapters_dir, chapter_file), 'r', encoding='utf-8') as f:
            chapter_data = json.load(f, object_pairs_hook=OrderedDict)
            # Map back to original keys
            if 'chapter_1_barbarossa' in chapter_file:
                reconstructed['chapter_1_june_22_23_1941'] = chapter_data
            elif 'chapter_2_moscow' in chapter_file:
                reconstructed['chapter_2_october_1941'] = chapter_data
            elif 'chapter_3_pearl_harbor_prep' in chapter_file:
                reconstructed['chapter_3_december_1941'] = chapter_data
            elif 'chapter_4_pearl_harbor' in chapter_file:
                reconstructed['chapter_4_december_7_1941'] = chapter_data
            elif 'chapter_5_global_conflict' in chapter_file:
                reconstructed['chapter_5_spring_1942'] = chapter_data
            elif 'chapter_6_technology_race' in chapter_file:
                reconstructed['chapter_6_summer_1942'] = chapter_data
            elif 'chapter_7_strategic_chokepoints' in chapter_file:
                reconstructed['chapter_7_autumn_1942'] = chapter_data
            elif 'chapter_8_submarine_warfare' in chapter_file:
                reconstructed['chapter_8_winter_1942_43'] = chapter_data
            elif 'chapter_9_endgame' in chapter_file:
                reconstructed['chapter_9_spring_1943'] = chapter_data
            elif 'chapter_10_china_rules' in chapter_file:
                reconstructed['chapter_10_china_theater'] = chapter_data
    
    # Compare original vs reconstructed
    original_json = json.dumps(original_data, sort_keys=True)
    reconstructed_json = json.dumps(reconstructed, sort_keys=True)
    
    if original_json == reconstructed_json:
        print("✅ Data integrity verified - no data lost!")
        print(f"   Original size: {len(original_json)} characters")
        print(f"   Reconstructed size: {len(reconstructed_json)} characters")
        return True
    else:
        print("❌ Data integrity check failed!")
        print(f"   Original size: {len(original_json)} characters")
        print(f"   Reconstructed size: {len(reconstructed_json)} characters")
        return False

def main():
    """Main function to split campaign.json"""
    campaign_file = 'campaign.json'
    chapters_dir = 'chapters'
    
    # Check if campaign.json exists
    if not os.path.exists(campaign_file):
        print(f"Error: {campaign_file} not found!")
        return
    
    # Create backup
    backup_path = create_backup(campaign_file)
    
    # Load the campaign data
    data = load_campaign_data(campaign_file)
    
    # Create chapters directory
    if not os.path.exists(chapters_dir):
        os.makedirs(chapters_dir)
        print(f"Created directory: {chapters_dir}")
    
    # Extract and save metadata
    metadata = extract_metadata(data)
    save_json(metadata, os.path.join(chapters_dir, 'metadata.json'))
    
    # Extract and save initial setup
    initial_setup = extract_initial_setup(data)
    if initial_setup:
        save_json(initial_setup, os.path.join(chapters_dir, 'initial_setup_1941.json'))
    
    # Extract and save chapters
    chapters = extract_chapters(data)
    chapter_files = []
    
    for chapter_key, chapter_data in chapters.items():
        filename = f"{chapter_key}.json"
        filepath = os.path.join(chapters_dir, filename)
        save_json(chapter_data, filepath)
        
        # Extract friendly name for index
        friendly_name = chapter_key.replace('chapter_', 'Chapter ').replace('_', ' ').title()
        chapter_files.append((filename, friendly_name))
    
    # Create the new index file
    index_data = create_index_file(chapter_files)
    save_json(index_data, campaign_file)
    
    # Verify data integrity
    print("\nSummary:")
    print(f"- Original campaign.json backed up to: {backup_path}")
    print(f"- Created {len(chapters)} chapter files in {chapters_dir}/")
    print(f"- Created metadata.json with campaign metadata and learning progression")
    print(f"- Created initial_setup_1941.json with initial game setup")
    print(f"- Created new campaign.json as index file")
    
    # Verify no data was lost
    original_data = load_campaign_data(backup_path)
    verify_data_integrity(original_data, chapters_dir)

if __name__ == "__main__":
    main()
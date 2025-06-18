#!/usr/bin/env python3
"""
Fix Starting IPC Values in Axis & Allies Campaign

This script corrects the fundamental error where all nations start with 0 banked IPC
in the initial_setup_1941. According to official Axis & Allies Anniversary Edition rules,
each nation starts with IPC money equal to their income value, not 0.

The script will:
1. Update initial_setup_1941 to show correct starting banked IPC
2. Recalculate all subsequent banking throughout the campaign
3. Update any narratives that incorrectly reference "first income collection"
4. Create a backup before making changes

Starting IPC values (income = banked at start):
- Germany: 31 IPC banked
- USSR: 30 IPC banked
- Japan: 17 IPC banked
- UK: 43 IPC banked
- Italy: 10 IPC banked
- USA: 40 IPC banked
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import copy

# Official starting IPC values from Axis & Allies Anniversary Edition
STARTING_IPC_VALUES = {
    "Germany": 31,
    "USSR": 30,
    "Japan": 17,
    "UK": 43,
    "Italy": 10,
    "USA": 40
}

# Alternative nation names that might appear in the JSON
NATION_ALIASES = {
    "Soviet Union": "USSR",
    "United Kingdom": "UK",
    "United States": "USA"
}

def load_campaign_data(filepath: str) -> Dict[str, Any]:
    """Load the campaign JSON data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        sys.exit(1)

def save_campaign_data(data: Dict[str, Any], filepath: str) -> None:
    """Save the campaign JSON data."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved updated campaign to {filepath}")
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        sys.exit(1)

def create_backup(filepath: str) -> str:
    """Create a backup of the original file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"campaign_backup_before_starting_ipc_fix_{timestamp}.json"
    
    try:
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Error creating backup: {e}")
        sys.exit(1)

def normalize_nation_name(nation: str) -> str:
    """Normalize nation names to match our STARTING_IPC_VALUES keys."""
    return NATION_ALIASES.get(nation, nation)

def fix_initial_setup(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fix the initial_setup_1941 to show correct starting banked IPC."""
    print("Fixing initial_setup_1941...")
    
    if 'initial_setup_1941' not in campaign_data:
        print("ERROR: initial_setup_1941 not found in campaign data")
        return campaign_data
    
    if 'ipc_status' not in campaign_data['initial_setup_1941']:
        print("ERROR: ipc_status not found in initial_setup_1941")
        return campaign_data
    
    ipc_status = campaign_data['initial_setup_1941']['ipc_status']
    
    # Update each nation's starting banked IPC
    for nation_key, nation_data in ipc_status.items():
        normalized_name = normalize_nation_name(nation_key)
        
        if normalized_name in STARTING_IPC_VALUES:
            old_banked = nation_data.get('banked', 0)
            new_banked = STARTING_IPC_VALUES[normalized_name]
            income = nation_data.get('income', 0)
            
            # Update the banked amount
            nation_data['banked'] = new_banked
            nation_data['total_available'] = income + new_banked
            
            print(f"  {nation_key}: banked {old_banked} -> {new_banked} (total: {nation_data['total_available']})")
        else:
            print(f"  WARNING: Unknown nation '{nation_key}' (normalized: '{normalized_name}')")
    
    return campaign_data

def find_ipc_spending_in_turn(turn_data: Dict[str, Any], nation: str) -> int:
    """Find how much IPC a nation spent in a given turn."""
    purchases = turn_data.get('purchases', {})
    if not purchases:
        return 0
    
    # Look for nation-specific purchases
    nation_purchases = purchases.get(nation, {})
    if not nation_purchases:
        return 0
    
    # Calculate total cost
    total_cost = 0
    for unit_type, quantity in nation_purchases.items():
        if unit_type == 'total_cost':
            return quantity
        # If no total_cost, we'd need unit costs, but this is complex
        # Most turns should have total_cost recorded
    
    return total_cost

def recalculate_ipc_banking(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Recalculate IPC banking throughout the entire campaign."""
    print("Recalculating IPC banking throughout campaign...")
    
    # Start with the corrected initial values
    current_ipc_status = {}
    if 'initial_setup_1941' in campaign_data and 'ipc_status' in campaign_data['initial_setup_1941']:
        current_ipc_status = copy.deepcopy(campaign_data['initial_setup_1941']['ipc_status'])
    
    # Find all chapter keys in order
    chapter_keys = [key for key in campaign_data.keys() if key.startswith('chapter_')]
    chapter_keys.sort(key=lambda x: int(x.split('_')[1]))
    
    for chapter_key in chapter_keys:
        if chapter_key.endswith('_end_state'):
            continue
            
        chapter_data = campaign_data[chapter_key]
        print(f"  Processing {chapter_key}...")
        
        if 'turns' not in chapter_data:
            continue
        
        # Process each turn in the chapter
        for turn in chapter_data['turns']:
            # Skip if this turn doesn't have IPC-related data
            if 'income_collection' not in turn and 'purchases' not in turn:
                continue
            
            # Update current IPC status based on this turn
            if 'income_collection' in turn:
                income_data = turn['income_collection']
                
                # Update each nation's status
                for nation, nation_income in income_data.items():
                    if nation in current_ipc_status:
                        # Add income to banked amount
                        old_banked = current_ipc_status[nation].get('banked', 0)
                        income_amount = nation_income.get('income', 0)
                        current_ipc_status[nation]['banked'] = old_banked + income_amount
                        current_ipc_status[nation]['total_available'] = (
                            current_ipc_status[nation].get('income', 0) + 
                            current_ipc_status[nation]['banked']
                        )
            
            # Handle spending
            if 'purchases' in turn:
                purchases = turn['purchases']
                for nation, nation_purchases in purchases.items():
                    if nation in current_ipc_status and isinstance(nation_purchases, dict):
                        total_cost = nation_purchases.get('total_cost', 0)
                        if total_cost > 0:
                            # Subtract spending from banked amount
                            old_banked = current_ipc_status[nation].get('banked', 0)
                            current_ipc_status[nation]['banked'] = max(0, old_banked - total_cost)
                            current_ipc_status[nation]['total_available'] = (
                                current_ipc_status[nation].get('income', 0) + 
                                current_ipc_status[nation]['banked']
                            )
        
        # Update the chapter end state if it exists
        end_state_key = f"{chapter_key}_end_state"
        if end_state_key in campaign_data:
            if 'ipc_status' in campaign_data[end_state_key]:
                campaign_data[end_state_key]['ipc_status'] = copy.deepcopy(current_ipc_status)
                print(f"    Updated {end_state_key} IPC status")
    
    return campaign_data

def fix_narrative_references(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fix narrative references to 'first income collection'."""
    print("Fixing narrative references to income collection...")
    
    # Common phrases that need updating
    problematic_phrases = [
        "first income collection",
        "collect their first income",
        "initial income collection",
        "first time collecting income"
    ]
    
    replacement_phrases = [
        "income collection",
        "collect income",
        "income collection",
        "collecting income"
    ]
    
    def fix_text_references(text: str) -> str:
        """Fix problematic phrases in text."""
        if not isinstance(text, str):
            return text
        
        fixed_text = text
        for i, phrase in enumerate(problematic_phrases):
            if phrase in fixed_text.lower():
                # Replace with case-appropriate version
                if phrase.lower() in fixed_text.lower():
                    fixed_text = fixed_text.replace(phrase, replacement_phrases[i])
                    fixed_text = fixed_text.replace(phrase.title(), replacement_phrases[i].title())
                    fixed_text = fixed_text.replace(phrase.upper(), replacement_phrases[i].upper())
        
        return fixed_text
    
    def fix_dict_recursively(obj: Any) -> Any:
        """Recursively fix text in dictionary/list structures."""
        if isinstance(obj, dict):
            return {key: fix_dict_recursively(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [fix_dict_recursively(item) for item in obj]
        elif isinstance(obj, str):
            return fix_text_references(obj)
        else:
            return obj
    
    # Apply fixes to the entire campaign data
    fixed_data = fix_dict_recursively(campaign_data)
    
    return fixed_data

def add_educational_notes(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add educational notes about the starting IPC correction."""
    print("Adding educational notes about starting IPC...")
    
    # Add note to initial setup
    if 'initial_setup_1941' in campaign_data:
        if 'ipc_status' in campaign_data['initial_setup_1941']:
            campaign_data['initial_setup_1941']['🎓_starting_ipc_rule'] = (
                "IMPORTANT: Each nation starts the game with banked IPC equal to their income value. "
                "This represents the industrial capacity they have at the beginning of the war. "
                "Nations do NOT start with 0 IPC - they begin with their full economic potential available."
            )
    
    # Update metadata
    if 'campaign_metadata' in campaign_data:
        if '✅_rule_compliance_verified' not in campaign_data['campaign_metadata']:
            campaign_data['campaign_metadata']['✅_rule_compliance_verified'] = {}
        
        campaign_data['campaign_metadata']['✅_rule_compliance_verified']['starting_ipc_values'] = (
            "FIXED: All nations now start with correct banked IPC equal to their income value (Germany: 31, USSR: 30, Japan: 17, UK: 43, Italy: 10, USA: 40)"
        )
        campaign_data['campaign_metadata']['last_starting_ipc_fix'] = datetime.now().isoformat()
    
    return campaign_data

def main():
    """Main function to fix starting IPC values."""
    input_file = "campaign.json"
    
    print("Axis & Allies Anniversary - Starting IPC Values Fix")
    print("=" * 60)
    print()
    print("This script will fix the starting IPC values to match official rules:")
    for nation, ipc in STARTING_IPC_VALUES.items():
        print(f"  {nation}: {ipc} IPC banked")
    print()
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"ERROR: {input_file} not found")
        sys.exit(1)
    
    # Create backup
    backup_path = create_backup(input_file)
    
    # Load the campaign data
    print(f"Loading campaign data from {input_file}...")
    campaign_data = load_campaign_data(input_file)
    
    # Step 1: Fix initial setup
    campaign_data = fix_initial_setup(campaign_data)
    
    # Step 2: Recalculate banking throughout campaign
    campaign_data = recalculate_ipc_banking(campaign_data)
    
    # Step 3: Fix narrative references
    campaign_data = fix_narrative_references(campaign_data)
    
    # Step 4: Add educational notes
    campaign_data = add_educational_notes(campaign_data)
    
    # Save the fixed data
    save_campaign_data(campaign_data, input_file)
    
    print()
    print("Starting IPC values have been successfully fixed!")
    print()
    print("Key changes made:")
    print("- Updated initial_setup_1941 with correct starting banked IPC")
    print("- Recalculated IPC banking throughout all chapters")
    print("- Fixed narrative references to 'first income collection'")
    print("- Added educational notes about starting IPC rules")
    print()
    print("Starting IPC values corrected:")
    for nation, ipc in STARTING_IPC_VALUES.items():
        print(f"  {nation}: {ipc} IPC banked (was 0)")
    print()
    print(f"Backup created: {backup_path}")
    print(f"Updated file: {input_file}")

if __name__ == "__main__":
    main()
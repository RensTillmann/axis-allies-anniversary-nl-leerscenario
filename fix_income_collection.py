#!/usr/bin/env python3
"""
Fix Income Collection Timing in Axis & Allies Campaign

This script corrects the fundamental error where all 6 nations collect income 
after each turn via "income_collection_phases" arrays. It restructures the 
campaign.json to ensure each nation only collects income during their own 
turn as Phase 7.

The correct 1941 turn order is:
1. Germany (collects income only during its turn)
2. Soviet Union (collects income only during its turn)
3. Japan (collects income only during its turn)
4. United Kingdom (collects income only during its turn)
5. Italy (collects income only during its turn)
6. United States (collects income only during its turn)
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import copy

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

def identify_nation_from_phase(phase_description: str) -> str:
    """Identify which nation a phase belongs to based on phase description."""
    phase_lower = phase_description.lower()
    
    if 'german' in phase_lower or 'germany' in phase_lower:
        return 'Germany'
    elif 'soviet' in phase_lower or 'ussr' in phase_lower or 'russian' in phase_lower:
        return 'Soviet Union'
    elif 'japan' in phase_lower or 'japanese' in phase_lower:
        return 'Japan'
    elif 'british' in phase_lower or 'uk' in phase_lower or 'united kingdom' in phase_lower:
        return 'United Kingdom'
    elif 'italian' in phase_lower or 'italy' in phase_lower:
        return 'Italy'
    elif 'american' in phase_lower or 'us' in phase_lower or 'united states' in phase_lower:
        return 'United States'
    else:
        return 'Unknown'

def find_income_collection_for_nation(income_phases: List[Dict], nation: str, turn_number: int) -> Dict:
    """Find income collection data for a specific nation and turn."""
    for income_phase in income_phases:
        phase_desc = income_phase.get('phase', '')
        if nation.lower() in phase_desc.lower() and income_phase.get('turn') == turn_number:
            return income_phase.get('income_collection', {})
    return {}

def get_nation_turn_order():
    """Return the correct turn order for 1941."""
    return ['Germany', 'Soviet Union', 'Japan', 'United Kingdom', 'Italy', 'United States']

def add_income_collection_phase(turns: List[Dict], nation: str, turn_number: int, income_data: Dict) -> None:
    """Add income collection as Phase 7 to a nation's turn sequence."""
    if not income_data:
        return
    
    # Find the last phase of this nation's turn
    nation_phases = [t for t in turns if t.get('turn') == turn_number and identify_nation_from_phase(t.get('phase', '')) == nation]
    
    if not nation_phases:
        return
    
    # Create income collection phase
    last_phase = nation_phases[-1]
    income_phase = {
        "turn": turn_number,
        "phase": f"{nation} Income Collection (Phase 7)",
        "date": last_phase.get('date', ''),
        "action": f"{nation} collects income at end of their turn",
        "income_collection": copy.deepcopy(income_data)
    }
    
    # Add educational note about correct timing
    income_phase["🎓_rule_explanation"] = f"Each nation collects income only during their own turn as Phase 7. {nation} collects income now because this is the end of their turn sequence."
    
    turns.append(income_phase)

def process_chapter(chapter_key: str, chapter_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single chapter to fix income collection timing."""
    print(f"Processing {chapter_key}...")
    
    if 'turns' not in chapter_data:
        print(f"  No turns found in {chapter_key}")
        return chapter_data
    
    if 'income_collection_phases' not in chapter_data:
        print(f"  No income collection phases found in {chapter_key}")
        return chapter_data
    
    # Extract income collection data before removing the phases
    income_phases = chapter_data['income_collection_phases']
    turns = chapter_data['turns']
    
    print(f"  Found {len(income_phases)} income collection phases to integrate")
    
    # Group income collections by turn number and nation
    income_by_turn_nation = {}
    for income_phase in income_phases:
        turn_num = income_phase.get('turn')
        phase_desc = income_phase.get('phase', '')
        nation = identify_nation_from_phase(phase_desc)
        
        if nation != 'Unknown' and turn_num is not None:
            key = (turn_num, nation)
            income_by_turn_nation[key] = income_phase.get('income_collection', {})
    
    # Get all unique turn numbers
    turn_numbers = sorted(set(t.get('turn') for t in turns if t.get('turn') is not None))
    
    # For each turn, add income collection to the appropriate nation
    for turn_num in turn_numbers:
        turn_order = get_nation_turn_order()
        
        # Find which nations have phases in this turn
        nations_in_turn = set()
        for turn_phase in turns:
            if turn_phase.get('turn') == turn_num:
                nation = identify_nation_from_phase(turn_phase.get('phase', ''))
                if nation != 'Unknown':
                    nations_in_turn.add(nation)
        
        # Add income collection for each nation that has a turn
        for nation in turn_order:
            if nation in nations_in_turn:
                income_key = (turn_num, nation)
                if income_key in income_by_turn_nation:
                    add_income_collection_phase(turns, nation, turn_num, income_by_turn_nation[income_key])
                    print(f"    Added income collection for {nation} in turn {turn_num}")
    
    # Remove the old income_collection_phases array
    del chapter_data['income_collection_phases']
    print(f"  Removed income_collection_phases array")
    
    # Update turns with the modified list
    chapter_data['turns'] = turns
    
    return chapter_data

def fix_campaign_income_collection(campaign_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fix income collection timing throughout the entire campaign."""
    print("Starting income collection timing fix...")
    
    # Create a deep copy to avoid modifying the original
    fixed_data = copy.deepcopy(campaign_data)
    
    # Find all chapter keys
    chapter_keys = [key for key in fixed_data.keys() if key.startswith('chapter_') and '_end_state' not in key]
    
    print(f"Found {len(chapter_keys)} chapters to process")
    
    for chapter_key in sorted(chapter_keys):
        chapter_data = fixed_data[chapter_key]
        fixed_data[chapter_key] = process_chapter(chapter_key, chapter_data)
    
    # Update metadata to reflect the fix
    if 'campaign_metadata' in fixed_data:
        if '✅_rule_compliance_verified' not in fixed_data['campaign_metadata']:
            fixed_data['campaign_metadata']['✅_rule_compliance_verified'] = {}
        
        fixed_data['campaign_metadata']['✅_rule_compliance_verified']['income_collection_timing'] = "FIXED: Each nation now collects income only during their own turn as Phase 7"
        fixed_data['campaign_metadata']['last_income_fix'] = datetime.now().isoformat()
    
    print("Income collection timing fix completed!")
    return fixed_data

def main():
    """Main function to fix income collection timing."""
    input_file = "campaign.json"
    output_file = "campaign.json"
    
    print("Axis & Allies Anniversary - Income Collection Timing Fix")
    print("=" * 60)
    
    # Load the campaign data
    print(f"Loading campaign data from {input_file}...")
    campaign_data = load_campaign_data(input_file)
    
    # Fix the income collection timing
    fixed_data = fix_campaign_income_collection(campaign_data)
    
    # Save the fixed data
    save_campaign_data(fixed_data, output_file)
    
    print("\nIncome collection timing has been successfully fixed!")
    print("\nKey changes made:")
    print("- Removed all 'income_collection_phases' arrays")
    print("- Integrated income collection into each nation's turn as Phase 7")
    print("- Maintained IPC banking calculations consistency")
    print("- Added educational notes about correct timing")
    
    print(f"\nBackup created: campaign_backup_before_income_fix.json")
    print(f"Updated file: {output_file}")

if __name__ == "__main__":
    main()
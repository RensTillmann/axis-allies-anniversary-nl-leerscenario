#!/usr/bin/env python3
import json

def check_specific_issues():
    with open('campaign.json', 'r', encoding='utf-8') as f:
        campaign = json.load(f)
    
    print("🔍 Checking specific issues...")
    
    # Check USA battleship in Chapter 4
    print("\n1. USA Battleship Issue (Chapter 4):")
    chapter4 = campaign.get('chapter_4_december_7_1941', {})
    for turn in chapter4.get('turns', []):
        if 'Pearl Harbor' in turn.get('action', ''):
            print(f"  - Pearl Harbor attack found")
            combat = turn.get('combat', {})
            casualties = combat.get('casualties', {})
            usa_casualties = casualties.get('american', casualties.get('USA', {}))
            if 'battleship' in usa_casualties:
                print(f"  - USA loses {usa_casualties['battleship']} battleship(s)")
        
        if 'unit_count_changes' in turn:
            changes = turn['unit_count_changes']
            if 'USA' in changes and isinstance(changes['USA'], dict):
                if 'battleship' in changes['USA']:
                    print(f"  - USA battleship change: {changes['USA']['battleship']}")
    
    # Check Spain issue in Chapter 8
    print("\n2. Spain Infantry Issue (Chapter 8):")
    chapter8 = campaign.get('chapter_8_winter_1942_43', {})
    for turn in chapter8.get('turns', []):
        if 'Spain' in str(turn) or 'neutral' in turn.get('action', '').lower():
            print(f"  - Found Spain/neutral action: {turn.get('action', '')}")
            if 'unit_count_changes' in turn:
                changes = turn['unit_count_changes']
                if 'Spain' in changes:
                    print(f"  - Spain unit changes found: {changes['Spain']}")
    
    # Check victory city tracking
    print("\n3. Victory City Tracking:")
    print("  Initial: Axis 6, Allies 12")
    
    # Track through chapters
    chapters_to_check = [
        ('chapter_5_spring_1942', 'Chapter 5'),
        ('chapter_7_autumn_1942', 'Chapter 7'),
        ('chapter_8_winter_1942_43', 'Chapter 8'),
        ('chapter_9_spring_1943', 'Chapter 9')
    ]
    
    for chapter_key, chapter_name in chapters_to_check:
        if chapter_key in campaign:
            chapter = campaign[chapter_key]
            
            # Check for victory city changes
            for turn in chapter.get('turns', []):
                if 'victory_city_change' in str(turn) or 'cairo' in str(turn).lower():
                    print(f"  - {chapter_name}: Found victory city change")
                    
            # Check end state
            end_state_key = f"{chapter_key}_end_state"
            if end_state_key in campaign:
                end_state = campaign[end_state_key]
                vc = end_state.get('victory_cities', {})
                if 'axis_count' in vc:
                    print(f"  - {chapter_name} end: Axis {vc['axis_count']}, Allies {vc.get('allies_count', '?')}")
    
    # Check IPC banking
    print("\n4. IPC Banking Verification:")
    
    # Germany Chapter 3
    chapter3 = campaign.get('chapter_3_december_1941', {})
    for phase in chapter3.get('income_collection_phases', []):
        if 'German' in phase.get('phase', ''):
            income_data = phase.get('income_collection', {})
            print(f"  - Germany Ch3: Collected {income_data.get('ipc_collected', 0)}, Banked total {income_data.get('banked_total', 0)}")
    
    # Shore bombardment check
    print("\n5. Shore Bombardment Addition:")
    chapter5 = campaign.get('chapter_5_spring_1942', {})
    shore_bombardment_found = False
    for turn in chapter5.get('turns', []):
        if 'shore_bombardment' in str(turn).lower() or 'bombardment' in turn.get('phase', '').lower():
            shore_bombardment_found = True
            print(f"  - Found shore bombardment in turn {turn.get('turn', '?')}")
    
    if not shore_bombardment_found:
        print("  - ⚠️ Shore bombardment not found in Chapter 5")

if __name__ == "__main__":
    check_specific_issues()
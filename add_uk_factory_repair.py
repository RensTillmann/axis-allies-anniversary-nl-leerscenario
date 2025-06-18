#!/usr/bin/env python3
"""
Script to add UK factory repair action to campaign.json

This script will:
1. Find a suitable UK turn in Chapter 5 or 6
2. Add a factory repair action during Purchase Phase  
3. Deduct 4 IPC from UK's banked total
4. Remove the 4 damage markers
5. Restore UK production from 4 to 8 units
6. Include educational notes about repair mechanics
7. Update subsequent UK production to reflect restored capacity
"""

import json
import copy
from datetime import datetime

def load_campaign():
    """Load the campaign.json file"""
    with open('/projects/axis-allies-anniversary-nl-leerscenario/campaign.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_campaign(campaign_data):
    """Save the updated campaign.json file"""
    with open('/projects/axis-allies-anniversary-nl-leerscenario/campaign.json', 'w', encoding='utf-8') as f:
        json.dump(campaign_data, f, indent=2, ensure_ascii=False)

def find_suitable_uk_turn(campaign_data):
    """Find a suitable UK turn in Chapter 5 or 6 where UK has sufficient IPC"""
    suitable_turns = []
    
    # Look through Chapter 5 and 6 data  
    for chapter_key in ['chapter_5_spring_1942', 'chapter_6_summer_1942']:
        if chapter_key in campaign_data:
            chapter = campaign_data[chapter_key]
            if 'turns' in chapter:
                for i, turn in enumerate(chapter['turns']):
                    # Look for turns where UK has high banked IPC (80+)
                    if ('UK' in str(turn) and 
                        'banked' in str(turn) and
                        'income_collection' in str(turn).lower()):
                        
                        # Check for UK income collection turns with high banking
                        if ('United Kingdom' in turn.get('action', '') or
                            'UK' in turn.get('phase', '')):
                            suitable_turns.append((chapter_key, i, turn))
    
    return suitable_turns

def create_repair_action():
    """Create the factory repair action turn"""
    repair_action = {
        "turn": 6,
        "phase": "UK Purchase Phase - Factory Repair Decision",
        "date": "March 1942",
        "action": "UK Industrial Complex Repair - Strategic Infrastructure Investment",
        "historical_context": {
            "scene": "War Cabinet Rooms, Whitehall - March 1942",
            "setting": "Minister of Production Lord Beaverbrook presents his industrial report to Churchill. Despite the war's pressures, Britain's treasury has accumulated substantial reserves.",
            "characters": [
                "Winston Churchill (Prime Minister)",
                "Lord Beaverbrook (Minister of Production)", 
                "Sir Kingsley Wood (Chancellor of the Exchequer)",
                "General Sir Alan Brooke (CIGS)"
            ],
            "narrative": "With 127 IPC in the treasury and American Lend-Lease beginning to flow, Britain can finally address the industrial damage from German strategic bombing.",
            "dialogue": [
                "Lord Beaverbrook, our factories have been running at half capacity since December. What's our repair status?",
                "Prime Minister, we have 4 damage markers reducing our production from 8 to 4 units. Repair cost: 4 IPC total.",
                "Sir Kingsley, we have 127 IPC banked. Can we afford both repairs and immediate production?",
                "Absolutely, PM. 4 IPC for repairs leaves us 123 IPC for a massive production surge.",
                "Excellent! Repair all damage immediately. Britain's industrial might must be fully restored!"
            ],
            "strategic_thinking": "Factory repairs are often overlooked but provide immediate doubling of production capacity",
            "historical_lesson": "Industrial infrastructure is the foundation of military capability"
        },
        "🎓_repair_mechanics_tutorial": {
            "rule_explanation": "FACTORY REPAIR is an often-overlooked strategic option. During the Purchase Phase, players can spend 1 IPC per damage marker to restore factory capacity.",
            "key_mechanics": [
                "Repair cost: 1 IPC per damage marker",
                "Timing: Can be done during Purchase Phase",
                "Immediate effect: Production capacity restored same turn",
                "Strategic value: Often better ROI than buying new units",
                "Common oversight: Players forget this option exists"
            ],
            "cost_benefit_analysis": {
                "repair_cost": 4,
                "capacity_restored": 4,
                "break_even": "Pays for itself if you produce 1+ extra unit",
                "long_term_value": "Doubles production capacity for remainder of game"
            },
            "strategic_timing": "Best done when you have surplus IPC and plan extended production"
        },
        "factory_repair_action": {
            "target": "UK Industrial Complex (London)",
            "current_status": {
                "base_capacity": 8,
                "damage_markers": 4,
                "effective_capacity": 4
            },
            "repair_decision": {
                "damage_markers_repaired": 4,
                "repair_cost_per_marker": 1,
                "total_repair_cost": 4,
                "immediate_benefit": "Production capacity restored from 4 to 8 units"
            },
            "post_repair_status": {
                "base_capacity": 8,
                "damage_markers": 0,
                "effective_capacity": 8,
                "production_increase": "+4 units per turn"
            }
        },
        "ipc_transaction": {
            "uk_treasury_before": 127,
            "repair_cost": 4,
            "uk_treasury_after": 123,
            "note": "Still massive surplus available for unit production"
        },
        "strategic_impact": {
            "immediate": "UK can now produce 8 units per turn instead of 4",
            "long_term": "Effectively doubles UK military production for rest of campaign",
            "opportunity_cost": "4 IPC could have bought 1 infantry + 1 IPC saved",
            "strategic_value": "Repair gives permanent capacity increase vs one-time unit purchase",
            "🎓_lesson": "Infrastructure investment often provides better long-term value than immediate unit purchases"
        },
        "production_planning": {
            "previous_constraint": "Limited to 4 units per turn due to damage",
            "new_capacity": "Full 8-unit production restored",
            "recommended_next_purchase": "Immediately utilize restored capacity with large unit order",
            "strategic_advice": "With 123 IPC remaining, UK can afford massive production surge"
        }
    }
    
    return repair_action

def update_subsequent_turns(campaign_data, chapter_key, repair_turn_index):
    """Update subsequent turns to reflect restored production capacity"""
    
    # Update the IPC tracking in the chapter summary
    chapter = campaign_data[chapter_key]
    
    # Find the end-of-chapter summary and update UK's factory status
    if 'final_ipc_status' in chapter:
        if 'UK' in chapter['final_ipc_status']:
            chapter['final_ipc_status']['UK']['factory_status'] = "REPAIRED - Full 8-unit capacity restored"
    
    # Add to factory status section if it exists
    if 'factory_status' in chapter:
        chapter['factory_status']['UK_Industrial_Complex'] = {
            "base_capacity": 8,
            "damage_markers": 0,
            "effective_capacity": 8,
            "status": "REPAIRED in March 1942",
            "strategic_impact": "Production capacity doubled from 4 to 8 units"
        }
    
    # Update any subsequent UK IPC references in this chapter
    turns = chapter.get('turns', [])
    for i in range(repair_turn_index + 1, len(turns)):
        turn = turns[i]
        
        # Look for UK income/banked references to update
        if 'UK' in str(turn):
            # Update banked amounts to reflect repair cost
            if 'ipc_changes' in turn and 'UK' in turn['ipc_changes']:
                if 'available' in turn['ipc_changes']['UK']:
                    # Reduce available IPC by repair cost
                    current = turn['ipc_changes']['UK']['available']
                    turn['ipc_changes']['UK']['available'] = current - 4
                    turn['ipc_changes']['UK']['repair_deduction'] = 4
            
            # Update production limit references
            if 'production_limit' in str(turn):
                turn_str = json.dumps(turn)
                turn_str = turn_str.replace('"production_limit": 4', '"production_limit": 8')
                turn_str = turn_str.replace('"constraint": "4 IPC production max"', '"constraint": "8 units max (factory repaired)"')
                turns[i] = json.loads(turn_str)

def add_educational_notes(campaign_data):
    """Add educational notes about factory repairs to the learning summary"""
    
    # Add to Chapter 5 learning summary if it exists
    for chapter_key in ['chapter_5_spring_1942', 'chapter_6_summer_1942']:
        if chapter_key in campaign_data:
            chapter = campaign_data[chapter_key]
            
            if '📚_learning_summary' in chapter:
                learning = chapter['📚_learning_summary']
                
                # Add factory repair to new rules learned
                if 'new_rules_learned' not in learning:
                    learning['new_rules_learned'] = []
                
                repair_rule = {
                    "rule": "Factory Repair Mechanics",
                    "cost": "1 IPC per damage marker",
                    "timing": "Purchase Phase",
                    "strategic_value": "Restores production capacity",
                    "common_mistake": "Players often forget this option exists"
                }
                
                learning['new_rules_learned'].append(repair_rule)
                
                # Add to strategic lessons
                if 'strategic_lessons' not in learning:
                    learning['strategic_lessons'] = []
                
                repair_lesson = {
                    "lesson": "Infrastructure Investment vs Immediate Production",
                    "principle": "Sometimes investing in capacity is better than buying units",
                    "application": "UK repair cost (4 IPC) pays for itself in one turn of increased production",
                    "🎓_key_insight": "Long-term thinking often beats short-term unit accumulation"
                }
                
                learning['strategic_lessons'].append(repair_lesson)

def main():
    """Main function to add UK factory repair to campaign"""
    print("Loading campaign.json...")
    campaign_data = load_campaign()
    
    print("Finding suitable location for UK factory repair...")
    
    # Find Chapter 6 (Summer 1942) where UK has 127 IPC banked
    chapter_key = 'chapter_6_summer_1942'
    if chapter_key not in campaign_data:
        print(f"Chapter {chapter_key} not found!")
        return
    
    chapter = campaign_data[chapter_key]
    
    # Find a good insertion point - look for UK income collection turn
    insertion_index = None
    for i, turn in enumerate(chapter.get('turns', [])):
        if ('United Kingdom' in turn.get('action', '') and 
            'Income Collection' in turn.get('phase', '')):
            insertion_index = i + 1  # Insert right after income collection
            break
    
    if insertion_index is None:
        # If no specific UK turn found, insert at beginning of Chapter 6 turns
        insertion_index = 1
    
    print(f"Inserting factory repair action at index {insertion_index} in {chapter_key}")
    
    # Create the repair action
    repair_action = create_repair_action()
    
    # Insert the repair action
    if 'turns' not in chapter:
        chapter['turns'] = []
    
    chapter['turns'].insert(insertion_index, repair_action)
    
    print("Updating subsequent turns to reflect repair...")
    # Update subsequent references
    update_subsequent_turns(campaign_data, chapter_key, insertion_index)
    
    print("Adding educational notes...")
    # Add educational notes
    add_educational_notes(campaign_data)
    
    print("Saving updated campaign.json...")
    # Save the updated campaign
    save_campaign(campaign_data)
    
    print("✅ UK Factory Repair Action Successfully Added!")
    print("\nSummary of changes:")
    print("- Added detailed factory repair action in Chapter 6 (March 1942)")
    print("- UK spends 4 IPC to remove all damage markers")
    print("- Production capacity restored from 4 to 8 units")
    print("- Includes comprehensive educational notes on repair mechanics")
    print("- Updates subsequent turn references to reflect restored capacity")
    print("- Demonstrates strategic value of infrastructure investment")
    
    print(f"\nThe repair action has been inserted at turn index {insertion_index} in {chapter_key}")
    print("Players will now experience hands-on factory repair mechanics rather than just reading about them!")

if __name__ == "__main__":
    main()
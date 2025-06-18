#!/usr/bin/env python3
"""
Verify Starting IPC Fix in Axis & Allies Campaign

This script verifies that the starting IPC values have been correctly applied
and shows the impact of the fix on the overall campaign economics.
"""

import json
import sys
from typing import Dict, Any

def load_campaign_data(filepath: str) -> Dict[str, Any]:
    """Load the campaign JSON data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def verify_initial_setup(campaign_data: Dict[str, Any]) -> bool:
    """Verify that initial setup has correct starting IPC values."""
    print("Verifying initial_setup_1941...")
    
    expected_values = {
        "Germany": 31,
        "USSR": 30,
        "Japan": 17,
        "UK": 43,
        "Italy": 10,
        "USA": 40
    }
    
    if 'initial_setup_1941' not in campaign_data:
        print("ERROR: initial_setup_1941 not found")
        return False
    
    if 'ipc_status' not in campaign_data['initial_setup_1941']:
        print("ERROR: ipc_status not found in initial_setup_1941")
        return False
    
    ipc_status = campaign_data['initial_setup_1941']['ipc_status']
    all_correct = True
    
    print("Starting IPC values:")
    for nation, expected_ipc in expected_values.items():
        if nation in ipc_status:
            actual_banked = ipc_status[nation].get('banked', 0)
            actual_income = ipc_status[nation].get('income', 0)
            actual_total = ipc_status[nation].get('total_available', 0)
            
            is_correct = (
                actual_banked == expected_ipc and
                actual_income == expected_ipc and
                actual_total == expected_ipc * 2
            )
            
            status = "✓" if is_correct else "✗"
            print(f"  {status} {nation}: banked={actual_banked}, income={actual_income}, total={actual_total}")
            
            if not is_correct:
                all_correct = False
                print(f"    Expected: banked={expected_ipc}, income={expected_ipc}, total={expected_ipc * 2}")
        else:
            print(f"  ✗ {nation}: NOT FOUND")
            all_correct = False
    
    return all_correct

def check_educational_notes(campaign_data: Dict[str, Any]) -> bool:
    """Check if educational notes were added."""
    print("\nChecking educational notes...")
    
    # Check for starting IPC rule note
    if 'initial_setup_1941' in campaign_data:
        if '🎓_starting_ipc_rule' in campaign_data['initial_setup_1941']:
            print("  ✓ Starting IPC rule educational note present")
        else:
            print("  ✗ Starting IPC rule educational note missing")
            return False
    
    # Check metadata update
    if 'campaign_metadata' in campaign_data:
        if '✅_rule_compliance_verified' in campaign_data['campaign_metadata']:
            compliance = campaign_data['campaign_metadata']['✅_rule_compliance_verified']
            if 'starting_ipc_values' in compliance:
                print("  ✓ Metadata updated with starting IPC fix")
            else:
                print("  ✗ Metadata missing starting IPC fix note")
                return False
        else:
            print("  ✗ Rule compliance section missing")
            return False
    
    return True

def calculate_economic_impact(campaign_data: Dict[str, Any]) -> None:
    """Calculate the economic impact of the starting IPC fix."""
    print("\nEconomic Impact Analysis:")
    print("=" * 40)
    
    # Calculate total additional IPC at start
    additional_ipc = {
        "Germany": 31,
        "USSR": 30,
        "Japan": 17,
        "UK": 43,
        "Italy": 10,
        "USA": 40
    }
    
    axis_additional = additional_ipc["Germany"] + additional_ipc["Italy"] + additional_ipc["Japan"]
    allies_additional = additional_ipc["USSR"] + additional_ipc["UK"] + additional_ipc["USA"]
    total_additional = axis_additional + allies_additional
    
    print(f"Additional IPC at game start:")
    print(f"  Axis powers: {axis_additional} IPC")
    print(f"    Germany: +{additional_ipc['Germany']} IPC")
    print(f"    Italy: +{additional_ipc['Italy']} IPC")
    print(f"    Japan: +{additional_ipc['Japan']} IPC")
    print()
    print(f"  Allied powers: {allies_additional} IPC")
    print(f"    USSR: +{additional_ipc['USSR']} IPC")
    print(f"    UK: +{additional_ipc['UK']} IPC")
    print(f"    USA: +{additional_ipc['USA']} IPC")
    print()
    print(f"  Total additional IPC: {total_additional}")
    print(f"  Allied advantage: +{allies_additional - axis_additional} IPC")
    
    # Calculate what this means in terms of units
    print("\nUnit Purchase Equivalents (additional starting capital):")
    print("  Germany (+31 IPC): ~5 Infantry + 1 Tank + 1 Fighter")
    print("  USSR (+30 IPC): ~6 Infantry + 1 Tank + 1 Artillery")
    print("  Japan (+17 IPC): ~3 Infantry + 1 Tank + AA Gun")
    print("  UK (+43 IPC): ~7 Infantry + 1 Tank + 1 Fighter")
    print("  Italy (+10 IPC): ~2 Infantry + 1 Tank")
    print("  USA (+40 IPC): ~6 Infantry + 1 Tank + 1 Fighter")

def main():
    """Main verification function."""
    print("Axis & Allies Anniversary - Starting IPC Fix Verification")
    print("=" * 60)
    
    # Load campaign data
    campaign_data = load_campaign_data("campaign.json")
    if not campaign_data:
        print("Failed to load campaign data")
        sys.exit(1)
    
    # Verify initial setup
    initial_setup_correct = verify_initial_setup(campaign_data)
    
    # Check educational notes
    notes_correct = check_educational_notes(campaign_data)
    
    # Calculate economic impact
    calculate_economic_impact(campaign_data)
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY:")
    print("=" * 60)
    
    if initial_setup_correct and notes_correct:
        print("✓ All verifications passed!")
        print("✓ Starting IPC values are correct")
        print("✓ Educational notes are present")
        print("✓ Fix has been successfully applied")
    else:
        print("✗ Some verifications failed:")
        if not initial_setup_correct:
            print("  - Starting IPC values incorrect")
        if not notes_correct:
            print("  - Educational notes missing")
    
    print("\nThis fix ensures that all nations start with their full")
    print("economic potential available, as per official rules.")

if __name__ == "__main__":
    main()
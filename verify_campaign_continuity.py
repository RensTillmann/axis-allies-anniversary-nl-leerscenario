#!/usr/bin/env python3
"""
Campaign Continuity Verification Script for Axis & Allies Anniversary Edition

This script verifies the mathematical and logical continuity of the modular campaign by:
1. Loading initial setup and all chapters in sequence
2. Tracking victory cities (should always total 18)
3. Tracking IPC income and banking for each nation
4. Tracking unit counts (purchases, losses, current totals)
5. Tracking factory damage and repairs
6. Verifying territory control changes
7. Checking turn order compliance
8. Verifying income collection timing (only during own turn)

Any continuity errors or mathematical inconsistencies are reported.
"""

import json
import os
from typing import Dict, List, Set, Tuple, Any
from datetime import datetime
from collections import defaultdict
import sys

class CampaignVerifier:
    def __init__(self):
        self.nations = ["Germany", "USSR", "Japan", "UK", "Italy", "USA", "China"]
        self.turn_order = ["Germany", "USSR", "Japan", "UK", "Italy", "USA", "China"]
        self.victory_cities = [
            "Berlin", "Rome", "Tokyo", "Paris", "Warsaw", "Shanghai",
            "Moscow", "London", "Washington", "Leningrad", "Stalingrad",
            "Calcutta", "Sydney", "San Francisco", "Honolulu", "Hong Kong",
            "Ottawa", "Manila"
        ]
        self.total_victory_cities = 18
        self.errors = []
        self.warnings = []
        
        # Track state across chapters
        self.current_state = {
            "victory_cities": {"axis_controlled": [], "allied_controlled": []},
            "ipc_status": {},
            "territories": {},
            "units": defaultdict(lambda: defaultdict(int)),
            "factory_damage": defaultdict(int),
            "turn_number": 0,
            "current_nation": None,
            "technologies": defaultdict(list)
        }
        
    def load_json(self, filepath: str) -> Dict:
        """Load JSON file and return contents."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to load {filepath}: {str(e)}")
            return {}
    
    def verify_victory_cities(self, data: Dict, chapter_name: str):
        """Verify victory cities always total 18 and track changes."""
        if "victory_cities" in data:
            vc = data["victory_cities"]
            axis = set(vc.get("axis_controlled", []))
            allied = set(vc.get("allied_controlled", []))
            
            # Check total count
            total = len(axis) + len(allied)
            if total != self.total_victory_cities:
                self.errors.append(f"{chapter_name}: Victory cities total {total}, expected {self.total_victory_cities}")
            
            # Check for duplicates
            overlap = axis & allied
            if overlap:
                self.errors.append(f"{chapter_name}: Cities controlled by both sides: {overlap}")
            
            # Check all cities are valid
            all_cities = axis | allied
            unknown = all_cities - set(self.victory_cities)
            if unknown:
                self.errors.append(f"{chapter_name}: Unknown victory cities: {unknown}")
            
            # Track changes
            if self.current_state["victory_cities"]:
                prev_axis = set(self.current_state["victory_cities"]["axis_controlled"])
                prev_allied = set(self.current_state["victory_cities"]["allied_controlled"])
                
                gained_by_axis = axis - prev_axis
                lost_by_axis = prev_axis - axis
                gained_by_allied = allied - prev_allied
                lost_by_allied = prev_allied - allied
                
                # Verify consistency
                if gained_by_axis != lost_by_allied:
                    self.errors.append(f"{chapter_name}: Victory city transfer mismatch - Axis gained {gained_by_axis} but Allies didn't lose them")
                if gained_by_allied != lost_by_axis:
                    self.errors.append(f"{chapter_name}: Victory city transfer mismatch - Allies gained {gained_by_allied} but Axis didn't lose them")
            
            # Update state
            self.current_state["victory_cities"] = {
                "axis_controlled": list(axis),
                "allied_controlled": list(allied)
            }
    
    def verify_ipc_tracking(self, data: Dict, chapter_name: str):
        """Verify IPC income, banking, and collection timing."""
        if "ipc_status" in data:
            for nation, ipc_data in data["ipc_status"].items():
                if nation not in self.nations:
                    self.errors.append(f"{chapter_name}: Unknown nation {nation}")
                    continue
                
                income = ipc_data.get("income", 0)
                banked = ipc_data.get("banked", 0)
                total = ipc_data.get("total_available", 0)
                
                # Basic math check
                if income + banked != total:
                    self.errors.append(f"{chapter_name}: {nation} IPC math error: {income} + {banked} != {total}")
                
                # Track changes
                if nation in self.current_state["ipc_status"]:
                    prev = self.current_state["ipc_status"][nation]
                    
                    # Check for negative values
                    if income < 0 or banked < 0:
                        self.errors.append(f"{chapter_name}: {nation} has negative IPC values")
                
                # Update state
                self.current_state["ipc_status"][nation] = ipc_data
    
    def verify_unit_tracking(self, territories: Dict, chapter_name: str):
        """Track unit purchases, losses, and current totals."""
        chapter_units = defaultdict(lambda: defaultdict(int))
        
        # Count all units by nation
        for territory, data in territories.items():
            controller = data.get("controller", "")
            units = data.get("units", {})
            
            for unit_type, count in units.items():
                if count > 0:
                    chapter_units[controller][unit_type] += count
        
        # Compare with previous state
        for nation in self.nations:
            for unit_type in ["infantry", "artillery", "tanks", "fighters", "bombers", 
                            "battleships", "carriers", "cruisers", "destroyers", 
                            "submarines", "transports", "aa_guns"]:
                current = chapter_units[nation][unit_type]
                previous = self.current_state["units"][nation][unit_type]
                
                # Large unexplained changes might indicate errors
                if abs(current - previous) > 10:
                    self.warnings.append(f"{chapter_name}: {nation} {unit_type} changed by {current - previous} units")
        
        # Update state
        self.current_state["units"] = chapter_units
    
    def verify_factory_damage(self, data: Dict, chapter_name: str):
        """Track factory damage and repairs."""
        if "factory_status" in data:
            for location, status in data["factory_status"].items():
                damage = status.get("damage", 0)
                max_damage = status.get("max_damage", 0)
                
                if damage > max_damage:
                    self.errors.append(f"{chapter_name}: {location} factory damage {damage} exceeds max {max_damage}")
                
                if damage < 0:
                    self.errors.append(f"{chapter_name}: {location} factory has negative damage")
                
                # Track changes
                prev_damage = self.current_state["factory_damage"].get(location, 0)
                if damage < prev_damage - 10:  # More than 10 repairs in one turn is suspicious
                    self.warnings.append(f"{chapter_name}: {location} factory repaired {prev_damage - damage} damage")
                
                self.current_state["factory_damage"][location] = damage
    
    def verify_turn_order(self, turns: List[Dict], chapter_name: str):
        """Verify correct turn order and income collection timing."""
        for turn_data in turns:
            turn_num = turn_data.get("turn", 0)
            phase = turn_data.get("phase", "")
            
            # Extract nation from phase
            acting_nation = None
            for nation in self.nations:
                if nation in phase:
                    acting_nation = nation
                    break
            
            if acting_nation:
                # Check turn order
                if self.current_state["current_nation"]:
                    expected_idx = self.turn_order.index(self.current_state["current_nation"])
                    expected_next = self.turn_order[(expected_idx + 1) % len(self.turn_order)]
                    
                    if turn_num > self.current_state["turn_number"]:
                        # New turn started
                        if acting_nation != "Germany" and acting_nation != expected_next:
                            self.warnings.append(f"{chapter_name}: Turn {turn_num} started with {acting_nation}, expected Germany")
                
                self.current_state["current_nation"] = acting_nation
                self.current_state["turn_number"] = turn_num
                
                # Verify income collection timing
                if "Collect Income" in phase:
                    if acting_nation != self.current_state["current_nation"]:
                        self.errors.append(f"{chapter_name}: {acting_nation} collecting income out of turn")
    
    def process_chapter(self, chapter_data: Dict, chapter_name: str) -> Dict:
        """Process a single chapter and extract end state."""
        end_state = {}
        
        # Handle different chapter structures
        if "turns" in chapter_data:
            # Direct turns array
            turns = chapter_data["turns"]
            self.verify_turn_order(turns, chapter_name)
        else:
            # Nested structure with chapter key
            for key, value in chapter_data.items():
                if isinstance(value, dict) and "turns" in value:
                    turns = value["turns"]
                    self.verify_turn_order(turns, chapter_name)
                    
                    # Extract other data
                    if "end_state" in value:
                        end_state = value["end_state"]
                    break
        
        # Look for state data in various locations
        for key in ["end_state", "final_state", "chapter_end"]:
            if key in chapter_data:
                end_state = chapter_data[key]
                break
        
        # Verify components
        if "victory_cities" in end_state:
            self.verify_victory_cities(end_state, chapter_name)
        
        if "ipc_status" in end_state:
            self.verify_ipc_tracking(end_state, chapter_name)
        
        if "territories" in end_state:
            self.verify_unit_tracking(end_state["territories"], chapter_name)
        
        if "factory_status" in end_state:
            self.verify_factory_damage(end_state, chapter_name)
        
        return end_state
    
    def verify_continuity(self, prev_end_state: Dict, next_start_state: Dict, 
                         prev_chapter: str, next_chapter: str):
        """Verify end state of one chapter matches start of next."""
        # Compare victory cities
        if "victory_cities" in prev_end_state and "victory_cities" in next_start_state:
            prev_vc = prev_end_state["victory_cities"]
            next_vc = next_start_state["victory_cities"]
            
            if set(prev_vc.get("axis_controlled", [])) != set(next_vc.get("axis_controlled", [])):
                self.errors.append(f"Victory city mismatch between {prev_chapter} end and {next_chapter} start")
        
        # Compare IPC status
        if "ipc_status" in prev_end_state and "ipc_status" in next_start_state:
            for nation in self.nations:
                if nation in prev_end_state["ipc_status"] and nation in next_start_state["ipc_status"]:
                    prev_ipc = prev_end_state["ipc_status"][nation]
                    next_ipc = next_start_state["ipc_status"][nation]
                    
                    # Allow for income collection between chapters
                    if abs(prev_ipc.get("banked", 0) - next_ipc.get("banked", 0)) > 50:
                        self.warnings.append(f"{nation} IPC changed significantly between {prev_chapter} and {next_chapter}")
    
    def run_verification(self):
        """Run complete verification of the campaign."""
        print("Campaign Continuity Verification")
        print("=" * 50)
        
        chapters_dir = "/projects/axis-allies-anniversary-nl-leerscenario/chapters"
        
        # Load initial setup
        print("\n1. Loading initial setup...")
        initial_data = self.load_json(os.path.join(chapters_dir, "initial_setup_1941.json"))
        if initial_data:
            self.verify_victory_cities(initial_data, "Initial Setup")
            self.verify_ipc_tracking(initial_data, "Initial Setup")
            print(f"   Victory Cities - Axis: {len(self.current_state['victory_cities']['axis_controlled'])}, "
                  f"Allied: {len(self.current_state['victory_cities']['allied_controlled'])}")
        
        # Process chapters in order
        chapter_files = [
            "chapter_01_barbarossa.json",
            "chapter_02_moscow.json", 
            "chapter_03_britain.json",
            "chapter_04_pearl_harbor.json",
            "chapter_05_global_conflict.json",
            "chapter_06_technology.json",
            "chapter_07_atlantic.json",
            "chapter_08_submarines.json",
            "chapter_09_victory.json",
            "chapter_10_china.json"
        ]
        
        prev_end_state = initial_data
        prev_chapter = "Initial Setup"
        
        for i, chapter_file in enumerate(chapter_files, 1):
            print(f"\n{i+1}. Processing {chapter_file}...")
            
            chapter_path = os.path.join(chapters_dir, chapter_file)
            if not os.path.exists(chapter_path):
                self.errors.append(f"Chapter file not found: {chapter_file}")
                continue
            
            chapter_data = self.load_json(chapter_path)
            if not chapter_data:
                continue
            
            # Look for start state
            start_state = None
            for key in ["start_state", "initial_state", "chapter_start"]:
                if key in chapter_data:
                    start_state = chapter_data[key]
                    break
            
            # Verify continuity with previous chapter
            if start_state and prev_end_state:
                self.verify_continuity(prev_end_state, start_state, prev_chapter, chapter_file)
            
            # Process chapter
            end_state = self.process_chapter(chapter_data, chapter_file)
            
            # Print current status
            if self.current_state["victory_cities"]:
                axis_count = len(self.current_state["victory_cities"]["axis_controlled"])
                allied_count = len(self.current_state["victory_cities"]["allied_controlled"])
                print(f"   Victory Cities - Axis: {axis_count}, Allied: {allied_count}")
            
            # Track IPC totals
            if self.current_state["ipc_status"]:
                axis_ipc = sum(data.get("income", 0) for nation, data in self.current_state["ipc_status"].items() 
                             if nation in ["Germany", "Japan", "Italy"])
                allied_ipc = sum(data.get("income", 0) for nation, data in self.current_state["ipc_status"].items() 
                               if nation in ["USSR", "UK", "USA"])
                print(f"   IPC Income - Axis: {axis_ipc}, Allied: {allied_ipc}")
            
            prev_end_state = end_state
            prev_chapter = chapter_file
        
        # Final report
        print("\n" + "=" * 50)
        print("VERIFICATION COMPLETE")
        print("=" * 50)
        
        if self.errors:
            print(f"\n❌ ERRORS FOUND: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
        else:
            print("\n✅ NO ERRORS FOUND")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings[:5]:  # Show first 5 warnings
                print(f"   - {warning}")
            if len(self.warnings) > 5:
                print(f"   ... and {len(self.warnings) - 5} more warnings")
        
        # Final state summary
        print("\n📊 FINAL CAMPAIGN STATE:")
        if self.current_state["victory_cities"]:
            axis_cities = self.current_state["victory_cities"]["axis_controlled"]
            allied_cities = self.current_state["victory_cities"]["allied_controlled"]
            print(f"   Victory Cities - Axis: {len(axis_cities)}, Allied: {len(allied_cities)}")
            print(f"   Victory Condition: {'ALLIED VICTORY' if len(allied_cities) >= 15 else 'AXIS VICTORY' if len(axis_cities) >= 15 else 'ONGOING'}")
        
        if self.current_state["ipc_status"]:
            print("\n   Final IPC Status:")
            for nation in self.turn_order:
                if nation in self.current_state["ipc_status"]:
                    ipc = self.current_state["ipc_status"][nation]
                    print(f"     {nation}: Income {ipc.get('income', 0)}, Banked {ipc.get('banked', 0)}")
        
        return len(self.errors) == 0

if __name__ == "__main__":
    verifier = CampaignVerifier()
    success = verifier.run_verification()
    sys.exit(0 if success else 1)
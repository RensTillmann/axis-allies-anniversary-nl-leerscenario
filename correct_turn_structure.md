# CORRECT TURN STRUCTURE IMPLEMENTATION

## Format: round_X_turn_Y_phase_Z

### Turn Order (1941 Scenario):
- Turn 1: Germany
- Turn 2: Soviet Union  
- Turn 3: Japan
- Turn 4: United Kingdom
- Turn 5: Italy
- Turn 6: United States

### Phase Numbers:
- Phase 1: Research & Development (optional)
- Phase 2: Purchase Units
- Phase 3: Combat Move
- Phase 4: Conduct Combat
- Phase 5: Noncombat Move
- Phase 6: Mobilize New Units
- Phase 7: Collect Income

### Campaign Restructuring:

**Chapter 1 (June 1941):**
- round_1_turn_1_phase_3: German Combat Move (to East Poland)
- round_1_turn_1_phase_4: German Combat (capture East Poland)
- round_1_turn_1_phase_7: German Income Collection
- round_1_turn_2_phase_3: Soviet Combat Move (to Poland)
- round_1_turn_2_phase_4: Soviet Combat (recapture Poland)
- round_1_turn_2_phase_7: Soviet Income Collection

**Chapter 2 (October 1941):**
- round_2_turn_1_phase_2: German Purchase (2 tanks)
- round_2_turn_1_phase_3: German Combat Move (to Ukraine)
- round_2_turn_1_phase_4: German Combat (capture Ukraine)
- round_2_turn_1_phase_6: German Mobilize Units (place tanks)
- round_2_turn_1_phase_7: German Income Collection
- round_2_turn_2_phase_2: Soviet Purchase (6 infantry)
- round_2_turn_2_phase_6: Soviet Mobilize Units (place infantry)
- round_2_turn_2_phase_7: Soviet Income Collection

**Chapter 3 (December 1941):**
- round_2_turn_1_phase_3: German Combat Move (fighters to UK)
- round_2_turn_1_phase_4: German Combat (air sweep + bombing)
- round_2_turn_4_phase_3: UK Combat Move (fighters to Germany)
- round_2_turn_4_phase_4: UK Combat (counter-attack)

This structure ensures each player completes ALL phases before next player begins.
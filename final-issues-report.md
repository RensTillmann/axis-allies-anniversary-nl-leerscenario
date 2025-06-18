# Final Campaign Issues Report

## Critical Issues Found (Must Fix)

### 1. **Chapter 5 - Victory City Contradiction** 🚨
- **Location**: `chapter_05_global_conflict.json` end state
- **Issue**: Cairo shown as Axis-controlled but narrative clearly shows UK recaptured it
- **Details**: 
  - Italian capture: Italy takes Cairo (Axis +1)
  - UK recapture: UK takes Cairo back (should be Allies +1)  
  - End state incorrectly shows Cairo in Axis list
- **Fix Required**: Move Cairo from axis_controlled to allied_controlled list
- **Impact**: Victory city counts wrong (shows Axis 8, should be Axis 7)

### 2. **Chapter 6 - German Income Inconsistency**
- **Location**: `chapter_06_technology.json` 
- **Issue**: Shows German income as 35, but Chapter 5 established it as 39
- **Details**: Missing continuity from Belorussia (+3) and Archangel (+3) captures
- **Fix Required**: Update German income from 35 to 39 or document territorial losses

### 3. **Chapter 7 - Massive German Income Jump**
- **Location**: `chapter_07_atlantic.json`
- **Issue**: Shows German territorial income as 58 (huge jump from 39)
- **Details**: No explanation for +19 IPC gain between chapters
- **Fix Required**: Either document missing conquests or correct income calculation

## Medium Priority Issues

### 4. **Missing Turn Phases**
- Several chapters show income collections without showing complete 7-phase sequences
- Some chapters jump between players without showing all phases
- **Fix**: Add missing phases or clarify which phases are skipped for narrative flow

### 5. **Chapter-to-Chapter Continuity**
- End states don't always match next chapter's starting conditions
- IPC totals may have other undocumented changes
- **Fix**: Systematic verification of all chapter transitions

## Low Priority Issues

### 6. **Inconsistent Field Names**
- Some chapters use "territorial_income", others use "income"
- Some use "ipc_banked", others use "banked"
- **Fix**: Standardize field naming conventions

## Show Stoppers Analysis

### Blocking Issues:
❌ **Chapter 5 Cairo contradiction** - Creates confusion about victory conditions
❌ **German income inconsistencies** - Breaks mathematical continuity

### Non-Blocking Issues:
✅ **Missing phases** - Doesn't prevent gameplay, just narrative completeness
✅ **Field naming** - Cosmetic issue only

## Recommendations

### Immediate Fixes (Required):
1. Fix Chapter 5 victory city end state (Cairo to Allied control)
2. Verify and correct German income progression in Chapters 6-7
3. Document any missing territorial conquests between chapters

### Quality Improvements (Optional):
1. Add missing turn phases for completeness
2. Standardize field naming
3. Add transition verification between all chapters

## Campaign Status
- **Playability**: Still playable with workarounds
- **Educational Value**: Intact (issues don't affect rule learning)
- **Mathematical Accuracy**: Compromised by income inconsistencies
- **Historical Narrative**: Strong throughout

**Verdict**: Fix the 2-3 critical issues and the campaign will be excellent.
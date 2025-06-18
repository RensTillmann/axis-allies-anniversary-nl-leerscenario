# Complete IPC Tracking - Territory Control Analysis

## Initial Setup (June 1941)
- **Germany**: 31 IPC
- **USSR**: 30 IPC  
- **Japan**: 17 IPC
- **UK**: 43 IPC
- **Italy**: 10 IPC
- **USA**: 40 IPC
- **Total**: 171 IPC

## Chapter 1: Operation Barbarossa (June 22-23, 1941)

### German Turn (Round 1, Turn 1):
- **Action**: Captures East Poland from USSR
- **Territory Change**: East Poland (2 IPC) USSR → Germany
- **Germany Income**: 31 + 2 = **33 IPC**
- **USSR Income**: 30 - 2 = **28 IPC**
- **Income Collection**: Germany collects 33 IPC ✓

### Soviet Turn (Round 1, Turn 2):
- **Action**: Recaptures Poland from Germany
- **Territory Change**: Poland (2 IPC) Germany → USSR  
- **Germany Income**: 33 - 2 = **31 IPC**
- **USSR Income**: 28 + 2 = **30 IPC**
- **Income Collection**: USSR collects 30 IPC ✓

### Chapter 1 End State:
- **Germany**: 31 income, 33 banked ✓
- **USSR**: 30 income, 30 banked ✓

## Chapter 2: Industrial Philosophy (October 1941)

### German Turn (Round 2, Turn 1):
- **Starting Income**: 31 IPC (lost Poland in Chapter 1)
- **Purchases**: 2 tanks (10 IPC), Banked: 33 - 10 = 23 IPC
- **Action**: Captures Ukraine from USSR
- **Territory Change**: Ukraine (2 IPC) USSR → Germany
- **Germany Income**: 31 + 2 = **33 IPC**
- **USSR Income**: 30 - 2 = **28 IPC**
- **Income Collection**: Germany should collect 33 IPC (not 35!)
- **❌ Current Error**: Shows 35 IPC collection with wrong calculation
- **✅ Correct**: 23 banked + 33 collected = 56 total

### Soviet Turn (Round 2, Turn 2):
- **Starting Income**: 28 IPC  
- **Purchases**: 6 infantry (18 IPC), Banked: 30 - 18 = 12 IPC
- **Income Collection**: USSR collects 28 IPC ✓
- **Banked Total**: 12 + 28 = 40 IPC

### Chapter 2 End State (ERRORS TO FIX):
- **❌ Germany**: Shows income 33, banked 23 (should be 33 income, 56 banked)
- **❌ USSR**: Shows income 28, banked 12 (should be 28 income, 40 banked)

## Chapter 3: Air Warfare Evolution (December 1941)

### German Turn (Round 3, Turn 1):
- **Starting Income**: 33 IPC
- **Starting Banked**: 56 IPC (from corrected Chapter 2)
- **No territorial changes**
- **Income Collection**: Should collect 33 IPC
- **❌ Current Error**: Shows "21 previous + 33 collected = 54"
- **✅ Correct**: 56 previous + 33 collected = 89 banked

### Chapter 3 End State (ERRORS TO FIX):
- **❌ Germany**: Shows income 33, banked 54 (should be 33 income, 89 banked)

## CORRECTIONS MADE:

### Chapter 2:
✅ Fixed German income collection: 35 → 33 IPC
✅ Fixed German banked total: 23 → 56 IPC  
✅ Fixed USSR banked total: 12 → 40 IPC
✅ Removed `total_available_next` fields

### Chapter 3:
✅ Fixed German income collection: 54 → 89 banked total
✅ Fixed German end state: 54 → 89 banked
✅ USSR correctly shows 40 banked (no income collection in Ch3)

### Chapter 5:
✅ Fixed German territorial income: 33 → 39 IPC (added Belorussia +3, Archangel +3)
✅ Fixed German banked total: 120 → 128 IPC
✅ Fixed UK territorial income: Cairo recaptured (43 IPC maintained)
✅ Fixed UK banked total: 127 → 86 IPC

## SUMMARY OF CURRENT STATUS:
- **Germany**: 39 income, 128 banked (Chapter 5 end)
- **USSR**: 28 income, 40 banked (needs Chapter 5 verification)
- **Japan**: 19 income, 46 banked (Chapter 4 end)
- **UK**: 43 income, 86 banked (Chapter 5 end)
- **USA**: 38 income, 3 banked (Chapter 4 end)
- **Italy**: Needs verification for Cairo loss/recapture

## Still Need to Check:
- Chapter 6-10 territorial changes and income collections
- USSR income collection in Chapter 5+ (if any)
- Italy income changes from Cairo operations
- All `total_available_next` field removals in remaining chapters
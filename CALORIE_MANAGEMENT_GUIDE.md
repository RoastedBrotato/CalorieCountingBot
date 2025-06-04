# 🍎 Complete Calorie Management Guide

## 📊 Viewing Your Calories

### `!today` - Quick Daily Overview
- Shows your **total calories** for today
- Displays **last 10 entries** with numbers for easy reference
- Each entry shows: `#. Time Food Name - Calories`
- **Example Output**:
```
📊 John's Calories Today
Total: 1,247 kcal

🍽️ Recent Foods
1. 09:00 Oatmeal with berries - 180 kcal
2. 12:15 Caesar salad - 250 kcal
3. 14:30 Grilled chicken - 300 kcal
```

### `!history` - Full Daily History
- Shows **ALL** your entries for today (no 10-entry limit)
- Perfect for reviewing everything you've eaten
- Still shows numbered entries for easy management

## 🗑️ Removing Entries

### `!remove <number>`
**Examples:**
```
!remove 2        # Removes entry #2
!remove 5        # Removes entry #5
```
- Removes the specific entry by its number
- **Automatically updates** your daily total
- Shows confirmation with new total

## ✏️ Editing Entries

### `!edit <number> <new_calories> [new_name]`
**Examples:**
```
!edit 3 350                           # Just change calories
!edit 3 350 Grilled chicken breast    # Change calories AND name
!edit 1 200 Steel cut oatmeal         # Update both values
```
- Edit calories and/or food name for any entry
- **Automatically recalculates** your daily total
- Shows what changed and the difference in calories

## 🔄 Managing Your Day

### `!reset` - Clear Everything
- Resets your entire day to 0 calories
- **Requires confirmation** with ✅/❌ reactions
- 30-second timeout for safety

## 🎯 Smart Workflow

### Best Practice for Daily Tracking:
1. **Add calories** throughout the day:
   - Use AI analysis: `!analyzeimage`, `!analyzefood`, `!estimate`
   - React with ✅ to quickly add
   - Or manually: `!addcalories 300 Chicken`

2. **Check progress**: `!today`

3. **Make corrections** as needed:
   - `!remove 4` if you accidentally added something
   - `!edit 2 250` if you underestimated portion size
   - `!edit 3 400 Large burger` to update both calories and name

4. **Review full day**: `!history`

## 🔥 AI-Powered + Manual Management

### Complete Calorie Tracking Workflow:
```
# Morning
!analyzefood 1 cup oatmeal with banana
✅ (react to add 180 kcal)

# Lunch - made an error
!addcalories 500 Salad
!edit 2 250 Small Caesar salad    # Correct the overestimate

# Afternoon snack
!estimate apple with peanut butter
✅ (react to add 190 kcal)

# Dinner
!analyzeimage                     # Upload dinner photo
✅ (react to add calories)

# Check daily progress
!today                           # See numbered list
!remove 4                        # Remove duplicate entry
!history                         # Review full day
```

## 📈 Entry Management Tips

### Using Entry Numbers:
- Entry numbers are **permanent** - removing entry #3 doesn't renumber others
- Use `!today` to see current numbers before editing/removing
- Numbers make it easy to reference specific meals

### Smart Editing:
- **Just calories**: `!edit 2 300`
- **Calories + name**: `!edit 2 300 New food name`
- **Complex names**: Use quotes if needed or just type naturally

### Quick Corrections:
- Wrong amount? `!edit <#> <correct_calories>`
- Duplicate entry? `!remove <#>`
- Forgot something? `!addcalories <amount> <food>`

## 🎯 Summary of All Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `!today` | View daily calories with numbers | `!today` |
| `!history` | View all entries for today | `!history` |
| `!remove <#>` | Delete specific entry | `!remove 3` |
| `!edit <#> <cal> [name]` | Edit entry | `!edit 2 250 Salad` |
| `!addcalories <cal> [name]` | Add manually | `!addcalories 300 Snack` |
| `!reset` | Clear entire day | `!reset` |
| `!analyzeimage` | AI image analysis | Upload + `!analyzeimage` |
| `!analyzefood [desc]` | Enhanced AI analysis | `!analyzefood 350g chicken` |
| `!estimate <desc>` | Text-only estimation | `!estimate 2 cups rice` |

Your calorie tracking is now **fully manageable** with easy viewing, editing, and removal of entries! 🎉

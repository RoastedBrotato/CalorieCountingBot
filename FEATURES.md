# Enhanced Calorie Tracking Features

## New Commands Added

### 1. `!analyzefood [description]` - Enhanced Image Analysis
- **Purpose**: Combine image analysis with text descriptions for maximum accuracy
- **Usage**: Upload an image and include measurements/descriptions
- **Example**: `!analyzefood 350g grilled chicken breast with steamed broccoli`
- **Benefits**:
  - Higher confidence scores (up to 85%+)
  - More accurate portion size estimates
  - Better calorie calculations based on specific measurements
  - Enhanced nutritional information

### 2. `!estimate <description>` - Text-Only Analysis
- **Purpose**: Get calorie estimates without needing images
- **Usage**: Describe your food with measurements
- **Example**: `!estimate 2 cups brown rice with 150g salmon and vegetables`
- **Benefits**:
  - Quick calorie logging without photos
  - Perfect for homemade meals
  - Includes nutritional breakdown
  - AI interpretation of your description

## Enhanced Features

### Improved Image Analysis
- **Better prompts** for more accurate AI analysis
- **Confidence-based color coding** in embed responses
- **Enhanced error handling** for API issues
- **Detailed nutritional breakdowns** with health notes

### Smart Description Processing
- **Measurement recognition** (grams, cups, pieces, etc.)
- **Cooking method consideration** (grilled, fried, baked)
- **Ingredient separation** for complex meals
- **Portion size validation** against visual cues

### Enhanced User Experience
- **Visual feedback** with confidence indicators
- **Description accuracy matching** (good/partial/poor)
- **Quick add buttons** (✅/❌ reactions)
- **Comprehensive help system**
- **Persistent calorie tracking** with daily totals
- **Automatic logging** via reaction buttons

## New Tracking Features

### 4. `!today` - View Daily Progress
- **Purpose**: Check your calorie intake for today
- **Shows**: Total calories, recent foods, timestamps
- **Example Output**: 
  ```
  📊 John's Calories Today
  Total: 1,247 kcal
  
  🍽️ Recent Foods
  14:30 Grilled chicken - 300 kcal
  12:15 Caesar salad - 250 kcal
  09:00 Oatmeal with berries - 180 kcal
  ```

### 5. `!reset` - Clear Daily Progress
- **Purpose**: Reset today's calorie count to zero
- **Safety**: Requires confirmation with ✅/❌ reactions
- **Use case**: Mistaken entries or starting fresh

### 6. Enhanced `!addcalories` Command
- **New feature**: Shows updated daily total after adding
- **Integration**: Works with persistent storage system
- **Example**: "Added 300 kcal for Chicken • Today's Total: 1,547 kcal"

## Reaction-Based Quick Logging

### How It Works
1. Use any AI analysis command (`!analyzeimage`, `!analyzefood`, `!estimate`)
2. Bot provides calorie estimate with ✅ and ❌ reactions
3. Click ✅ to automatically add calories to your daily total
4. Click ❌ to decline (analysis is ignored)
5. Get instant confirmation with updated daily total

### Benefits
- **No manual typing** - just react to add calories
- **Prevents duplicate entries** - one reaction = one log entry
- **Instant feedback** - see your daily total immediately
- **Error prevention** - confirmation messages prevent mistakes

## Data Persistence

### Storage System
- **JSON file storage** (`user_calories.json`)
- **Per-user tracking** - each Discord user has separate data
- **Daily organization** - calories organized by date
- **Automatic backup** - data saved after each entry

### Data Structure
```json
{
  "user_id": {
    "2025-06-04": {
      "total_calories": 1247,
      "foods": [
        {
          "name": "Grilled chicken",
          "calories": 300,
          "timestamp": "2025-06-04T14:30:00"
        }
      ]
    }
  }
}
```

## Command Hierarchy

1. **Basic**: `!analyzeimage` - Image only
2. **Enhanced**: `!analyzefood [description]` - Image + text for accuracy
3. **Text-only**: `!estimate <description>` - No image needed
4. **Manual**: `!addcalories <amount> [food]` - Direct entry
5. **Tracking**: `!today` - View progress, `!reset` - Clear day

## Usage Tips

### For Best Results with `!analyzefood`:
- Include specific weights (350g, 2 cups, 1 medium)
- Mention cooking methods (grilled, steamed, fried)
- Describe visible ingredients
- Be specific about portion sizes

### For Accurate Text Estimates with `!estimate`:
- Use standard measurements
- Include preparation details
- Mention sauces or additions
- Specify cooking methods

## Technical Implementation

### New Functions Added:
- `analyze_food_with_description()` - Enhanced analysis with text
- Enhanced prompt engineering for better AI responses
- Improved JSON parsing and error handling
- Confidence scoring based on description accuracy

### Error Handling:
- API key validation
- Image download verification
- JSON parsing fallbacks
- Comprehensive error messages with help links

## Future Enhancements

- User preference learning
- Meal logging and history
- Daily calorie tracking
- Nutritional goal setting
- Recipe analysis
- Barcode scanning integration

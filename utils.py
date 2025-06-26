def word_to_num(word):
    """Convert word numbers to integers"""
    word_dict = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
        'to': 2  # Common misheard word
    }
    return word_dict.get(word.lower(), None)

def extract_prescription(text, medicines_list, threshold=80):
    """Extract prescription information from text, limited to top 5 most similar medicines."""
    prescriptions = []
    import re
    from rapidfuzz import fuzz

    found_meds = []
    text_lower = text.lower()
    for med in medicines_list:
        med_clean = med.strip().lower()
        score = fuzz.partial_ratio(med_clean, text_lower)
        if score >= threshold:
            start = text_lower.find(med_clean.split()[0])
            found_meds.append({'name': med, 'start': start, 'score': score})

    # Sort by highest similarity score, then by order of appearance
    found_meds.sort(key=lambda x: (-x['score'], x['start']))
    # Limit to top 5 most similar
    found_meds = found_meds[:5]

    for i in range(len(found_meds)):
        med_name = found_meds[i]['name']
        start_pos = found_meds[i]['start']
        end_pos = found_meds[i+1]['start'] if i + 1 < len(found_meds) else len(text)
        segment = text[start_pos:end_pos]
        
        # Extract days
        num_pattern = r'(\d+|one|two|to|three|four|five|six|seven|eight|nine|ten)'
        days_match = re.search(num_pattern + r'\s*(day|days)', segment, re.IGNORECASE)
        days = 1
        if days_match:
            days_str = days_match.group(1)
            num_val = word_to_num(days_str) if not days_str.isdigit() else int(days_str)
            days = num_val if num_val else 1
        
        # Extract tablets
        tablets_match = re.search(num_pattern + r'\s*(tablet|tablets)', segment, re.IGNORECASE)
        tablets = 1
        if tablets_match:
            tablets_str = tablets_match.group(1)
            num_val = word_to_num(tablets_str) if not tablets_str.isdigit() else int(tablets_str)
            tablets = num_val if num_val else 1
        
        # Determine meal time
        meal = 'After Meal'
        if 'before meal' in segment.lower():
            meal = 'Before Meal'
        elif 'after meal' in segment.lower() or 'afternoon' in segment.lower():
            meal = 'After Meal'
        
        prescriptions.append({
            'Medicine Name': med_name,
            'Number of Days': days,
            'Tablets per Day': tablets,
            'Meal Time': meal
        })
    
    return prescriptions 
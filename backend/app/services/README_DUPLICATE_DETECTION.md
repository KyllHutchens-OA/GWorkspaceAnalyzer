# Duplicate Detection - Conservative Approach

## Philosophy

**Guaranteed Savings vs. Review Flags**

We take a conservative approach to avoid false positives that could damage user trust:

### 1. Exact Duplicates (HIGH CONFIDENCE - Counted as Waste)
- **Criteria**: Same invoice number + vendor + amount
- **Confidence**: 98%
- **Amount**: Full duplicate amount counted as waste
- **Action**: User can immediately claim this as a duplicate charge

**Example:**
```
AWS Invoice #INV-2024-001 for $1,250 charged on Mar 1 and Mar 2
= $1,250 guaranteed waste
```

### 2. Probable Duplicates (LOW CONFIDENCE - Review Flag Only)
- **Criteria**: Same vendor + amount within 2 days
- **Confidence**: 50%
- **Amount**: $0.00 (NOT counted as guaranteed waste)
- **Action**: Flagged for user review with note

**Why the conservative approach?**
- Weekly subscriptions (every 7 days) are normal
- Monthly subscriptions (every ~30 days) are normal
- We don't want to claim "You're wasting $500" when it's a legitimate subscription

**Example:**
```
Stripe $49.00 on Mar 1 and Mar 3 (2 days apart)
- Could be a duplicate
- Could be two separate legitimate charges
- Potential waste: $49.00 (shown in details)
- Guaranteed waste: $0.00
- Note: "Please verify if this is a legitimate recurring charge or a duplicate"
```

### 3. Subscription Detection
Before flagging a probable duplicate, we check if it's a regular subscription:

**Detected patterns:**
- Weekly: 7 days ± 2 days
- Bi-weekly: 14 days ± 3 days
- Monthly: 30 days ± 5 days
- Quarterly: 90 days ± 7 days
- Annual: 365 days ± 14 days

If 3+ charges match these patterns, they're **NOT** flagged as duplicates.

## Dashboard Display

### Guaranteed Waste (Bold, Large)
```
You're wasting $1,250 this month
```
Only includes:
- Exact duplicates (98% confidence)
- Verified price increases
- User-confirmed issues

### Potential Issues (Separate Section)
```
Review These Charges (2 items)
- Stripe: $49.00 charged twice within 2 days → Potential waste: $49.00
  [Mark as Duplicate] [It's Legitimate]
```

## User Actions

For probable duplicates, user can:
1. **Mark as Duplicate** → Moves to guaranteed waste, creates refund task
2. **It's Legitimate** → Removes from review list
3. **Add Note** → User can explain what it is

## Configuration

```python
detector = DuplicateDetector(
    duplicate_window_days=7,  # Only used for temporal clustering
    price_threshold=20.0      # Flag price increases >20%
)
```

**Probable duplicate window is hardcoded to 2 days** to avoid false positives.

## Testing

```bash
cd backend
python tests/test_duplicate_detector.py
```

Expected results:
- Exact duplicates: Counted as waste
- Probable duplicates: $0.00 waste, flagged for review
- Subscriptions: Not flagged at all

## Future Enhancements

1. **Machine Learning**: Learn from user feedback (duplicate vs legitimate)
2. **Vendor-specific rules**: Some vendors always send 2 emails (receipt + invoice)
3. **Amount tolerance**: Allow small variations ($49.00 vs $49.99)
4. **Invoice content matching**: Compare line items, not just totals

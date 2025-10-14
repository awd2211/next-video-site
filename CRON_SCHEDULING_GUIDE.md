# Cron Expression Scheduling Guide

## 📅 Overview

The enhanced scheduling system now supports **Cron expressions** for flexible, powerful recurrence rules. This allows you to create complex scheduling patterns beyond simple daily, weekly, or monthly recurrences.

## 🎯 What Are Cron Expressions?

Cron expressions are a time-based job scheduling format consisting of 5 fields:

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

### Special Characters

| Character | Meaning | Example |
|-----------|---------|---------|
| `*` | Every value | `* * * * *` = every minute |
| `*/n` | Every n values | `*/15 * * * *` = every 15 minutes |
| `a-b` | Range from a to b | `9-17 * * *` = hours 9 to 17 |
| `a,b,c` | Specific values | `0 9,12,18 * * *` = 9 AM, noon, 6 PM |
| `-` | Range separator | `1-5` = Monday to Friday |

## 📚 Common Patterns

### Frequent Schedules

| Pattern | Expression | Description |
|---------|-----------|-------------|
| **Every minute** | `* * * * *` | Runs every minute |
| **Every 5 minutes** | `*/5 * * * *` | Runs every 5 minutes |
| **Every 15 minutes** | `*/15 * * * *` | Runs every 15 minutes |
| **Every 30 minutes** | `*/30 * * * *` | Runs every 30 minutes |

### Hourly Schedules

| Pattern | Expression | Description |
|---------|-----------|-------------|
| **Every hour** | `0 * * * *` | Top of every hour |
| **Every 2 hours** | `0 */2 * * *` | Every 2 hours at :00 |
| **Every 6 hours** | `0 */6 * * *` | Every 6 hours (12am, 6am, 12pm, 6pm) |
| **Every 12 hours** | `0 */12 * * *` | Twice daily (12am, 12pm) |

### Daily Schedules

| Pattern | Expression | Description |
|---------|-----------|-------------|
| **Daily at 9 AM** | `0 9 * * *` | Every day at 9:00 AM |
| **Daily at noon** | `0 12 * * *` | Every day at 12:00 PM |
| **Daily at 6 PM** | `0 18 * * *` | Every day at 6:00 PM |
| **Daily at midnight** | `0 0 * * *` | Every day at 12:00 AM |
| **Twice daily** | `0 9,18 * * *` | 9 AM and 6 PM every day |

### Weekly Schedules

| Pattern | Expression | Description |
|---------|-----------|-------------|
| **Weekdays at 9 AM** | `0 9 * * 1-5` | Monday to Friday at 9 AM |
| **Weekdays at 6 PM** | `0 18 * * 1-5` | Monday to Friday at 6 PM |
| **Weekends at 10 AM** | `0 10 * * 0,6` | Saturday and Sunday at 10 AM |
| **Monday mornings** | `0 9 * * 1` | Every Monday at 9 AM |
| **Friday evenings** | `0 17 * * 5` | Every Friday at 5 PM |

### Monthly Schedules

| Pattern | Expression | Description |
|---------|-----------|-------------|
| **First of month** | `0 9 1 * *` | 1st day of every month at 9 AM |
| **Mid-month** | `0 9 15 * *` | 15th of every month at 9 AM |
| **Last weekday** | `0 9 28-31 * *` | Between 28-31 (catches month end) |

### Special Patterns

| Pattern | Expression | Description |
|---------|-----------|-------------|
| **Quarterly** | `0 9 1 */3 *` | Every 3 months on 1st at 9 AM |
| **Business hours** | `0 9-17 * * 1-5` | Hourly during 9-5, Mon-Fri |
| **Night shift** | `0 0-6,18-23 * * *` | Every hour from 6 PM to 6 AM |

## 🚀 Quick Start

### 1. Backend Implementation

Create a schedule with cron recurrence:

```python
from app.schemas.scheduling import ScheduleCreate
from app.models.scheduling import ScheduleRecurrence

schedule_data = ScheduleCreate(
    content_type="video",
    content_id=123,
    scheduled_time=datetime.now(timezone.utc),
    recurrence=ScheduleRecurrence.CUSTOM,  # Use CUSTOM for cron
    recurrence_config={
        "cron_expression": "0 9 * * 1-5"  # Weekdays at 9 AM
    },
    auto_publish=True,
    priority=80
)
```

### 2. API Validation

Validate cron expressions before using them:

```bash
# Validate expression
curl -X POST "http://localhost:8000/api/v1/admin/scheduling/cron/validate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"expression": "0 9 * * 1-5"}'

# Response:
{
  "valid": true,
  "description": "On monday to friday at 9:00",
  "next_occurrences": [
    "2025-10-15T09:00:00+00:00",
    "2025-10-16T09:00:00+00:00",
    "2025-10-17T09:00:00+00:00",
    "2025-10-18T09:00:00+00:00",
    "2025-10-19T09:00:00+00:00"
  ]
}
```

### 3. Frontend Usage

Use the `CronBuilder` component:

```tsx
import CronBuilder from '@/components/CronBuilder'

function ScheduleForm() {
  const [cronExpression, setCronExpression] = useState('0 9 * * *')

  return (
    <Form>
      <Form.Item label="Recurrence Pattern">
        <CronBuilder
          value={cronExpression}
          onChange={setCronExpression}
          onValidate={(valid, description) => {
            console.log('Valid:', valid, 'Description:', description)
          }}
        />
      </Form.Item>
    </Form>
  )
}
```

## 📖 API Reference

### POST `/api/v1/admin/scheduling/cron/validate`

Validate a cron expression.

**Request:**
```json
{
  "expression": "0 9 * * 1-5"
}
```

**Response:**
```json
{
  "valid": true,
  "error_message": null,
  "description": "On monday to friday at 9:00",
  "next_occurrences": [
    "2025-10-15T09:00:00Z",
    "2025-10-16T09:00:00Z",
    ...
  ]
}
```

### GET `/api/v1/admin/scheduling/cron/patterns`

Get predefined cron patterns.

**Response:**
```json
{
  "patterns": [
    {
      "name": "daily_morning",
      "expression": "0 9 * * *",
      "description": "Daily at 9:00 AM",
      "category": "daily",
      "next_run": "2025-10-15T09:00:00Z"
    },
    ...
  ],
  "categories": ["frequent", "hourly", "daily", "weekly", "monthly", "special"]
}
```

### POST `/api/v1/admin/scheduling/cron/next-runs`

Calculate next N execution times.

**Request:**
```json
{
  "expression": "0 9 * * 1-5",
  "count": 10,
  "from_time": "2025-10-14T00:00:00Z"  // optional
}
```

**Response:**
```json
{
  "expression": "0 9 * * 1-5",
  "description": "On monday to friday at 9:00",
  "next_runs": [
    "2025-10-14T09:00:00Z",
    "2025-10-15T09:00:00Z",
    ...
  ]
}
```

## 🔧 Utilities Reference

### CronValidator

```python
from app.utils.cron_utils import CronValidator

# Validate expression
is_valid, error_msg = CronValidator.validate_cron_expression("0 9 * * *")

# Get human-readable description
description = CronValidator.describe_cron("0 9 * * 1-5")
# Returns: "On monday to friday at 9:00"

# Get next occurrences
occurrences = CronValidator.get_next_occurrences("0 9 * * *", count=5)
# Returns: [datetime, datetime, ...]

# Get common patterns
patterns = CronValidator.get_common_patterns()
# Returns: {"daily_9am": "0 9 * * *", ...}
```

### CronScheduleCalculator

```python
from app.utils.cron_utils import CronScheduleCalculator

# Calculate next run time
next_run = CronScheduleCalculator.calculate_next_run(
    "0 9 * * 1-5",
    last_run=datetime.now(),
    timezone_offset=0
)

# Check if should execute now
should_execute = CronScheduleCalculator.should_execute_now(
    "0 9 * * *",
    last_run=last_execution_time,
    grace_period_seconds=60
)

# Get all executions in date range
executions = CronScheduleCalculator.get_execution_windows(
    "0 9 * * 1-5",
    start_date=start,
    end_date=end,
    max_results=100
)
```

## 💡 Use Cases

### 1. Content Publishing Schedule

**Scenario:** Publish new videos every weekday morning at 9 AM

```json
{
  "content_type": "video",
  "content_id": 456,
  "scheduled_time": "2025-10-15T09:00:00Z",
  "recurrence": "custom",
  "recurrence_config": {
    "cron_expression": "0 9 * * 1-5"
  },
  "auto_publish": true
}
```

### 2. Weekend Highlights

**Scenario:** Publish weekend highlight reels every Saturday at 10 AM

```json
{
  "content_type": "video",
  "content_id": 789,
  "scheduled_time": "2025-10-18T10:00:00Z",
  "recurrence": "custom",
  "recurrence_config": {
    "cron_expression": "0 10 * * 6"
  },
  "auto_publish": true
}
```

### 3. Prime Time Publishing

**Scenario:** Publish content during peak hours (9 AM, noon, 6 PM) on weekdays

```json
{
  "content_type": "video",
  "content_id": 101,
  "scheduled_time": "2025-10-15T09:00:00Z",
  "recurrence": "custom",
  "recurrence_config": {
    "cron_expression": "0 9,12,18 * * 1-5"
  },
  "notify_subscribers": true,
  "auto_publish": true
}
```

### 4. Monthly Newsletter

**Scenario:** Publish monthly newsletter on the 1st at 8 AM

```json
{
  "content_type": "announcement",
  "content_id": 202,
  "scheduled_time": "2025-11-01T08:00:00Z",
  "recurrence": "custom",
  "recurrence_config": {
    "cron_expression": "0 8 1 * *"
  },
  "auto_publish": true
}
```

### 5. Quarterly Reports

**Scenario:** Publish quarterly business reports on the 1st day of Q1, Q2, Q3, Q4

```json
{
  "content_type": "video",
  "content_id": 303,
  "scheduled_time": "2026-01-01T09:00:00Z",
  "recurrence": "custom",
  "recurrence_config": {
    "cron_expression": "0 9 1 1,4,7,10 *"
  },
  "priority": 100
}
```

## ⚠️ Important Notes

### Validation Rules

1. **Minimum Interval:** Cron expressions cannot execute more than once per minute
2. **Expression Format:** Must be exactly 5 space-separated fields
3. **Valid Ranges:**
   - Minute: 0-59
   - Hour: 0-23
   - Day: 1-31
   - Month: 1-12
   - Weekday: 0-6 (0 = Sunday)

### Best Practices

1. **Always Validate:** Use the validation API before creating schedules
2. **Preview Next Runs:** Check next occurrences to ensure correct pattern
3. **Use Templates:** Start with predefined patterns when possible
4. **Test First:** Create test schedules to verify behavior
5. **Monitor Execution:** Check schedule history for any issues

### Performance Considerations

- Complex expressions with high frequency may impact system performance
- Avoid overlapping schedules for the same content
- Use priority levels to manage execution order
- Monitor Celery worker logs for execution patterns

## 🔍 Troubleshooting

### Common Errors

**Error:** "Invalid cron expression format"
- **Solution:** Ensure exactly 5 fields separated by spaces

**Error:** "Cron expression interval too frequent"
- **Solution:** Minimum interval is 1 minute, use `*/1 * * * *` or longer

**Error:** "CUSTOM recurrence requires 'cron_expression'"
- **Solution:** Include `cron_expression` in `recurrence_config` when using `ScheduleRecurrence.CUSTOM`

### Debugging Tips

1. **Check validation response:**
   ```bash
   curl -X POST /api/v1/admin/scheduling/cron/validate \
     -d '{"expression": "YOUR_EXPRESSION"}'
   ```

2. **View next executions:**
   ```bash
   curl -X POST /api/v1/admin/scheduling/cron/next-runs \
     -d '{"expression": "YOUR_EXPRESSION", "count": 10}'
   ```

3. **Check Celery logs:**
   ```bash
   docker-compose logs -f celery-worker
   ```

## 🎨 Frontend Components

### CronBuilder Component

The `CronBuilder` component provides three input modes:

1. **Templates Tab:** Select from predefined patterns
2. **Simple Builder Tab:** Visual dropdown selectors for each field
3. **Advanced Tab:** Manual text input with validation

**Props:**
- `value?: string` - Current cron expression
- `onChange?: (value: string) => void` - Callback when expression changes
- `onValidate?: (valid: boolean, description: string) => void` - Validation callback

**Features:**
- Real-time validation with visual feedback
- Preview of next 5 execution times
- Human-readable descriptions
- Category-organized templates
- Copy-paste support for expressions

## 📊 Integration Examples

### With Scheduling Form

```tsx
import { Form, DatePicker, Select, InputNumber } from 'antd'
import CronBuilder from '@/components/CronBuilder'
import { ScheduleRecurrence } from '@/types/scheduling'

function ScheduleForm() {
  const [recurrence, setRecurrence] = useState<ScheduleRecurrence>('once')
  const [cronExpression, setCronExpression] = useState('0 9 * * *')

  return (
    <Form>
      <Form.Item label="Recurrence Type" name="recurrence">
        <Select onChange={(value) => setRecurrence(value)}>
          <Select.Option value="once">Once</Select.Option>
          <Select.Option value="daily">Daily</Select.Option>
          <Select.Option value="weekly">Weekly</Select.Option>
          <Select.Option value="monthly">Monthly</Select.Option>
          <Select.Option value="custom">Custom (Cron)</Select.Option>
        </Select>
      </Form.Item>

      {recurrence === 'custom' && (
        <Form.Item label="Cron Pattern" required>
          <CronBuilder
            value={cronExpression}
            onChange={setCronExpression}
          />
        </Form.Item>
      )}

      {/* Other form fields */}
    </Form>
  )
}
```

### With Calendar View

The calendar view automatically handles cron-based recurring schedules:

```tsx
import { Calendar } from '@fullcalendar/react'

// Recurring events with cron are expanded automatically
// The backend calculates next_occurrence for each schedule
```

## 🚦 Testing

### Unit Tests

```python
# Test cron validation
def test_cron_validation():
    from app.utils.cron_utils import CronValidator

    # Valid expression
    is_valid, msg = CronValidator.validate_cron_expression("0 9 * * 1-5")
    assert is_valid is True

    # Invalid expression
    is_valid, msg = CronValidator.validate_cron_expression("invalid")
    assert is_valid is False

# Test next occurrence calculation
def test_next_occurrence():
    from app.utils.cron_utils import CronScheduleCalculator
    from datetime import datetime, timezone

    next_run = CronScheduleCalculator.calculate_next_run(
        "0 9 * * *",
        datetime(2025, 10, 14, 8, 0, 0, tzinfo=timezone.utc)
    )

    assert next_run.hour == 9
    assert next_run.minute == 0
```

### Integration Tests

```bash
# Test cron validation endpoint
curl -X POST http://localhost:8000/api/v1/admin/scheduling/cron/validate \
  -H "Content-Type: application/json" \
  -d '{"expression": "0 9 * * 1-5"}'

# Test pattern retrieval
curl http://localhost:8000/api/v1/admin/scheduling/cron/patterns

# Test schedule creation with cron
curl -X POST http://localhost:8000/api/v1/admin/scheduling/ \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "video",
    "content_id": 123,
    "scheduled_time": "2025-10-15T09:00:00Z",
    "recurrence": "custom",
    "recurrence_config": {
      "cron_expression": "0 9 * * 1-5"
    }
  }'
```

## 📚 Additional Resources

- [Cron Expression Syntax](https://crontab.guru/) - Interactive cron expression tester
- [Croniter Documentation](https://github.com/kiorky/croniter) - Python library used
- [Scheduling System Guide](./SCHEDULING_SYSTEM_ENHANCEMENTS.md) - Complete scheduling docs
- [API Reference](./SCHEDULING_COMPLETE_SUMMARY.md) - Full API documentation

## 🎉 Summary

With cron expression support, you can now create:

✅ **Flexible schedules** - Any time pattern imaginable
✅ **Precise timing** - Down to the minute
✅ **Complex recurrence** - Weekdays, specific dates, ranges
✅ **Business rules** - Match your content strategy
✅ **Easy management** - Visual builder + templates

The enhanced recurrence system brings enterprise-level scheduling capabilities to your content management platform! 🚀

"""
Cron Expression Utilities
Provides cron expression validation, parsing, and next execution calculation
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from croniter import croniter
from loguru import logger


class CronValidator:
    """Cron expression validator and parser"""

    @staticmethod
    def validate_cron_expression(expression: str) -> Tuple[bool, Optional[str]]:
        """
        Validate cron expression format

        Args:
            expression: Cron expression string (e.g., "0 9 * * 1-5")

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if expression is valid
            if not croniter.is_valid(expression):
                return False, "Invalid cron expression format"

            # Additional validation: ensure expression is not too frequent
            cron = croniter(expression, datetime.now(timezone.utc))
            next_run = cron.get_next(datetime)
            second_run = cron.get_next(datetime)

            interval_seconds = (second_run - next_run).total_seconds()

            # Prevent expressions that run more than once per minute
            if interval_seconds < 60:
                return False, "Cron expression interval too frequent (minimum 1 minute)"

            return True, None

        except Exception as e:
            logger.error(f"Cron validation error: {e}")
            return False, f"Cron expression error: {str(e)}"

    @staticmethod
    def get_next_occurrences(
        expression: str, count: int = 5, start_time: Optional[datetime] = None
    ) -> List[datetime]:
        """
        Get next N occurrences of cron expression

        Args:
            expression: Cron expression
            count: Number of occurrences to calculate
            start_time: Starting point (default: now)

        Returns:
            List of datetime objects
        """
        try:
            if start_time is None:
                start_time = datetime.now(timezone.utc)

            cron = croniter(expression, start_time)
            occurrences = []

            for _ in range(count):
                next_run = cron.get_next(datetime)
                occurrences.append(next_run)

            return occurrences

        except Exception as e:
            logger.error(f"Error calculating occurrences: {e}")
            return []

    @staticmethod
    def describe_cron(expression: str) -> str:
        """
        Generate human-readable description of cron expression

        Args:
            expression: Cron expression

        Returns:
            Human-readable description
        """
        try:
            # Parse cron parts: minute hour day month weekday
            parts = expression.split()

            if len(parts) != 5:
                return "Invalid cron expression"

            minute, hour, day, month, weekday = parts

            descriptions = []

            # Weekday description
            if weekday != '*':
                weekday_names = {
                    '0': 'Sunday', '1': 'Monday', '2': 'Tuesday',
                    '3': 'Wednesday', '4': 'Thursday', '5': 'Friday', '6': 'Saturday'
                }
                if '-' in weekday:
                    start, end = weekday.split('-')
                    descriptions.append(f"on {weekday_names.get(start, start)} to {weekday_names.get(end, end)}")
                elif ',' in weekday:
                    days = [weekday_names.get(d, d) for d in weekday.split(',')]
                    descriptions.append(f"on {', '.join(days)}")
                else:
                    descriptions.append(f"on {weekday_names.get(weekday, weekday)}")

            # Day of month description
            if day != '*':
                if ',' in day:
                    descriptions.append(f"on days {day} of the month")
                elif '-' in day:
                    descriptions.append(f"from day {day.split('-')[0]} to {day.split('-')[1]} of the month")
                else:
                    descriptions.append(f"on day {day} of the month")

            # Month description
            if month != '*':
                month_names = {
                    '1': 'January', '2': 'February', '3': 'March', '4': 'April',
                    '5': 'May', '6': 'June', '7': 'July', '8': 'August',
                    '9': 'September', '10': 'October', '11': 'November', '12': 'December'
                }
                if ',' in month:
                    months = [month_names.get(m, m) for m in month.split(',')]
                    descriptions.append(f"in {', '.join(months)}")
                else:
                    descriptions.append(f"in {month_names.get(month, month)}")

            # Hour description
            if hour != '*':
                if ',' in hour:
                    descriptions.append(f"at hours {hour}")
                elif '-' in hour:
                    descriptions.append(f"from hour {hour.split('-')[0]} to {hour.split('-')[1]}")
                elif '/' in hour:
                    _, interval = hour.split('/')
                    descriptions.append(f"every {interval} hours")
                else:
                    time_str = f"{hour}:{minute if minute != '*' else '00'}"
                    descriptions.append(f"at {time_str}")
            elif minute != '*':
                if '/' in minute:
                    _, interval = minute.split('/')
                    descriptions.append(f"every {interval} minutes")
                else:
                    descriptions.append(f"at minute {minute}")
            else:
                descriptions.append("every minute")

            return " ".join(descriptions).capitalize()

        except Exception as e:
            logger.error(f"Error describing cron: {e}")
            return f"Cron: {expression}"

    @staticmethod
    def get_common_patterns() -> dict:
        """
        Get common cron expression patterns

        Returns:
            Dictionary of pattern names and expressions
        """
        return {
            "every_minute": "* * * * *",
            "every_5_minutes": "*/5 * * * *",
            "every_15_minutes": "*/15 * * * *",
            "every_30_minutes": "*/30 * * * *",
            "every_hour": "0 * * * *",
            "every_2_hours": "0 */2 * * *",
            "every_6_hours": "0 */6 * * *",
            "every_12_hours": "0 */12 * * *",
            "daily_9am": "0 9 * * *",
            "daily_noon": "0 12 * * *",
            "daily_6pm": "0 18 * * *",
            "daily_midnight": "0 0 * * *",
            "weekdays_9am": "0 9 * * 1-5",
            "weekdays_6pm": "0 18 * * 1-5",
            "weekends_10am": "0 10 * * 0,6",
            "monday_9am": "0 9 * * 1",
            "friday_5pm": "0 17 * * 5",
            "first_of_month": "0 9 1 * *",
            "last_day_of_month": "0 9 28-31 * *",
            "weekly_sunday": "0 9 * * 0",
            "biweekly": "0 9 */14 * *",
            "quarterly": "0 9 1 */3 *",
        }


class CronScheduleCalculator:
    """Calculate next execution times for cron-based schedules"""

    @staticmethod
    def calculate_next_run(
        cron_expression: str,
        last_run: Optional[datetime] = None,
        timezone_offset: int = 0
    ) -> Optional[datetime]:
        """
        Calculate next run time for cron expression

        Args:
            cron_expression: Cron expression
            last_run: Last execution time (default: now)
            timezone_offset: Timezone offset in hours from UTC

        Returns:
            Next execution datetime or None if error
        """
        try:
            base_time = last_run if last_run else datetime.now(timezone.utc)

            # Apply timezone offset
            if timezone_offset != 0:
                base_time = base_time + timedelta(hours=timezone_offset)

            cron = croniter(cron_expression, base_time)
            next_run = cron.get_next(datetime)

            # Convert back to UTC
            if timezone_offset != 0:
                next_run = next_run - timedelta(hours=timezone_offset)

            return next_run

        except Exception as e:
            logger.error(f"Error calculating next run: {e}")
            return None

    @staticmethod
    def should_execute_now(
        cron_expression: str,
        last_run: Optional[datetime] = None,
        grace_period_seconds: int = 60
    ) -> bool:
        """
        Check if cron schedule should execute now

        Args:
            cron_expression: Cron expression
            last_run: Last execution time
            grace_period_seconds: Grace period for execution (default: 60s)

        Returns:
            True if should execute now
        """
        try:
            now = datetime.now(timezone.utc)
            next_run = CronScheduleCalculator.calculate_next_run(cron_expression, last_run)

            if next_run is None:
                return False

            # Check if next_run is within grace period of now
            time_diff = (now - next_run).total_seconds()

            # Should execute if:
            # 1. next_run is in the past or now
            # 2. Within grace period
            return -grace_period_seconds <= time_diff <= grace_period_seconds

        except Exception as e:
            logger.error(f"Error checking execution: {e}")
            return False

    @staticmethod
    def get_execution_windows(
        cron_expression: str,
        start_date: datetime,
        end_date: datetime,
        max_results: int = 100
    ) -> List[datetime]:
        """
        Get all execution windows between two dates

        Args:
            cron_expression: Cron expression
            start_date: Start date
            end_date: End date
            max_results: Maximum number of results

        Returns:
            List of execution times
        """
        try:
            cron = croniter(cron_expression, start_date)
            executions = []

            while len(executions) < max_results:
                next_run = cron.get_next(datetime)

                if next_run > end_date:
                    break

                executions.append(next_run)

            return executions

        except Exception as e:
            logger.error(f"Error getting execution windows: {e}")
            return []


# Predefined cron patterns with descriptions
CRON_PATTERNS = {
    "every_minute": {
        "expression": "* * * * *",
        "description": "Every minute",
        "category": "frequent"
    },
    "every_5_minutes": {
        "expression": "*/5 * * * *",
        "description": "Every 5 minutes",
        "category": "frequent"
    },
    "every_15_minutes": {
        "expression": "*/15 * * * *",
        "description": "Every 15 minutes",
        "category": "frequent"
    },
    "every_30_minutes": {
        "expression": "*/30 * * * *",
        "description": "Every 30 minutes",
        "category": "frequent"
    },
    "hourly": {
        "expression": "0 * * * *",
        "description": "Every hour at minute 0",
        "category": "hourly"
    },
    "every_2_hours": {
        "expression": "0 */2 * * *",
        "description": "Every 2 hours",
        "category": "hourly"
    },
    "every_6_hours": {
        "expression": "0 */6 * * *",
        "description": "Every 6 hours",
        "category": "hourly"
    },
    "daily_morning": {
        "expression": "0 9 * * *",
        "description": "Daily at 9:00 AM",
        "category": "daily"
    },
    "daily_noon": {
        "expression": "0 12 * * *",
        "description": "Daily at noon",
        "category": "daily"
    },
    "daily_evening": {
        "expression": "0 18 * * *",
        "description": "Daily at 6:00 PM",
        "category": "daily"
    },
    "daily_midnight": {
        "expression": "0 0 * * *",
        "description": "Daily at midnight",
        "category": "daily"
    },
    "weekdays_morning": {
        "expression": "0 9 * * 1-5",
        "description": "Weekdays at 9:00 AM",
        "category": "weekly"
    },
    "weekdays_evening": {
        "expression": "0 18 * * 1-5",
        "description": "Weekdays at 6:00 PM",
        "category": "weekly"
    },
    "weekend_morning": {
        "expression": "0 10 * * 0,6",
        "description": "Weekends at 10:00 AM",
        "category": "weekly"
    },
    "monday_morning": {
        "expression": "0 9 * * 1",
        "description": "Every Monday at 9:00 AM",
        "category": "weekly"
    },
    "friday_evening": {
        "expression": "0 17 * * 5",
        "description": "Every Friday at 5:00 PM",
        "category": "weekly"
    },
    "first_of_month": {
        "expression": "0 9 1 * *",
        "description": "First day of month at 9:00 AM",
        "category": "monthly"
    },
    "mid_month": {
        "expression": "0 9 15 * *",
        "description": "15th of month at 9:00 AM",
        "category": "monthly"
    },
    "quarterly": {
        "expression": "0 9 1 */3 *",
        "description": "Quarterly (every 3 months)",
        "category": "special"
    },
}

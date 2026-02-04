# Tasks

The `Task` class is a model that represents a scheduled job to be executed by the system's scheduler. It is based on the `apscheduler` library.

## Task Class

The `Task` defines a scheduled job.

### Fields

-   `name`: A unique name for the task.
-   `func`: The dotted path to the function to be executed.
-   `replace_existing`: A boolean that, if true, will replace an existing task with the same name.
-   `max_instances`: The maximum number of concurrent instances of this task.
-   `next_run_time`: The scheduled time for the next run.
-   `args`: A JSON list of positional arguments to pass to the function.
-   `kwargs`: A JSON object of keyword arguments to pass to the function.
-   `trigger`: The type of trigger. Currently, only `interval` is supported via the model, but `cron` is used internally.
-   `trigger_config`: A JSON object with the trigger-specific configuration.
-   `active`: A boolean to enable or disable the task.

## Triggers

### IntervalTrigger

The `IntervalTrigger` is used to run a task at fixed intervals.

**Accepted Fields:**

-   `weeks` (int): number of weeks to wait
-   `days` (int): number of days to wait
-   `hours` (int): number of hours to wait
-   `minutes` (int): number of minutes to wait
-   `seconds` (int): number of seconds to wait
-   `start_date` (datetime|str): starting point for the interval calculation
-  `end_date` (datetime|str): latest possible date/time to trigger on
-   `timezone` (datetime.tzinfo|str): time zone to use for the date/time calculations
-   `jitter` (int|None): advance or delay the job execution by ``jitter`` seconds at most.

### CronTrigger

The `CronTrigger` is used to run a task at specific times, similar to the classic cron scheduler.

**Accepted Fields:**

-   `year` (int|str): 4-digit year
-   `month` (int|str): month (1-12)
-   `day` (int|str): day of the (1-31)
-   `week` (int|str): ISO week (1-53)
-   `day_of_week` (int|str): number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
-   `hour` (int|str): hour (0-23)
-   `minute` (int|str): minute (0-59)
-   `second` (int|str): second (0-59)
-   `start_date` (datetime|str): earliest date/time to trigger on (inclusive)
-   `end_date` (datetime|str): latest date/time to trigger on (inclusive)
-   `timezone` (datetime.tzinfo|str): time zone to use for the date/time calculations
-   `jitter` (int|None): advance or delay the job execution by ``jitter`` seconds at most.

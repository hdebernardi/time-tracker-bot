# time-tracker-bot

This project is aim to track activity of a person on his laptop.

It saves all activities to a JSON file that you can use to run data analysis.

## Representation of an activity

* `name`: the name of that activity
* `duration`: the total duration of that activity
* `entries`: the time entries of that activity
    * `start_time`, expressed as *year-month-day hours:minutes:seconds*
    * `end_time`, expressed as *year-month-day hours:minutes:seconds*
    * `duration`, expressed in *seconds*
   
## Roadmap

- [ ] Use signals instead of active loops
- [ ] Data analytics
# uplan
Planning tool for University of Vienna's ufind, to filter out courses based on given time constraints.

This tools is a solution to a problem I have been facing for the last couple of years. Instead of painstakingly
figuring out which courses fit your schedule and don't overlap, you can use uplan.

uplan takes a configuration file in JSON format, where you tell your needs:

```
{
    "modules": [
        {
            "title": "Vertiefung Programmierung",
            "id": "317609",
            "priority": 10,
            "participants": 100
        },
        {
            "title": "LPS",
            "id": "321972",
            "priority": 10,
            "participants": 300
        },
        ...
    ],
    "unavailable_slots": [
        {
            "day": "Montag",
            "start": "08:00",
            "end": "12:00"
        },
        ...
    ],
    "priorities": [
        {
            "course_id": "051920",
            "group_name": "3"
        },
        ...
    ]
}
```

In `modules` you list all the modules you intend to take. Each module needs a `title`, the unique ID from ufind (which you can find in your browsers address bar), a `priority` that you assigned to it (best within 1-10 bounds) and an expected number of `participants`. At some point probably know how many people are typically interested in a course and can provide an approximate number here. Exactness is not important, as we need it only for weight calculation later on.

In `unavailable_slots` you specify any time slots that you cannot spend studying, because, for example, you have to actually earn a living, or some other minor inconvenience.

In `priorities` you can specify specific courses that you know you want to take. Putting your `course_id` (which you also can find in ufind) here does not guarantee the course actually showing up in your schedule, but makes it more likely.

## Usage

`python uplan.py <PATH TO YOUR JSON> <ANY COURSES YOU WANT TO TAKE>`

uplan runs in the terminal and directly outputs its generated schedules.s

To make sure that some course really shows up in your planning, you can specify it when calling the program by appending it after your path to the JSON file:

`python uplan.py 2025S.json 051920 180077 > plan.txt`

This will make sure that any generated schedules that lack `051920` or `180077` are skipped.

### Data Generation

In order to generate your possible schedules, uplan needs to read all possible courses for your modules. This takes a while
and is currently prone to timeouts. If this is the case, you either need to run uplan again or supply the necessary data yourself.

uplan refreshes its data every 2 days, in order to operate with the latest information from ufind.
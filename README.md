# uplan
Planning tool for University of Vienna's ufind, to filter out courses based on given time constraints.

This tools is a solution to a problem I have been facing for the last couple of years. Instead of painstakingly
figuring out which courses fit your schedule and don't overlap, you can now use uplan.

uplan takes a configuration file in JSON format, where you write down your needs:

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

In `modules` you list all the modules you intend to take. Each module needs a `title` (which is only a helper for you to remember what module you wrote down here), the unique ID from ufind (which you can find in your browsers address bar), a `priority` that you assigned to it (best within 1-10 bounds) and an expected number of `participants`. At some point probably know how many people are typically interested in a course and can provide an approximate number here. Exactness is not important, as we need it only for weight calculation later on.

In `unavailable_slots` you specify any time slots that you cannot spend studying, because, for example, you have to actually earn a living, or some other minor inconvenience.

In `priorities` you can specify specific courses that you know you want to take. Putting your `course_id` (which you also can find in ufind) here does not guarantee the course actually showing up in your schedule, but makes it more likely.

## Usage

`python uplan.py <PATH TO YOUR JSON> <MAX NUMBER OF COURSES> <ANY COURSES YOU WANT TO TAKE>`

uplan runs in the terminal and directly outputs its generated schedules.

To make sure that some course really shows up in your planning, you can specify it when calling the program by appending it after your path to the JSON file:

`python uplan.py 2025S.json 051920 180077 > plan.txt`

This will make sure that any generated schedules that lack `051920` or `180077` are skipped.

You can also specify courses that you don't want to take, by adding a `-` in front of it: `-180077` excludes the course `180077`.

### Data Generation

In order to generate your possible schedules, uplan needs to read all possible courses for your modules. This takes a while
and is currently prone to timeouts. If this is the case, you either need to run uplan again or supply the necessary data yourself.

uplan refreshes its data every 2 days, in order to operate with the latest information from ufind.

## Rooms

uplan retrieves and stores the location of the courses and uses this information to calculate the time needed to travel
between two locations. By modifying `rooms.py` you can add rooms as you need them (they need to be within the location as specified on ufind), or
modify the time you think you need for travel, as these are only my approximations :-)

For performance reasons, the rooms are stored in alphabetical order and only show the travel cost to themselves and those rooms that
come after them, in alphabetical order. Therefore, when adding a new room "Spengergasse" (for example), you would need to place the node after "Sensengasse"
and add the travel costs at the rooms above your newly inserted room (e.g. in "Baden", "Ettenreichgasse" etc.)

weekday_map = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag" ]

class TextExporter:
    _template = ""

    def export_schedules(self, schedules):
        output = ""

        for idx in range(len(schedules)):
            text = self._export_schedule(schedules[idx], idx)
            output += text + "\n\n"

        return output

    def _export_schedule(self, schedule, number):
        text = "Schedule #" + str(number + 1) + "\n"
        text += "ECTS = " + str(schedule.ects()) + "\n"
        text += "Probability = " + str(schedule.total_chance() * 100.0) + " %\n\n\n"
        
        days = []
        for day in weekday_map:
            days.append(["________ " + day + " ________"])

        max_depth = 1
        for event in schedule.events():
            event_weekday_idx = weekday_map.index(event.day())

            max_length_of_slot = len(days[event_weekday_idx][0])

            for idx in range(0, len(event.title()), max_length_of_slot):
                part_of_title = event.title()[idx:idx + max_length_of_slot]
                part_of_title += " " * (max_length_of_slot - len(part_of_title))

                days[event_weekday_idx].append(part_of_title)

            event_id = "[" + event.id() + "]"
            event_id += " " * (max_length_of_slot - len(event_id))

            days[event_weekday_idx].append(event_id)

            date_format = event.date_format()
            date_format += " " * (max_length_of_slot - len(date_format))

            days[event_weekday_idx].append(date_format)

            max_depth = max(max_depth, len(days[event_weekday_idx]))

        max_line_length = 0

        for idx in range(max_depth):
            line = ""

            for day in days:
                if len(day) > idx:
                    line += day[idx] + "\t\t"
                else:
                    line += " " * len(day[0]) + "\t\t"
            
            max_line_length = max(max_line_length, len(line))

            text += line + "\n"

        return text
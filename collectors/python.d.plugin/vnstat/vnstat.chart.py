# -*- coding: utf-8 -*-
# Description: vnstat netdata python.d module
# Author: Noah Troy    (NoahTroy)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
from calendar import monthrange

from bases.FrameworkServices.ExecutableService import ExecutableService

VNSTAT_BASE_COMMAND = "vnstat --json"

ORDER = [
    "now_vs_day_def",
    "hours_average_def",
    "hours_total_def",
    "days_average_def",
    "days_total_def",
    "months_average_def",
    "months_total_def",
    "years_average_def",
    "years_total_def",
    "totals_def",
]

DYNAMIC_CHARTS = {
    "now_vs_day_def": {
        "options": [
            None,
            "Current vs. Yesterday",
            "kilobits/s",
            "average data rate",
            "vnstat.now_vs_day_def",
            "stacked",
        ],
        "lines": [
            ["now_vs_day_def_current", "now", "absolute", 1, 1],
            ["now_vs_day_def_yesterday", "yesterday", "absolute", 1, 1],
        ],
    },
    "hours_average_def": {
        "options": [
            None,
            "Average Data Transfer Rate Per Hour",
            "kilobits/s",
            "hourly data rate",
            "vnstat.hours_average_def",
            "stacked",
        ],
        "lines": [["hours_average_def_hour1", "hour1", "absolute", 1, 1]],
    },
    "hours_total_def": {
        "options": [
            None,
            "Total Data Transfer Per Hour",
            "B",
            "hourly transfer",
            "vnstat.hours_total_def",
            "stacked",
        ],
        "lines": [["hours_total_def_hour1", "hour1", "absolute", 1, 1]],
    },
    "days_average_def": {
        "options": [
            None,
            "Average Data Transfer Rate Per Day",
            "kilobits/s",
            "daily data rate",
            "vnstat.days_average_def",
            "stacked",
        ],
        "lines": [["days_average_def_day1", "day1", "absolute", 1, 1]],
    },
    "days_total_def": {
        "options": [
            None,
            "Total Data Transfer Per Day",
            "B",
            "daily transfer",
            "vnstat.days_total_def",
            "stacked",
        ],
        "lines": [["days_total_def_day1", "day1", "absolute", 1, 1]],
    },
    "months_average_def": {
        "options": [
            None,
            "Average Data Transfer Rate Per Month",
            "kilobits/s",
            "monthly data rate",
            "vnstat.months_average_def",
            "stacked",
        ],
        "lines": [["months_average_def_month1", "month1", "absolute", 1, 1]],
    },
    "months_total_def": {
        "options": [
            None,
            "Total Data Transfer Per Month",
            "B",
            "monthly transfer",
            "vnstat.months_total_def",
            "stacked",
        ],
        "lines": [["months_total_def_month1", "month1", "absolute", 1, 1]],
    },
    "years_average_def": {
        "options": [
            None,
            "Average Data Transfer Rate Per Year",
            "kilobits/s",
            "yearly data rate",
            "vnstat.years_average_def",
            "stacked",
        ],
        "lines": [["years_average_def_year1", "year1", "absolute", 1, 1]],
    },
    "years_total_def": {
        "options": [
            None,
            "Total Data Transfer Per Year",
            "B",
            "yearly transfer",
            "vnstat.years_total_def",
            "stacked",
        ],
        "lines": [["years_total_def_year1", "year1", "absolute", 1, 1]],
    },
    "totals_def": {
        "options": [
            None,
            "Total RX vs. Total TX",
            "B",
            "total transfer",
            "vnstat.totals_def",
            "stacked",
        ],
        "lines": [
            ["totals_def_rx", "rx", "absolute", 1, 1],
            ["totals_def_tx", "tx", "absolute", 1, 1],
        ],
    },
}


class Service(ExecutableService):
    def __init__(self, configuration=None, name=None):
        ExecutableService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = DYNAMIC_CHARTS
        self.command = VNSTAT_BASE_COMMAND

    def generate_charts_and_values(self, interfaces, data_points):
        charts = {}
        order = []
        data = dict()

        try:
            hours_limit = int(self.configuration.get("hours_limit", 0))
            days_limit = int(self.configuration.get("days_limit", 0))
            months_limit = int(self.configuration.get("months_limit", 0))
            years_limit = int(self.configuration.get("years_limit", 0))
        except Exception as msg:
            self.debug(str(msg))
            self.debug(
                'You are most-likely seeing the above message because "hours_limit", "days_limit", "months_limit", or'
                + '"years_limit" contained invalid (non-integer) entries. The default values will be used instead...'
            )
            hours_limit = 0
            days_limit = 0
            months_limit = 0
            years_limit = 0

        try:
            data_representation = int(self.configuration.get("data_representation", 1))
            if not (
                (data_representation == 0)
                or ((data_representation == 1) or (data_representation == 2))
            ):
                data_representation = 1
        except Exception as msg:
            self.debug(str(msg))
            self.debug(
                'You are most-likely seeing the above message because "data_representation"'
                + 'contains an invalid (non-integer) entry. The default value will be used instead...'
            )
            data_representation = 1

        try:
            charts_enabled = int(self.configuration.get("enable_charts", 0))
            if not ((charts_enabled == 1) and (len(interfaces) == 1)):
                charts_enabled = 0
        except Exception as msg:
            self.debug(str(msg))
            self.debug(
                'You are most-likely seeing the above message because "enable_charts"'
                + 'contains an invalid (non-integer) entry. The default value will be used instead...'
            )
            charts_enabled = 0

        index = 0
        for interface in interfaces:

            interface_or_chart = interface
            if charts_enabled == 1:
                interface_or_chart = "chart"

            charts[("now_vs_day_" + interface_or_chart)] = {
                "options": [
                    None,
                    "Current vs. Yesterday",
                    "kilobits/s",
                    ("average data rate " + interface),
                    ("vnstat.now_vs_day_" + interface_or_chart),
                    "stacked",
                ],
                "lines": [
                    [
                        ("now_vs_day_" + interface + "_current"),
                        "current",
                        "absolute",
                        1,
                        1,
                    ],
                    [
                        ("now_vs_day_" + interface + "_yesterday"),
                        "yesterday",
                        "absolute",
                        1,
                        1,
                    ],
                ],
            }

            order.append(("now_vs_day_" + interface_or_chart))

            data[("now_vs_day_" + interface + "_current")] = data_points[index][2]
            data[("now_vs_day_" + interface + "_yesterday")] = data_points[index][3]

            if hours_limit != 0:
                if (data_representation == 0) or (data_representation == 2):
                    charts[("hours_average_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Average Data Transfer Rate Per Hour",
                            "kilobits/s",
                            ("hourly data rate " + interface),
                            ("vnstat.hours_average_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("hours_average_" + interface_or_chart))

                if (data_representation == 0) or (data_representation == 1):
                    charts[("hours_total_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Total Data Transfer Per Hour",
                            "B",
                            ("hourly transfer " + interface),
                            ("vnstat.hours_total_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("hours_total_" + interface_or_chart))

                start_at = len(data_points[index][4]) - hours_limit
                if (hours_limit == -1) or (start_at < 0):
                    start_at = 0
                for hour in data_points[index][4][start_at:]:
                    if (data_representation == 0) or (data_representation == 2):
                        total_amount = hour[1]
                        average_amount = ((total_amount * 8) / 1000) / 3600
                        new_line = [
                            (
                                "hours_average_"
                                + interface
                                + "_hour"
                                + str(hash(hour[0]))[1:]
                            ),
                            hour[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("hours_average_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("hours_average_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "hours_average_"
                                + interface
                                + "_hour"
                                + str(hash(hour[0]))[1:]
                            )
                        ] = average_amount

                    if (data_representation == 0) or (data_representation == 1):
                        new_line = [
                            (
                                "hours_total_"
                                + interface
                                + "_hour"
                                + str(hash(hour[0]))[1:]
                            ),
                            hour[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("hours_total_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("hours_total_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "hours_total_"
                                + interface
                                + "_hour"
                                + str(hash(hour[0]))[1:]
                            )
                        ] = hour[1]

            if days_limit != 0:
                if (data_representation == 0) or (data_representation == 2):
                    charts[("days_average_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Average Data Transfer Rate Per Day",
                            "kilobits/s",
                            ("daily data rate " + interface),
                            ("vnstat.days_average_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("days_average_" + interface_or_chart))

                if (data_representation == 0) or (data_representation == 1):
                    charts[("days_total_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Total Data Transfer Per Day",
                            "B",
                            ("daily transfer " + interface),
                            ("vnstat.days_total_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("days_total_" + interface_or_chart))

                start_at = len(data_points[index][5]) - days_limit
                if (days_limit == -1) or (start_at < 0):
                    start_at = 0
                for day in data_points[index][5][start_at:]:
                    if (data_representation == 0) or (data_representation == 2):
                        total_amount = day[1]
                        average_amount = ((total_amount * 8) / 1000) / 86400
                        new_line = [
                            (
                                "days_average_"
                                + interface
                                + "_day"
                                + str(hash(day[0]))[1:]
                            ),
                            day[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("days_average_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("days_average_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "days_average_"
                                + interface
                                + "_day"
                                + str(hash(day[0]))[1:]
                            )
                        ] = average_amount

                    if (data_representation == 0) or (data_representation == 1):
                        new_line = [
                            (
                                "days_total_"
                                + interface
                                + "_day"
                                + str(hash(day[0]))[1:]
                            ),
                            day[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("days_total_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("days_total_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            ("days_total_" + interface + "_day" + str(hash(day[0]))[1:])
                        ] = day[1]

            if months_limit != 0:
                if (data_representation == 0) or (data_representation == 2):
                    charts[("months_average_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Average Data Transfer Rate Per Month",
                            "kilobits/s",
                            ("monthly data rate " + interface),
                            ("vnstat.months_average_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("months_average_" + interface_or_chart))

                if (data_representation == 0) or (data_representation == 1):
                    charts[("months_total_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Total Data Transfer Per Month",
                            "B",
                            ("monthly transfer " + interface),
                            ("vnstat.months_total_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("months_total_" + interface_or_chart))

                start_at = len(data_points[index][6]) - months_limit
                if (months_limit == -1) or (start_at < 0):
                    start_at = 0
                for month in data_points[index][6][start_at:]:
                    if (data_representation == 0) or (data_representation == 2):
                        total_amount = month[1]
                        number_of_days = monthrange(
                            int(month[0].split("/")[1]), int(month[0].split("/")[0])
                        )[1]
                        average_amount = ((total_amount * 8) / 1000) / (
                            number_of_days * 86400
                        )
                        new_line = [
                            (
                                "months_average_"
                                + interface
                                + "_month"
                                + str(hash(month[0]))[1:]
                            ),
                            month[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("months_average_" + interface_or_chart)][
                            "lines"
                        ].append(new_line)

                        try:
                            self.charts[
                                ("months_average_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "months_average_"
                                + interface
                                + "_month"
                                + str(hash(month[0]))[1:]
                            )
                        ] = average_amount

                    if (data_representation == 0) or (data_representation == 1):
                        new_line = [
                            (
                                "months_total_"
                                + interface
                                + "_month"
                                + str(hash(month[0]))[1:]
                            ),
                            month[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("months_total_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("months_total_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "months_total_"
                                + interface
                                + "_month"
                                + str(hash(month[0]))[1:]
                            )
                        ] = month[1]

            if years_limit != 0:
                if (data_representation == 0) or (data_representation == 2):
                    charts[("years_average_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Average Data Transfer Rate Per Year",
                            "kilobits/s",
                            ("yearly data rate " + interface),
                            ("vnstat.years_average_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("years_average_" + interface_or_chart))

                if (data_representation == 0) or (data_representation == 1):
                    charts[("years_total_" + interface_or_chart)] = {
                        "options": [
                            None,
                            "Total Data Transfer Per Year",
                            "B",
                            ("yearly transfer " + interface),
                            ("vnstat.years_total_" + interface_or_chart),
                            "stacked",
                        ],
                        "lines": [],
                    }

                    order.append(("years_total_" + interface_or_chart))

                start_at = len(data_points[index][7]) - years_limit
                if (years_limit == -1) or (start_at < 0):
                    start_at = 0
                for year in data_points[index][7][start_at:]:
                    if (data_representation == 0) or (data_representation == 2):
                        total_amount = year[1]
                        number_of_days = 365
                        if monthrange(int(year[0]), 2)[1] == 29:
                            number_of_days = 366
                        average_amount = ((total_amount * 8) / 1000) / (
                            number_of_days * 86400
                        )
                        new_line = [
                            (
                                "years_average_"
                                + interface
                                + "_year"
                                + str(hash(year[0]))[1:]
                            ),
                            year[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("years_average_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("years_average_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "years_average_"
                                + interface
                                + "_year"
                                + str(hash(year[0]))[1:]
                            )
                        ] = average_amount

                    if (data_representation == 0) or (data_representation == 1):
                        new_line = [
                            (
                                "years_total_"
                                + interface
                                + "_year"
                                + str(hash(year[0]))[1:]
                            ),
                            year[0],
                            "absolute",
                            1,
                            1,
                        ]
                        charts[("years_total_" + interface_or_chart)]["lines"].append(
                            new_line
                        )

                        try:
                            self.charts[
                                ("years_total_" + interface_or_chart)
                            ].add_dimension(new_line)
                        except Exception as msg:
                            # This value either already exists or the chart has not been instantiated yet
                            self.debug(str(msg))

                        data[
                            (
                                "years_total_"
                                + interface
                                + "_year"
                                + str(hash(year[0]))[1:]
                            )
                        ] = year[1]

            charts[("totals_" + interface_or_chart)] = {
                "options": [
                    None,
                    "Total RX vs. Total TX",
                    "B",
                    ("total bandwidth " + interface),
                    ("vnstat.totals_" + interface_or_chart),
                    "stacked",
                ],
                "lines": [
                    [("totals_" + interface + "_rx"), "rx", "absolute", 1, 1],
                    [("totals_" + interface + "_tx"), "tx", "absolute", 1, 1],
                ],
            }

            order.append(("totals_" + interface_or_chart))

            data[("totals_" + interface + "_rx")] = data_points[index][0]
            data[("totals_" + interface + "_tx")] = data_points[index][1]

            index += 1

        return charts, order, data

    def _get_data(self):
        """
        Parse vnstat command output
        :return: dict
        """

        try:
            raw_output = str(self._get_raw_data()[0]).strip()
            output = json.loads(raw_output)

            allowed_interfaces = self.configuration.get("interface", "all").split()

            interfaces = []
            data_points = []
            for interface in output["interfaces"]:
                if (not ("all" in allowed_interfaces)) and (
                    not (interface["name"] in allowed_interfaces)
                ):
                    continue

                interfaces.append(interface["name"])

                traffic = interface["traffic"]

                total_rx = traffic["total"]["rx"]
                total_tx = traffic["total"]["tx"]

                current_amount = (
                    traffic["fiveminute"][(len(traffic["fiveminute"]) - 1)]["rx"]
                    + traffic["fiveminute"][(len(traffic["fiveminute"]) - 1)]["tx"]
                )
                current_data_rate = ((current_amount * 8) / 1000) / 300
                # If no data is present for yesterday, then today's values will be chosen automatically:
                yesterdayAmount = (
                    traffic["day"][(len(traffic["day"]) - 2)]["rx"]
                    + traffic["day"][(len(traffic["day"]) - 2)]["tx"]
                )
                yesterday_data_rate = ((yesterdayAmount * 8) / 1000) / 86400

                hours_total_data = []
                for hour in traffic["hour"]:
                    date = (
                        str(hour["date"]["day"])
                        + "/"
                        + str(hour["date"]["month"])
                        + "/"
                        + str(hour["date"]["year"])
                    )
                    minute = str(hour["time"]["minute"])
                    if len(minute) == 1:
                        minute = "0" + minute
                    time = str(hour["time"]["hour"]) + ":" + minute
                    hour_total = hour["rx"] + hour["tx"]
                    hours_total_data.append([(time + " " + date), hour_total])

                days_total_data = []
                for day in traffic["day"]:
                    date = (
                        str(day["date"]["day"])
                        + "/"
                        + str(day["date"]["month"])
                        + "/"
                        + str(day["date"]["year"])
                    )
                    day_total = day["rx"] + day["tx"]
                    days_total_data.append([date, day_total])

                months_total_data = []
                for month in traffic["month"]:
                    date = (
                        str(month["date"]["month"]) + "/" + str(month["date"]["year"])
                    )
                    month_total = month["rx"] + month["tx"]
                    months_total_data.append([date, month_total])

                years_total_data = []
                for year in traffic["year"]:
                    date = str(year["date"]["year"])
                    year_total = year["rx"] + year["tx"]
                    years_total_data.append([date, year_total])

                this_interface_data = [
                    total_rx,
                    total_tx,
                    current_data_rate,
                    yesterday_data_rate,
                    hours_total_data,
                    days_total_data,
                    months_total_data,
                    years_total_data,
                ]

                data_points.append(this_interface_data)

            self.definitions, self.order, data = self.generate_charts_and_values(
                interfaces, data_points
            )

            return data

        except Exception as msg:
            self.error(str(msg))
            return None

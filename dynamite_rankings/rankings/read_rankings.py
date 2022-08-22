# DynamiteRankings: An open-source NCAA football ranking and prediction program.
# Copyright (C) 2019  Bryan VanDuinen and Arthur Rajala

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Add the root package directory to path for importing
# This is so user does not need to run setup.py or modify PYTHONPATH
from os.path import dirname, join, realpath
import sys
root = dirname(dirname(realpath(__file__)))
sys.path.append(root)
sys.path.append(join(dirname(root), "TheKickIsBAD"))

# Standard imports
import json
import sys
import the_kick_is_bad
from the_kick_is_bad import utils


def read_rankings(year, week):

    # Open rankings file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/{year}/team_rankings-{year}-{week:02}.csv"
    with open(filename) as file:

        rankings = {}

        # Remove the header line
        _ = file.readline().strip()

        # Loop through lines to read ranking data
        ranking_line = file.readline().strip()
        while ranking_line:

            # Split the ranking data
            ranking = ranking_line.split(",")
            team = ranking[0]
            rank = ranking[1]
            previous_rank = ranking[2]
            delta_rank = ranking[3]
            team_score = ranking[4]
            strength = ranking[5]
            standard_deviation = ranking[6]

            # Pack ranking structure
            rankings[team] = {
                "rank": int(rank),
                "previous rank": int(previous_rank),
                "delta rank": int(delta_rank),
                "team score": float(team_score),
                "strength": float(strength),
                "standard deviation": float(standard_deviation)
            }

            ranking_line = file.readline().strip()

        return rankings


if __name__ == "__main__":
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != "bowl":
        week = int(week)
    rankings = read_rankings(year, week)
    rankings_string = json.dumps(rankings, indent=2)
    print(rankings_string)

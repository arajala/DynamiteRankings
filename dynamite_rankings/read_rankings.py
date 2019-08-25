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

import json
import os
import sys

from read_number_of_weeks import read_number_of_weeks


def read_rankings(year, week):

    # Check if the week is 'bowl' week
    num_weeks = read_number_of_weeks(year)
    if type(week) is str:
        week = num_weeks + 1
    elif week > num_weeks:
        raise Exception('Value of week should not exceed {0}. Did you mean "bowl"?'.format(num_weeks))

    # Open rankings file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}\\rankings\\{1}\\team_rankings-{1}-{2:02}.csv'.format(absolute_path, year, week)
    with open(filename) as file:

        rankings = {}

        # Remove the header line
        _ = file.readline().strip()

        # Loop through lines to read ranking data
        ranking_line = file.readline().strip()
        while ranking_line:

            # Split the ranking data
            ranking = ranking_line.split(',')
            team = ranking[0]
            rank = ranking[1]
            previous_rank = ranking[2]
            delta_rank = ranking[3]
            team_score = ranking[4]
            strength = ranking[5]
            standard_deviation = ranking[6]

            # Pack ranking structure
            rankings[team] = {
                'rank': int(rank),
                'previous rank': int(previous_rank),
                'delta rank': int(delta_rank),
                'team score': float(team_score),
                'strength': float(strength),
                'standard deviation': float(standard_deviation)
            }

            ranking_line = file.readline().strip()

        return rankings

if __name__ == '__main__':
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != 'bowl':
        week = int(week)
    rankings = read_rankings(year, week)
    rankings_string = json.dumps(rankings, indent=2)
    print(rankings_string)

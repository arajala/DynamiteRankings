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


def read_model(year, week):

    # Check if the week is 'bowl' week
    num_weeks = read_number_of_weeks(year)
    if type(week) is str:
        week = num_weeks + 1
    elif week > num_weeks:
        raise Exception('Value of week should not exceed {0}. Did you mean "bowl"?'.format(num_weeks))

    # Open model file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}\\models\\{1}\\model-{1}-{2:02}.csv'.format(absolute_path, year, week)
    with open(filename) as file:

        model = {}

        # Remove the header line
        _ = file.readline().strip()

        # Loop through lines to read model data
        model_line = file.readline().strip()
        while model_line:

            # Split the model data
            model_data = model_line.split(',')
            team = model_data[0]
            strength = model_data[1]
            standard_deviation = model_data[2]
            points_margin = model_data[3]
            average_opponent_strength = model_data[4]
            rushing_yards_margin = model_data[5]
            home_field_correction = model_data[6]
            games_played = model_data[7]

            # Pack ranking structure
            model[team] = {
                'strength': float(strength),
                'standard deviation': float(standard_deviation),
                'points margin': float(points_margin),
                'average opponent strength': float(average_opponent_strength),
                'rushing yards margin': float(rushing_yards_margin),
                'home field correction': float(home_field_correction),
                'games played': int(games_played)
            }

            model_line = file.readline().strip()

        return model

if __name__ == '__main__':
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != 'bowl':
        week = int(week)
    model = read_model(year, week)
    model_string = json.dumps(model, indent=2)
    print(model_string)

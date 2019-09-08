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


def read_predictions(year, week):

    # Check if the week is 'bowl' week
    num_weeks = read_number_of_weeks(year)
    if type(week) is str:
        week = num_weeks + 1
    elif week > num_weeks:
        raise Exception('Value of week should not exceed {0}. Did you mean "bowl"?'.format(num_weeks))

    # Open predictions file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}/predictions/{1}/predictions-{1}-{2:02}.csv'.format(absolute_path, year, week)
    with open(filename) as file:

        predictions = []

        # Remove the header line
        _ = file.readline().strip()

        # Loop through lines to read prediction data
        prediction_line = file.readline().strip()
        while prediction_line:

            # Split the prediction data
            prediction = prediction_line.split(',')
            away_team = prediction[0]
            home_team = prediction[1]
            predicted_winner = prediction[2]
            predicted_margin_of_victory = prediction[3]
            game_interest = prediction[4]

            # Pack prediction structure
            predictions.append({
                'away team': away_team,
                'home team': home_team,
                'predicted winner': predicted_winner,
                'predicted margin of victory': float(predicted_margin_of_victory),
                'game interest': float(game_interest)
            })

            prediction_line = file.readline().strip()

        return predictions

if __name__ == '__main__':
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != 'bowl':
        week = int(week)
    predictions = read_predictions(year, week)
    predictions_string = json.dumps(predictions, indent=2)
    print(predictions_string)

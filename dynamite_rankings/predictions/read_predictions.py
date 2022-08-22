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


def read_predictions(year, week):

    # Open predictions file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/{year}/predictions-{year}-{week:02}.csv"
    with open(filename) as file:

        predictions = []

        # Remove the header line
        _ = file.readline().strip()

        # Loop through lines to read prediction data
        prediction_line = file.readline().strip()
        while prediction_line:

            # Split the prediction data
            prediction = prediction_line.split(",")
            away_team = prediction[0]
            home_team = prediction[1]
            predicted_winner = prediction[2]
            predicted_margin_of_victory = prediction[3]
            game_interest = prediction[4]

            # Pack prediction structure
            predictions.append({
                "away team": away_team,
                "home team": home_team,
                "predicted winner": predicted_winner,
                "predicted margin of victory": float(predicted_margin_of_victory),
                "game interest": float(game_interest)
            })

            prediction_line = file.readline().strip()

        return predictions


if __name__ == "__main__":
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != "bowl":
        week = int(week)
    predictions = read_predictions(year, week)
    predictions_string = json.dumps(predictions, indent=2)
    print(predictions_string)

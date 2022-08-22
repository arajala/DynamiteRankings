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

import json
import sys
from the_kick_is_bad import utils


def read_model(year, week):

    # Open model file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/{year}/model-{year}-{week:02}.csv"
    with open(filename) as file:

        model = {}

        # Remove the header line
        _ = file.readline().strip()

        # Loop through lines to read model data
        model_line = file.readline().strip()
        while model_line:

            # Split the model data
            model_data = model_line.split(",")
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
                "strength": float(strength),
                "standard deviation": float(standard_deviation),
                "points margin": float(points_margin),
                "average opponent strength": float(average_opponent_strength),
                "rushing yards margin": float(rushing_yards_margin),
                "home field correction": float(home_field_correction),
                "games played": int(games_played)
            }

            model_line = file.readline().strip()

        return model


if __name__ == "__main__":
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != "bowl":
        week = int(week)
    model = read_model(year, week)
    model_string = json.dumps(model, indent=2)
    print(model_string)

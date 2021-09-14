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
sys.path.append(join(root, "TheKickIsBAD"))

# Standard imports
import json
import the_kick_is_bad
from the_kick_is_bad import utils
from urllib.request import urlopen

# DynamiteRankings imports
from rankings.read_rankings import read_rankings


def predict(year, week):

    scores = the_kick_is_bad.read_scores(year, week)

    rankings = read_rankings(year, week - 1)

    # Check if the week is 'bowl' week
    num_weeks = the_kick_is_bad.read_number_of_weeks(year)
    week, _ = utils.check_week(week, num_weeks)

    # Loop through scores to make predictions
    predictions = []
    for game in scores["games"]:

        # Get the team names
        away_team = game["game"]["away"]["names"]["standard"]
        home_team = game["game"]["home"]["names"]["standard"]

        # Determine home field advantage
        # Assume all bowl games are neutral site
        if week <= num_weeks:
            home_field_advantage = 4
        else:
            home_field_advantage = 0

        # Get away team strength
        away_team_strength = rankings[away_team]["strength"]

        # Get home team strength and add home field advantage
        home_team_strength = rankings[home_team]["strength"] + home_field_advantage

        # Pick the winner based on team strength
        if home_team_strength >= away_team_strength:
            predicted_winner = home_team
            predicted_margin_of_victory = home_team_strength - away_team_strength
        else:
            predicted_winner = away_team
            predicted_margin_of_victory = away_team_strength - home_team_strength

        # Calculate the game interest score
        game_interest = rankings[away_team]["team score"] + rankings[home_team]["team score"] - predicted_margin_of_victory

        # Pack predictions
        predictions.append({
            "away team": away_team,
            "home team": home_team,
            "predicted winner": predicted_winner,
            "predicted margin of victory": predicted_margin_of_victory,
            "game interest": game_interest
        })
    
    # Sort predictions by game interest
    predictions = sorted(predictions, key=lambda p: p["game interest"], reverse=True)

    # Print predictions
    predictions_file_string = "AwayTeam,HomeTeam,PredictedWinner,PredictedMoV,GameInterest\n"
    for prediction in predictions:

        # Print to console in pretty format
        print("{0} @ {1}: Predicted Winner: {2}, Predicted MoV: {3:.1f}, Game Interest: {4:.1f}".format(prediction["away team"],
                                                                                                        prediction["home team"],
                                                                                                        prediction["predicted winner"],
                                                                                                        prediction["predicted margin of victory"],
                                                                                                        prediction["game interest"]))

        # Print to file string in csv format
        predictions_file_string += "{0},{1},{2},{3:.1f},{4:.1f}\n".format(prediction["away team"],
                                                                          prediction["home team"],
                                                                          prediction["predicted winner"],
                                                                          prediction["predicted margin of victory"],
                                                                          prediction["game interest"])
        
    # Create the predictions file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/predictions/{year}/predictions-{year}-{week:02}.csv"
    utils.write_string(predictions_file_string, filename)


if __name__ == "__main__":
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != "bowl":
        week = int(week)
    predict(year, week)

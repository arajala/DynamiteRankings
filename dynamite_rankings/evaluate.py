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

import os
import sys

from read_predictions import read_predictions
from read_scores import read_scores


def evaluate(year, week):

    predictions = read_predictions(year, week)

    scores = read_scores(year, week)

    # Loop through predictions to check results
    results = []
    for prediction in predictions:
        away_team = prediction['away team']
        home_team = prediction['home team']
        predicted_winner = prediction['predicted winner']
        predicted_margin_of_victory = prediction['predicted margin of victory']

        # Loop through all scores to find the matching (completed) game
        for game in scores['games']:
            if game['game']['gameState'] != 'final':
                continue
            
            # Check if this is the same game by comparing team names
            if game['game']['away']['names']['standard'] == away_team and game['game']['home']['names']['standard'] == home_team:
                away_score = int(game['game']['away']['score'])
                home_score = int(game['game']['home']['score'])

                # Get the actual results
                if away_score > home_score:
                    actual_winner = away_team
                elif home_score > away_score:
                    actual_winner = home_team
                else:
                    actual_winner = 'TIE'
                actual_margin_of_victory = abs(away_score - home_score)
                
                # Save the results data
                results.append({
                    'away team': away_team,
                    'home team': home_team,
                    'predicted winner': predicted_winner,
                    'actual winner': actual_winner,
                    'predicted margin of victory': predicted_margin_of_victory,
                    'actual margin of victory': actual_margin_of_victory
                })
                break

    # Print results
    num_results = len(results)
    num_correct = 0
    results_file_string = 'AwayTeam,HomeTeam,PredictedWinner,Result,PredictedMoV,ActualMoV\n'
    for result in results:

        # Determine if prediction was correct
        if result['predicted winner'] == result['actual winner']:
            result_string = 'RIGHT'
            num_correct += 1
        else:
            result_string = 'WRONG'
            result['actual margin of victory'] *= -1

        # Print to file string in csv format
        results_file_string += '{0},{1},{2},{3},{4:.1f},{5}\n'.format(
            result['away team'], result['home team'], result['predicted winner'], result_string, result['predicted margin of victory'], result['actual margin of victory'])

        # Print to console strin in pretty format
        if result['predicted winner'] == result['home team']:
            predicted_loser = result['away team']
        else:
            predicted_loser = result['home team']
        results_console_string = '{0}: Predicted {1} over {2} by {3:.1f} (actual: {4})'.format(
            result_string, result['predicted winner'], predicted_loser, result['predicted margin of victory'], result['actual margin of victory'])
        print(results_console_string)

    # Print statistics to console
    print('({0}/{1}) {2:.1f}%'.format(num_correct, num_results, num_correct / num_results * 100))

    # Create the results file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}/predictions/{1}/results-{1}-{2:02}.csv'.format(absolute_path, year, week)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(results_file_string)
    
if __name__ == '__main__':
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != 'bowl':
        week = int(week)
    evaluate(year, week)

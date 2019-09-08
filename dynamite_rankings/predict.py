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
import time
from urllib.request import urlopen

from read_number_of_weeks import read_number_of_weeks
from read_rankings import read_rankings
from read_scores import read_scores
from read_stadiums import read_stadiums
from read_teams import read_teams


def predict(year, week):

    scores = read_scores(year, week)

    rankings = read_rankings(year, week - 1)

    home_stadiums = read_stadiums(year)

    # Check if the week is 'bowl' week
    num_weeks = read_number_of_weeks(year)
    if type(week) is str:
        week = num_weeks + 1
    elif week > num_weeks:
        raise Exception('Value of week should not exceed {0}. Did you mean "bowl"?'.format(num_weeks))

    # Loop through scores to make predictions
    predictions = []
    for game in scores['games']:

        # Get the team names
        away_team = game['game']['away']['names']['standard']
        home_team = game['game']['home']['names']['standard']

        # Try to download game info for location information
        game_center_url = game['game']['url']
        game_info_url = 'https://data.ncaa.com/casablanca{0}/gameInfo.json'.format(game_center_url)
        num_retries = 3
        success = False
        while num_retries > 0:
            try:
                game_info = download_game_info(game_info_url)
                num_retries = 0
                success = True
            except Exception:
                print('Error downloading game info, retrying...')
                num_retries -= 1
                time.sleep(1)

        # Determine home field advantage
        if success:

            # Get the stadium name, including city/state
            translation_table = str.maketrans('', '', '/-&() .;\'\n\t\r')
            stadium = game_info['venue']['name'].translate(translation_table)
            city = game_info['venue']['city'].translate(translation_table)
            state = game_info['venue']['state'].translate(translation_table)
            stadium_full_name = '{0}-{1}-{2}'.format(stadium, city, state)

            # Check if this is a true home game or not
            if stadium_full_name == home_stadiums[home_team]:
                home_field_advantage = 4
            else:
                print('{0} @ {1}: Neutral site game detected'.format(away_team, home_team))
                home_field_advantage = 0
        else:
            print('Failed to download game info, assuming true home game')
            home_field_advantage = 4

        # Get away team strength
        away_team_strength = rankings[away_team]['strength']

        # Get home team strength and add home field advantage
        home_team_strength = rankings[home_team]['strength'] + home_field_advantage

        # Pick the winner based on team strength
        if home_team_strength >= away_team_strength:
            predicted_winner = home_team
            predicted_margin_of_victory = home_team_strength - away_team_strength
        else:
            predicted_winner = away_team
            predicted_margin_of_victory = away_team_strength - home_team_strength

        # Calculate the game interest score
        game_interest = rankings[away_team]['team score'] + rankings[home_team]['team score'] - predicted_margin_of_victory

        # Pack predictions
        predictions.append({
            'away team': away_team,
            'home team': home_team,
            'predicted winner': predicted_winner,
            'predicted margin of victory': predicted_margin_of_victory,
            'game interest': game_interest
        })
    
    # Sort predictions by game interest
    predictions = sorted(predictions, key=lambda p: p['game interest'], reverse=True)

    # Print predictions
    predictions_file_string = 'AwayTeam,HomeTeam,PredictedWinner,PredictedMoV,GameInterest\n'
    for prediction in predictions:

        # Print to console in pretty format
        print('{0} @ {1}: Predicted Winner: {2}, Predicted MoV: {3:.1f}, Game Interest: {4:.1f}'.format(
            prediction['away team'], prediction['home team'], prediction['predicted winner'], prediction['predicted margin of victory'], prediction['game interest']))

        # Print to file string in csv format
        predictions_file_string += '{0},{1},{2},{3:.1f},{4:.1f}\n'.format(
            prediction['away team'], prediction['home team'], prediction['predicted winner'], prediction['predicted margin of victory'], prediction['game interest'])
        
    # Create the predictions file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}/predictions/{1}/predictions-{1}-{2:02}.csv'.format(absolute_path, year, week)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(predictions_file_string)

def download_game_info(game_info_url):
    web_response = urlopen(game_info_url)
    web_data = web_response.read()
    game_info = json.loads(web_data)
    return game_info
    
if __name__ == '__main__':
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != 'bowl':
        week = int(week)
    predict(year, week)

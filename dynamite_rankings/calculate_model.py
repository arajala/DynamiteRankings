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
import numpy as np

from read_teams import read_teams
from read_stats import read_stats
from read_model import read_model
from read_number_of_weeks import read_number_of_weeks


def calculate_model(year, week):

    # Check if the week is 'bowl' week
    num_weeks = read_number_of_weeks(year)
    if type(week) is str:
        week = num_weeks + 1
    elif week > num_weeks:
        raise Exception('Value of week should not exceed {0}. Did you mean "bowl"?'.format(num_weeks))

    teams, _ = read_teams(year)

    if week == 0:
        stats = None
    else:
        stats = read_stats(year, week)

    if week < 4:
        prev_stats = read_stats(year - 1, 'bowl')
        prev_model = read_model(year - 1, 'bowl')
    else:
        prev_stats = None
        prev_model = None

    games_played = calculate_games_played(week, stats, teams)
    points_margin = calculate_points_margin(week, stats, prev_stats, games_played, teams)
    rushing_yards_margin = calculate_rushing_yards_margin(week, stats, prev_stats, games_played, teams)
    home_field_corrections = calculate_home_field_corrections(week, stats, prev_stats, prev_model, games_played, teams)

    games_played_normalization = calculate_games_played_normalization(stats, games_played, teams)

    strengths = calculate_strengths(week, points_margin, rushing_yards_margin, home_field_corrections, games_played, games_played_normalization, prev_model, teams)
    average_opponent_strengths = games_played_normalization * strengths

    standard_deviations = calculate_standard_deviations(week, prev_model, teams)

    model = {}
    i = 0
    for team in teams:
        model[team] = {
            'strength': strengths[i],
            'standard deviation': standard_deviations[i],
            'points margin': points_margin[i],
            'average opponent strength': average_opponent_strengths[i],
            'rushing yards margin': rushing_yards_margin[i],
            'home field correction': home_field_corrections[i],
            'games played': games_played[i]
        }
        i += 1

    # Print predictions
    model_file_string = 'Team,Strength,StandardDeviation,PointsMargin,AverageOpponentStrength,RushingYardsMargin,HomeFieldCorrection,GamesPlayed\n'
    for team in model:

        # Print to file string in csv format
        model_file_string += '{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(
            team, model[team]['strength'], model[team]['standard deviation'], model[team]['points margin'], model[team]['average opponent strength'], model[team]['rushing yards margin'], model[team]['home field correction'], model[team]['games played'])
        
    # Create the predictions file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}\\model\\{1}\\model-{1}-{2:02}.json'.format(absolute_path, year, week)
    with open(filename, 'w') as file:
        file.write(model_file_string)

    return model, strengths, standard_deviations

def calculate_games_played(week, stats, teams):

    num_teams = len(teams)
    games_played = np.zeros(num_teams, 1)

    i = 0
    for team in teams:
        if week == 0:
            games_played[i] = 1
        elif week < 4:
            games_played[i] = stats[team]['games played']['season'] + 1
        else:
            games_played[i] = stats[team]['games played']['season']
        i += 1

    return games_played

def calculate_points_margin(week, stats, prev_stats, games_played, teams):

    num_teams = len(teams)
    points_margin = np.zeros(num_teams, 1)

    i = 0
    for team in teams:
        if week == 0:
            if team in prev_stats:
                prev_points_margin = prev_stats[team]['points']['total']['gained']['season'] - prev_stats[team]['points']['total']['allowed']['season']
                prev_games_played = prev_stats[team]['games played']['season']
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] = prev_points_margin_per_game
        elif week < 4:
            points_margin[i] = stats[team]['points']['total']['gained']['season'] - stats[team]['points']['total']['allowed']['season']
            if team in prev_stats:
                prev_points_margin = prev_stats[team]['points']['total']['gained']['season'] - prev_stats[team]['points']['total']['allowed']['season']
                prev_games_played = prev_stats[team]['games played']['season']
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] += prev_points_margin_per_game
            else:
                points_margin_per_game = points_margin[i] / max(1, (games_played[i] - 1))
                points_margin[i] += points_margin_per_game
        else:
            points_margin[i] = stats[team]['points']['total']['gained']['season'] - stats[team]['points']['total']['allowed']['season']

        points_margin[i] /= max(1, games_played[i])

        i += 1

    return points_margin

def calculate_rushing_yards_margin(week, stats, prev_stats, games_played, teams):

    num_teams = len(teams)
    rushing_yards_margin = np.zeros(num_teams, 1)

    i = 0
    for team in teams:
        if week == 0:
            if team in prev_stats:
                prev_rushing_yards_margin = prev_stats[team]['rushing']['yards']['gained']['season'] - prev_stats[team]['rushing']['yards']['allowed']['season']
                prev_games_played = prev_stats[team]['games played']['season']
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
        elif week < 4:
            rushing_yards_margin[i] = stats[team]['rushing']['yards']['gained']['season'] - stats[team]['rushing']['yards']['allowed']['season']
            if team in prev_stats:
                prev_rushing_yards_margin = prev_stats[team]['rushing']['yards']['gained']['season'] - prev_stats[team]['rushing']['yards']['allowed']['season']
                prev_games_played = prev_stats[team]['games played']['season']
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
            else:
                rushing_yards_margin_per_game = rushing_yards_margin[i] / max(1, (games_played[i] - 1))
                rushing_yards_margin[i] += rushing_yards_margin_per_game
        else:
            rushing_yards_margin[i] = stats[team]['rushing']['yards']['gained']['season'] - stats[team]['rushing']['yards']['allowed']['season']

        rushing_yards_margin[i] /= max(1, games_played[i])

        i += 1

    return rushing_yards_margin

def calculate_home_field_corrections(week, stats, prev_stats, prev_model, games_played, teams):

    num_teams = len(teams)
    home_field_corrections = np.zeros(num_teams, 1)

    i = 0
    for team in teams:
        for is_home in stats[team]['schedule']['home']:
            if is_home:
                home_field_corrections[i] -= 1
            else:
                home_field_corrections[i] += 1
        if week < 4:
            if team in prev_model:
                prev_home_field_correction = prev_model[team]['home field correction']
                prev_games_played = prev_stats[team]['games played']['season']
                prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                home_field_corrections[i] += prev_home_field_correction_per_game

        home_field_corrections[i] /= max(1, games_played[i])

        i += 1

    return home_field_corrections

def calculate_games_played_normalization(stats, games_played, teams):

    num_teams = len(teams)
    games_played_normalization = np.zeros(num_teams, num_teams)

    team_to_index = {}
    i = 0
    for team in teams:
        team_to_index[team] = i
        i += 1

    i = 0
    for team in teams:
        for opponent in stats[team]['schedule']['opponents']:
            j = team_to_index[opponent]
            games_played_normalization[i][j] = 1 / max(1, games_played[i])
        i += 1

    return games_played_normalization

def calculate_strengths(week, points_margin, rushing_yards_margin, home_field_corrections, games_played, games_played_normalization, prev_model, teams):

    num_teams = len(teams)

    rush_yard_coefficient = 0.0837058862488956
    home_field_coefficient = 4

    i = np.eye(num_teams)
    b = points_margin + rush_yard_coefficient * rushing_yards_margin + home_field_coefficient * home_field_corrections

    if week < 4:
        i = 0
        for team in teams:
            if team in prev_model:
                b[i] += prev_model[team]['average opponent strength'] / max(1, games_played[i])
            else:
                pass
            i += 1

    a = i - games_played_normalization
    strengths = np.linalg.solve(a, b)

    return strengths

def calculate_standard_deviations(year, week, teams):

    num_teams = len(teams)

    strengths = np.zeros(num_teams, week - 1)
    if week > 0:
        i = 0
        for team in teams:
            for w in range(1, week):
                prev_model = read_model(year, w)
                strengths[i][w - 1] = prev_model[team]['strength']
            i += 1
        standard_deviations = np.std(strengths, axis=2)
    else:
        standard_deviations = np.zeros(num_teams, 1)

    return standard_deviations

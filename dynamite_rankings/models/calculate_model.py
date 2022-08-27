# DynamiteRankings: An open-source NCAA football ranking and prediction program.
# Copyright (C) 2019-2022 Bryan VanDuinen and Arthur Rajala

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

###############################################################################

# Add the root package directory to path for importing
# This is to ease UX as user does not need to run setup.py or modify PYTHONPATH
from os.path import dirname, join, realpath
import sys
root = dirname(dirname(realpath(__file__)))
sys.path.append(root)
sys.path.append(join(dirname(root), "TheKickIsBAD"))

###############################################################################

# DynamiteRankings imports
from models.read_model import read_model

# TheKickIsBAD imports
import the_kick_is_bad
from the_kick_is_bad import utils

# Standard imports
import numpy as np

###############################################################################

def calculate_model(year, week, stats, teams):
    """ Calculates the model for a given year and week, and saves it to the models/{year} directory. """
    if week < 9:
        prev_teams = the_kick_is_bad.read_teams(year - 1)
        prev_stats = the_kick_is_bad.read_stats_by_category(year - 1, prev_teams)
        prev_games = the_kick_is_bad.read_games(year - 1)
        prev_year_final_week = sorted(prev_games.keys())[-1]
        prev_model = read_model(year - 1, prev_year_final_week)
    else:
        prev_stats = None
        prev_model = None

    games_played = calculate_games_played(week, stats, teams)
    points_margin = calculate_points_margin(week, stats, prev_stats, games_played, teams)
    rushing_yards_margin = calculate_rushing_yards_margin(week, stats, prev_stats, games_played, teams)
    home_field_corrections = calculate_home_field_corrections(week, stats, prev_stats, prev_model, games_played, teams)

    games_played_normalization = calculate_games_played_normalization(week, stats, games_played, teams)

    strengths = calculate_strengths(week, points_margin, rushing_yards_margin, home_field_corrections, games_played, games_played_normalization, prev_model, teams)
    average_opponent_strengths = np.matmul(games_played_normalization, strengths)

    standard_deviations = calculate_standard_deviations(year, week, prev_model, teams)

    model = {}
    i = 0
    for team in teams:
        model[team] = {
            "strength": strengths[i],
            "standard deviation": standard_deviations[i],
            "points margin": points_margin[i],
            "average opponent strength": average_opponent_strengths[i],
            "rushing yards margin": rushing_yards_margin[i],
            "home field correction": home_field_corrections[i],
            "games played": games_played[i]
        }
        i += 1

    # Print predictions
    model_file_string = "Team,Strength,StandardDeviation,PointsMargin,AverageOpponentStrength,RushingYardsMargin,HomeFieldCorrection,GamesPlayed\n"
    for team in model:

        # Print to file string in csv format
        model_file_string += "{0},{1},{2},{3},{4},{5},{6},{7:.0f}\n".format(team,
                                                                            model[team]["strength"],
                                                                            model[team]["standard deviation"],
                                                                            model[team]["points margin"],
                                                                            model[team]["average opponent strength"],
                                                                            model[team]["rushing yards margin"],
                                                                            model[team]["home field correction"],
                                                                            model[team]["games played"])
        
    # Create the predictions file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/{year}/model-{year}-{week:02}.csv"
    utils.write_string(model_file_string, filename)

    return model, strengths, standard_deviations

def calculate_games_played(week, stats, teams):
    """ Calculates a team-wise array of games played through the current week.
        Sets a minimum value of 1 to avoid future divide by 0 concerns.
        Before week 9, counts last season as an extra game. """
    num_teams = len(teams)
    games_played = np.zeros(num_teams)

    i = 0
    for team in teams:
        # Set minimum of 1 game to protect against div by 0
        if week == 0:
            games_played[i] = 1
        else:
            # Loop through pairs of week and games played results
            for matchup_week, result_gp in zip(stats[team]["matchups"]["weeks"], stats[team]["results"]["games played"]):
                # Count the games played up to the requested week
                if matchup_week <= week:
                    games_played[i] += result_gp
            # Before week 9, count an extra game for 'last year'
            if week < 9:
                games_played[i] += 1
        i += 1

    return games_played

def calculate_points_margin(week, stats, prev_stats, games_played, teams):
    """ Calculates a team-wise array of point margins per game.
        For the preseason ranking, only uses the average of last season.
        Before week 9, uses last season's average as an extra game. """
    num_teams = len(teams)
    points_margin = np.zeros(num_teams)

    i = 0
    for team in teams:
        # Use last year's stats for this year's preseason
        if week == 0:
            if team in prev_stats:
                prev_points_margin = sum(prev_stats[team]["results"]["points"]) - sum(prev_stats[team]["results"]["points allowed"])
                prev_games_played = sum(prev_stats[team]["results"]["games played"])
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] = prev_points_margin_per_game
        else:
            points_margin[i] = sum(stats[team]["results"]["points"]) - sum(stats[team]["results"]["points allowed"])
            # Before week 9, count an extra game for 'last year'
            if week < 9:
                # If the team existed last year, use the actual values from last year
                if team in prev_stats:
                    prev_points_margin = sum(prev_stats[team]["results"]["points"]) - sum(prev_stats[team]["results"]["points allowed"])
                    prev_games_played = sum(prev_stats[team]["results"]["games played"])
                    prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                    points_margin[i] += prev_points_margin_per_game
                # If this is a new team, fake the previous value with this year's average
                else:
                    points_margin_per_game = points_margin[i] / max(1, (games_played[i] - 1))
                    points_margin[i] += points_margin_per_game

        points_margin[i] /= max(1, games_played[i])
        i += 1

    return points_margin

def calculate_rushing_yards_margin(week, stats, prev_stats, games_played, teams):
    """ Calculates a team-wise array of rushing yard margins per game.
        For the preseason ranking, only uses the average of last season.
        Before week 9, uses last season's average as an extra game. """
    num_teams = len(teams)
    rushing_yards_margin = np.zeros(num_teams)

    i = 0
    for team in teams:
        # Use last year's stats for this year's preseason
        if week == 0:
            if team in prev_stats:
                prev_rushing_yards_margin = sum(prev_stats[team]["offense"]["rushing"]["yards"]) - sum(prev_stats[team]["defense"]["rushing"]["yards"])
                prev_games_played = sum(prev_stats[team]["results"]["games played"])
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
            else:
                print(f"Warning: didn't find {team} in last year's stats")
        else:
            rushing_yards_margin[i] = sum(stats[team]["offense"]["rushing"]["yards"]) - sum(stats[team]["defense"]["rushing"]["yards"])
            # Before week 9, count an extra game for 'last year'
            if week < 9:
                # If the team existed last year, use the actual values from last year
                if team in prev_stats:
                    prev_rushing_yards_margin = sum(prev_stats[team]["offense"]["rushing"]["yards"]) - sum(prev_stats[team]["defense"]["rushing"]["yards"])
                    prev_games_played = sum(prev_stats[team]["results"]["games played"])
                    prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                    rushing_yards_margin[i] += prev_rushing_yards_margin_per_game
                # If this is a new team, fake the previous value with this year's average
                else:
                    rushing_yards_margin_per_game = rushing_yards_margin[i] / max(1, (games_played[i] - 1))
                    rushing_yards_margin[i] += rushing_yards_margin_per_game

        rushing_yards_margin[i] /= max(1, games_played[i])
        i += 1

    return rushing_yards_margin

def calculate_home_field_corrections(week, stats, prev_stats, prev_model, games_played, teams):
    """ Calculates a team-wise array of home field correction factors.
        For the preseason ranking, only uses the average of last season.
        Before week 9, uses last season's average as an extra game. """
    num_teams = len(teams)
    home_field_corrections = np.zeros(num_teams)

    i = 0
    for team in teams:
        # Use last year's stats for this year's preseason
        if week == 0:
            if team in prev_stats:
                prev_home_field_correction = prev_model[team]["home field correction"]
                prev_games_played = sum(prev_stats[team]["results"]["games played"])
                prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                home_field_corrections[i] += prev_home_field_correction_per_game
            else:
                print(f"Warning: didn't find {team} in last year's stats")
        else:
            for is_home, neutral_site in zip(stats[team]["matchups"]["home"], stats[team]["matchups"]["neutral site"]):
                if is_home:
                    home_field_corrections[i] -= 1
                elif not neutral_site:
                    home_field_corrections[i] += 1
            # Before week 9, count an extra game for 'last year'
            if week < 9:
                # If the team existed last year, use the actual values from last year
                if team in prev_model and team in prev_stats:
                    prev_home_field_correction = prev_model[team]["home field correction"]
                    prev_games_played = sum(prev_stats[team]["results"]["games played"])
                    prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                    home_field_corrections[i] += prev_home_field_correction_per_game
                else:
                    print(f"Warning: didn't find {team} in last year's model or stats")

        home_field_corrections[i] /= max(1, games_played[i])
        i += 1

    return home_field_corrections

def calculate_games_played_normalization(week, stats, games_played, teams):
    """ Calculates a team by team matrix of normalization factors based on games played. """
    num_teams = len(teams)
    games_played_normalization = np.zeros((num_teams, num_teams))

    team_to_index = {}
    i = 0
    for team in teams:
        team_to_index[team] = i
        i += 1

    if week > 0:
        i = 0
        for team in teams:
            for opponent in stats[team]["matchups"]["opponents"]:
                j = team_to_index[opponent]
                games_played_normalization[i][j] = 1 / max(1, games_played[i])
            i += 1

    return games_played_normalization

def calculate_strengths(week, points_margin, rushing_yards_margin, home_field_corrections, games_played, games_played_normalization, prev_model, teams):
    """ Calculates a team-wise array of team strengths based on the DynamiteRankings special sauce. """
    num_teams = len(teams)

    rush_yard_coefficient = 0.0837058862488956
    home_field_coefficient = 4

    I = np.eye(num_teams)
    B = points_margin + rush_yard_coefficient * rushing_yards_margin + home_field_coefficient * home_field_corrections

    if week < 9:
        i = 0
        for team in teams:
            if team in prev_model:
                B[i] += prev_model[team]["average opponent strength"] / max(1, games_played[i])
            else:
                print(f"Warning: didn't find {team} in last year's model")
                pass
            i += 1

    A = I - games_played_normalization
    try:
        strengths = np.linalg.solve(A, B)
    except:
        print(f"Warning: Singular matrix cannot be solved in week {week}, using least squares")
        strengths = np.linalg.lstsq(A, B, rcond=-1)[0]

    return strengths

def calculate_standard_deviations(year, week, prev_model, teams):
    """ Calculates a team-wise array of the standard deviations of team strengths.
        For the preseason ranking, returns zeros. """
    num_teams = len(teams)

    if week > 0:
        strengths = np.zeros((num_teams, week))
        i = 0
        for team in teams:
            for w in range(1, week):
                prev_model = read_model(year, w)
                strengths[i][w - 1] = prev_model[team]["strength"]
            i += 1
        standard_deviations = np.std(strengths, axis=1)
    else:
        standard_deviations = np.zeros(num_teams)

    return standard_deviations

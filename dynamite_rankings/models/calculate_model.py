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
import numpy as np
import the_kick_is_bad
from the_kick_is_bad import utils

# DynamiteRankings imports
from models.read_model import read_model


def calculate_model(year, week, stats, teams):

    if week < 9:
        prev_stats = the_kick_is_bad.read_stats(year - 1, "bowl")
        prev_model = read_model(year - 1, "bowl")
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

    num_teams = len(teams)
    games_played = np.zeros(num_teams)

    i = 0
    for team in teams:
        if week == 0:
            games_played[i] = 1
        elif week < 9:
            games_played[i] = stats[team]["games played"]["season"] + 1
        else:
            games_played[i] = stats[team]["games played"]["season"]
        i += 1

    return games_played

def calculate_points_margin(week, stats, prev_stats, games_played, teams):

    num_teams = len(teams)
    points_margin = np.zeros(num_teams)

    i = 0
    for team in teams:
        if week == 0:
            if team in prev_stats:
                prev_points_margin = sum(prev_stats[team]["points"]["total"]["gained"]) - sum(prev_stats[team]["points"]["total"]["allowed"])
                prev_games_played = prev_stats[team]["games played"]["season"]
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] = prev_points_margin_per_game
            else:
                prev_points_margin = sum(prev_stats["FCS"]["points"]["total"]["gained"]) - sum(prev_stats["FCS"]["points"]["total"]["allowed"])
                prev_games_played = prev_stats["FCS"]["games played"]["season"]
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] = prev_points_margin_per_game
        elif week < 9:
            points_margin[i] = sum(stats[team]["points"]["total"]["gained"]) - sum(stats[team]["points"]["total"]["allowed"])
            if team in prev_stats:
                prev_points_margin = sum(prev_stats[team]["points"]["total"]["gained"]) - sum(prev_stats[team]["points"]["total"]["allowed"])
                prev_games_played = prev_stats[team]["games played"]["season"]
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] += prev_points_margin_per_game
            else:
                prev_points_margin = sum(prev_stats["FCS"]["points"]["total"]["gained"]) - sum(prev_stats["FCS"]["points"]["total"]["allowed"])
                prev_games_played = prev_stats["FCS"]["games played"]["season"]
                prev_points_margin_per_game = prev_points_margin / max(1, prev_games_played)
                points_margin[i] += prev_points_margin_per_game
        else:
            points_margin[i] = sum(stats[team]["points"]["total"]["gained"]) - sum(stats[team]["points"]["total"]["allowed"])

        points_margin[i] /= max(1, games_played[i])

        i += 1

    return points_margin

def calculate_rushing_yards_margin(week, stats, prev_stats, games_played, teams):

    num_teams = len(teams)
    rushing_yards_margin = np.zeros(num_teams)

    i = 0
    for team in teams:
        if week == 0:
            if team in prev_stats:
                prev_rushing_yards_margin = sum(prev_stats[team]["rushing"]["yards"]["gained"]) - sum(prev_stats[team]["rushing"]["yards"]["allowed"])
                prev_games_played = prev_stats[team]["games played"]["season"]
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
            else:
                prev_rushing_yards_margin = sum(prev_stats["FCS"]["rushing"]["yards"]["gained"]) - sum(prev_stats["FCS"]["rushing"]["yards"]["allowed"])
                prev_games_played = prev_stats["FCS"]["games played"]["season"]
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
        elif week < 9:
            rushing_yards_margin[i] = sum(stats[team]["rushing"]["yards"]["gained"]) - sum(stats[team]["rushing"]["yards"]["allowed"])
            if team in prev_stats:
                prev_rushing_yards_margin = sum(prev_stats[team]["rushing"]["yards"]["gained"]) - sum(prev_stats[team]["rushing"]["yards"]["allowed"])
                prev_games_played = prev_stats[team]["games played"]["season"]
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
            else:
                prev_rushing_yards_margin = sum(prev_stats["FCS"]["rushing"]["yards"]["gained"]) - sum(prev_stats["FCS"]["rushing"]["yards"]["allowed"])
                prev_games_played = prev_stats["FCS"]["games played"]["season"]
                prev_rushing_yards_margin_per_game = prev_rushing_yards_margin / max(1, prev_games_played)
                rushing_yards_margin[i] = prev_rushing_yards_margin_per_game
        else:
            rushing_yards_margin[i] = sum(stats[team]["rushing"]["yards"]["gained"]) - sum(stats[team]["rushing"]["yards"]["allowed"])

        rushing_yards_margin[i] /= max(1, games_played[i])

        i += 1

    return rushing_yards_margin

def calculate_home_field_corrections(week, stats, prev_stats, prev_model, games_played, teams):

    num_teams = len(teams)
    home_field_corrections = np.zeros(num_teams)

    i = 0
    for team in teams:
        if week == 0:
            if team in prev_model:
                prev_home_field_correction = prev_model[team]["home field correction"]
                prev_games_played = prev_stats[team]["games played"]["season"]
                prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                home_field_corrections[i] += prev_home_field_correction_per_game
            else:
                prev_home_field_correction = prev_model["FCS"]["home field correction"]
                prev_games_played = prev_stats["FCS"]["games played"]["season"]
                prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                home_field_corrections[i] += prev_home_field_correction_per_game
        elif week < 9:
            for is_home in stats[team]["schedule"]["home"]:
                if is_home:
                    home_field_corrections[i] -= 1
                else:
                    home_field_corrections[i] += 1
            if team in prev_model:
                prev_home_field_correction = prev_model[team]["home field correction"]
                prev_games_played = prev_stats[team]["games played"]["season"]
                prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                home_field_corrections[i] += prev_home_field_correction_per_game
            else:
                prev_home_field_correction = prev_model["FCS"]["home field correction"]
                prev_games_played = prev_stats["FCS"]["games played"]["season"]
                prev_home_field_correction_per_game = prev_home_field_correction / max(1, prev_games_played)
                home_field_corrections[i] += prev_home_field_correction_per_game
        else:
            for is_home in stats[team]["schedule"]["home"]:
                if is_home:
                    home_field_corrections[i] -= 1
                else:
                    home_field_corrections[i] += 1

        home_field_corrections[i] /= max(1, games_played[i])

        i += 1

    return home_field_corrections

def calculate_games_played_normalization(week, stats, games_played, teams):

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
            for opponent in stats[team]["schedule"]["opponents"]:
                j = team_to_index[opponent]
                games_played_normalization[i][j] = 1 / max(1, games_played[i])
            i += 1

    return games_played_normalization

def calculate_strengths(week, points_margin, rushing_yards_margin, home_field_corrections, games_played, games_played_normalization, prev_model, teams):

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
                B[i] += prev_model["FCS"]["average opponent strength"] / max(1, games_played[i])
            i += 1

    A = I - games_played_normalization
    strengths = np.linalg.solve(A, B)

    return strengths

def calculate_standard_deviations(year, week, prev_model, teams):

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

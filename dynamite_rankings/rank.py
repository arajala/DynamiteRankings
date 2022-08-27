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
sys.path.append(join(root, "TheKickIsBAD"))

###############################################################################

# DynamiteRankings imports
from models.calculate_model import calculate_model
from rankings.read_rankings import read_rankings

# TheKickIsBAD imports
import the_kick_is_bad
from the_kick_is_bad import utils

# Standard imports
import argparse
import numpy as np
import statistics

###############################################################################

def rank(year, week):
    """ Ranks all teams, conferences, and divisions for the given {year}, {week}. """
    teams = the_kick_is_bad.read_teams(year)

    if week == 0:
        stats = None
    else:
        stats = the_kick_is_bad.read_stats_by_category(year, teams, max_week=week)

    teams = the_kick_is_bad.read_teams(year)

    team_rankings = calculate_team_rankings(year, week, stats, teams)

    calculate_conference_rankings(year, week, teams, team_rankings)

    calculate_division_rankings(year, week, teams, team_rankings)

def calculate_team_rankings(year, week, stats, teams):
    """ Calculates team rankings, prints them to console, and saves them to rankings/{year} directory. """
    _, strengths, standard_deviations = calculate_model(year, week, stats, teams)

    normalized_strengths = strengths - min(strengths)
    if week > 0:
        prev_rankings = read_rankings(year, week - 1)

    if week == 0:
        team_scores = normalized_strengths * 0.5
    else:
        wins = get_wins_array(stats, teams)
        games_played = get_games_played_array(stats, teams)
        team_scores = normalized_strengths * (wins + 2) / (games_played + 4)

    sort_indexes = np.argsort(-team_scores)

    rankings = {}
    i = 0
    if week > 0:
        for team in teams:
            rankings[team] = {
                "rank": np.where(sort_indexes == i)[0][0] + 1,
                "previous rank": prev_rankings[team]["rank"],
                "delta rank": prev_rankings[team]["rank"] - (np.where(sort_indexes == i)[0][0] + 1),
                "team score": team_scores[i],
                "strength": strengths[i],
                "standard deviation": standard_deviations[i]
            }
            i += 1
    else:
        for team in teams:
            rankings[team] = {
                "rank": np.where(sort_indexes == i)[0][0] + 1,
                "previous rank": 0,
                "delta rank": 0 - (np.where(sort_indexes == i)[0][0] + 1),
                "team score": team_scores[i],
                "strength": strengths[i],
                "standard deviation": standard_deviations[i]
            }
            i += 1

    # Print teamrankings
    team_rankings_file_string = "Team,Rank,PrevRank,DeltaRank,TeamScore,Strength,StandardDeviation\n"
    for team in rankings:

        # Print to file string in csv format
        team_rankings_file_string += "{0},{1:.0f},{2:.0f},{3:.0f},{4:.1f},{5:.1f},{6:.1f}\n".format(team,
                                                                                                    rankings[team]["rank"],
                                                                                                    rankings[team]["previous rank"],
                                                                                                    rankings[team]["delta rank"],
                                                                                                    rankings[team]["team score"],
                                                                                                    rankings[team]["strength"],
                                                                                                    rankings[team]["standard deviation"])
        
    teams_list = []
    team_names = []
    for team in teams.values():
        teams_list.append(team["uniqname"])
        team_names.append(team["name"])

    print("")
    for index in sort_indexes:
        team = teams_list[index]
        team_name = team_names[index]
        team_rankings_string = "{0:.0f} ({1:.0f}): {2}, Team Score: {3:.1f}, Strength: {4:.1f}, Std: {5:.1f}".format(rankings[team]["rank"],
                                                                                                                     rankings[team]["delta rank"],
                                                                                                                     team_name,
                                                                                                                     rankings[team]["team score"],
                                                                                                                     rankings[team]["strength"],
                                                                                                                     rankings[team]["standard deviation"])
        print(team_rankings_string)

    # Create the predictions file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/rankings/{year}/team_rankings-{year}-{week:02}.csv"
    utils.write_string(team_rankings_file_string, filename)

    return rankings

def calculate_conference_rankings(year, week, teams, team_rankings):
    """ Calculates conference rankings, prints them to console, and saves them to rankings/{year} directory. """
    # Make lists of all the team scores in each conference
    conference_rankings = {}
    for team in teams:
        conference = teams[team]["conference"]
        if conference not in conference_rankings:
            conference_rankings[conference] = []
        conference_rankings[conference].append(team_rankings[team]["team score"])

    # Convert dictionary to averaged list for sorting
    sorted_conference_rankings = []
    for conference in conference_rankings:
        sorted_conference_rankings.append({
            "conference": conference,
            "score": statistics.mean(conference_rankings[conference])
        })
    
    # Sort conference rankings by average team score
    sorted_conference_rankings = sorted(sorted_conference_rankings, key=lambda p: p["score"], reverse=True)

    # Print conference rankings
    print("")
    rank = 1
    conference_rankings_file_string = "Conference,Score\n"
    for conference_ranking in sorted_conference_rankings:

        # Print to file string in csv format
        conference = conference_ranking["conference"]
        score = conference_ranking["score"]
        conference_rankings_file_string += f"{conference},{score:.1f}\n"

        # Print to console in pretty format
        print(f"{rank}: {conference}, Score: {score:.1f}")
        rank += 1

    # Create the conference rankings file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/rankings/{year}/conference_rankings-{year}-{week:02}.csv"
    utils.write_string(conference_rankings_file_string, filename)

def calculate_division_rankings(year, week, teams, team_rankings):
    """ Calculates division rankings, prints them to console, and saves them to rankings/{year} directory. """
    # Make lists of all the team scores in each division
    division_rankings = {}
    for team in teams:
        conference = teams[team]["conference"]
        division = teams[team]["division"]
        if division == "":
            division = conference
        else:
            division = f"{conference} - {division}"
        if division not in division_rankings:
            division_rankings[division] = []
        division_rankings[division].append(team_rankings[team]["team score"])

    # Convert dictionary to averaged list for sorting
    sorted_division_rankings = []
    for division in division_rankings:
        sorted_division_rankings.append({
            "division": division,
            "score": statistics.mean(division_rankings[division])
        })
    
    # Sort division rankings by average team score
    sorted_division_rankings = sorted(sorted_division_rankings, key=lambda p: p["score"], reverse=True)

    # Print division rankings
    print("")
    rank = 1
    division_rankings_file_string = "Division,Score\n"
    for division_ranking in sorted_division_rankings:

        # Print to file string in csv format
        division = division_ranking["division"]
        score = division_ranking["score"]
        division_rankings_file_string += f"{division},{score:.1f}\n"

        # Print to console in pretty format
        print(f"{rank}: {division}, Score: {score:.1f}")
        rank += 1

    # Create the division rankings file with absolute path
    absolute_path = utils.get_abs_path(__file__)
    filename = f"{absolute_path}/rankings/{year}/division_rankings-{year}-{week:02}.csv"
    utils.write_string(division_rankings_file_string, filename)

def get_wins_array(stats, teams):
    num_teams = len(teams)
    wins = np.zeros(num_teams)

    i = 0
    for team in teams:
        wins[i] = sum(stats[team]["results"]["won"])
        i += 1

    return wins

def get_games_played_array(stats, teams):
    num_teams = len(teams)
    games_played = np.zeros(num_teams)

    i = 0
    for team in teams:
        games_played[i] = sum(stats[team]["results"]["games played"])
        i += 1

    return games_played

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    parser.add_argument("week", type=int)
    args = parser.parse_args()
    rank(args.year, args.week)

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

import numpy as np

from calculate_model import calculate_model
from read_rankings import read_rankings
from read_stats import read_stats
from read_teams import read_teams


def rank(year, week):

    team_rankings = calculate_team_rankings(year, week)

    calculate_conference_rankings(year, week, team_rankings)

    calculate_division_rankings(year, week, team_rankings)

def calculate_team_rankings(year, week):

    if week > 0:
        stats = read_stats(year, week)
    else:
        stats = None

    teams, _ = read_teams(year)
    
    _, strengths, standard_deviations = calculate_model(year, week, stats, teams)
    # strengths = get_model_array(model, 'strength')
    normalized_strengths = strengths - min(strengths)
    # standard_deviations = get_model_array(model, 'standard deviation')
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
                'rank': np.where(sort_indexes == i)[0][0] + 1,
                'previous rank': prev_rankings[team]['rank'],
                'delta rank': prev_rankings[team]['rank'] - (np.where(sort_indexes == i)[0][0] + 1),
                'team score': team_scores[i],
                'strength': strengths[i],
                'standard deviation': standard_deviations[i]
            }
            i += 1
    else:
        for team in teams:
            rankings[team] = {
                'rank': np.where(sort_indexes == i)[0][0] + 1,
                'previous rank': 0,
                'delta rank': 0 - (np.where(sort_indexes == i)[0][0] + 1),
                'team score': team_scores[i],
                'strength': strengths[i],
                'standard deviation': standard_deviations[i]
            }
            i += 1

    # Print teamrankings
    team_rankings_file_string = 'Team,Rank,PrevRank,DeltaRank,TeamScore,Strength,StandardDeviation\n'
    for team in rankings:

        # Print to file string in csv format
        team_rankings_file_string += '{0},{1},{2},{3},{4},{5},{6}\n'.format(
            team, rankings[team]['rank'], rankings[team]['previous rank'], rankings[team]['delta rank'], rankings[team]['team score'], rankings[team]['strength'], rankings[team]['standard deviation'])
        
    teams_list = []
    for team in teams:
        teams_list.append(team)

    for index in sort_indexes:
        team = teams_list[index]
        team_rankings_string = '{0} ({1}): {2}, Team Score: {3:.1f}, Strength: {4:.1f}, Std: {5:.1f}'.format(
            rankings[team]['rank'], rankings[team]['delta rank'], team, rankings[team]['team score'], rankings[team]['strength'], rankings[team]['standard deviation'])
        print(team_rankings_string)

    # Create the predictions file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}\\rankings\\{1}\\team_rankings-{1}-{2:02}.csv'.format(absolute_path, year, week)
    with open(filename, 'w') as file:
        file.write(team_rankings_file_string)

    return rankings

def calculate_conference_rankings(year, week, team_rankings):
    pass

def calculate_division_rankings(year, week, team_rankings):
    pass

def get_wins_array(stats, teams):
    num_teams = len(teams)
    wins = np.zeros(num_teams, 1)

    i = 0
    for team in teams:
        wins[i] = stats[team]['record']['wins']['season']
        i += 1

    return wins

def get_games_played_array(stats, teams):
    num_teams = len(teams)
    games_played = np.zeros(num_teams, 1)

    i = 0
    for team in teams:
        games_played[i] = stats[team]['games played']['season']
        i += 1

    return games_played
    
if __name__ == '__main__':
    year = int(sys.argv[1])
    week = sys.argv[2]
    if week != 'bowl':
        week = int(week)
    rank(year, week)

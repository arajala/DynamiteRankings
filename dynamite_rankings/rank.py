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
import statistics
import sys

import numpy as np

from calculate_model import calculate_model
from read_number_of_weeks import read_number_of_weeks
from read_rankings import read_rankings
from read_stats import read_stats
from read_teams import read_teams


def rank(year, week):

    if week == 0:
        stats = None
    else:
        stats = read_stats(year, week)

    # Check if the week is 'bowl' week and read stats
    num_weeks = read_number_of_weeks(year)
    if type(week) is str:
        week = num_weeks + 1
    elif week > num_weeks:
        raise Exception('Value of week should not exceed {0}. Did you mean "bowl"?'.format(num_weeks))

    teams, _ = read_teams(year)

    team_rankings = calculate_team_rankings(year, week, stats, teams)

    calculate_conference_rankings(year, week, teams, team_rankings)

    calculate_division_rankings(year, week, teams, team_rankings)

def calculate_team_rankings(year, week, stats, teams):
    
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
        team_rankings_file_string += '{0},{1:.0f},{2:.0f},{3:.0f},{4},{5},{6}\n'.format(
            team, rankings[team]['rank'], rankings[team]['previous rank'], rankings[team]['delta rank'], rankings[team]['team score'], rankings[team]['strength'], rankings[team]['standard deviation'])
        
    teams_list = []
    for team in teams:
        teams_list.append(team)

    for index in sort_indexes:
        team = teams_list[index]
        team_rankings_string = '{0:.0f} ({1:.0f}): {2}, Team Score: {3:.1f}, Strength: {4:.1f}, Std: {5:.1f}'.format(
            rankings[team]['rank'], rankings[team]['delta rank'], team, rankings[team]['team score'], rankings[team]['strength'], rankings[team]['standard deviation'])
        print(team_rankings_string)

    # Create the predictions file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}/rankings/{1}/team_rankings-{1}-{2:02}.csv'.format(absolute_path, year, week)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(team_rankings_file_string)

    return rankings

def calculate_conference_rankings(year, week, teams, team_rankings):

    # Make lists of all the team scores in each conference
    conference_rankings = {}
    for team in teams:
        conference = teams[team]['conference']
        if conference not in conference_rankings:
            conference_rankings[conference] = []
        conference_rankings[conference].append(team_rankings[team]['team score'])

    # Convert dictionary to averaged list for sorting
    sorted_conference_rankings = []
    for conference in conference_rankings:
        sorted_conference_rankings.append({
            'conference': conference,
            'score': statistics.mean(conference_rankings[conference])
        })
    
    # Sort conference rankings by average team score
    sorted_conference_rankings = sorted(sorted_conference_rankings, key=lambda p: p['score'], reverse=True)

    # Print conference rankings
    rank = 1
    conference_rankings_file_string = 'Conference,Score\n'
    for conference_ranking in sorted_conference_rankings:

        # Print to file string in csv format
        conference_rankings_file_string += '{0},{1:.1f}\n'.format(conference_ranking['conference'], conference_ranking['score'])

        # Print to console in pretty format
        print('{0}: {1}, Score: {2:.1f}'.format(rank, conference_ranking['conference'], conference_ranking['score']))
        rank += 1

    # Create the conference rankings file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}/rankings/{1}/conference_rankings-{1}-{2:02}.csv'.format(absolute_path, year, week)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(conference_rankings_file_string)

def calculate_division_rankings(year, week, teams, team_rankings):

    # Make lists of all the team scores in each division
    division_rankings = {}
    for team in teams:
        division = teams[team]['division']
        if division not in division_rankings:
            division_rankings[division] = []
        division_rankings[division].append(team_rankings[team]['team score'])

    # Convert dictionary to averaged list for sorting
    sorted_division_rankings = []
    for division in division_rankings:
        sorted_division_rankings.append({
            'division': division,
            'score': statistics.mean(division_rankings[division])
        })
    
    # Sort division rankings by average team score
    sorted_division_rankings = sorted(sorted_division_rankings, key=lambda p: p['score'], reverse=True)

    # Print division rankings
    rank = 1
    division_rankings_file_string = 'Division,Score\n'
    for division_ranking in sorted_division_rankings:

        # Print to file string in csv format
        division_rankings_file_string += '{0},{1:.1f}\n'.format(division_ranking['division'], division_ranking['score'])

        # Print to console in pretty format
        print('{0}: {1}, Score: {2:.1f}'.format(rank, division_ranking['division'], division_ranking['score']))
        rank += 1

    # Create the division rankings file with absolute path
    absolute_path = os.path.dirname(os.path.realpath(__file__))
    filename = '{0}/rankings/{1}/division_rankings-{1}-{2:02}.csv'.format(absolute_path, year, week)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(division_rankings_file_string)

def get_wins_array(stats, teams):
    num_teams = len(teams)
    wins = np.zeros(num_teams)

    i = 0
    for team in teams:
        wins[i] = stats[team]['record']['wins']['season']
        i += 1

    return wins

def get_games_played_array(stats, teams):
    num_teams = len(teams)
    games_played = np.zeros(num_teams)

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

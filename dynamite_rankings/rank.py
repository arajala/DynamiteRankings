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
from read_stats import read_stats
from read_teams import read_teams


def rank(year, week):

    team_rankings = calculate_team_rankings(year, week)

    calculate_conference_rankings(year, week, team_rankings)

    calculate_division_rankings(year, week, team_rankings)

def calculate_team_rankings(year, week):

    stats = read_stats(year, week)
    teams, _ = read_teams(year)
    
    model, strengths, _ = calculate_model(year, week)
    # strengths = get_model_array(model, 'strength')
    strengths = strengths - min(strengths)
    # standard_deviations = get_model_array(model, 'standard deviation')

    if week == 0:
        team_scores = strengths * 0.5
    else:
        wins = get_wins_array(stats, teams)
        games_played = get_games_played_array(stats, teams)
        team_scores = strengths * (wins + 2) / (games_played + 4)

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

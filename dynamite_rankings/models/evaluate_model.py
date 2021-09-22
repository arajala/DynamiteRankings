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
import the_kick_is_bad
from the_kick_is_bad import utils

# DynamiteRankings imports
from rankings.read_rankings import read_rankings


def evaluate_model():

    results = {}

    start_year = 2013
    end_year = 2020
    max_num_weeks = 16
    
    all_num_games = 0
    all_num_correct = 0
    conf_num_games = 0
    conf_num_correct = 0
    nonconf_num_games = 0
    nonconf_num_correct = 0
    champ_num_games = 0
    champ_num_correct = 0
    fcs_num_games = 0
    fcs_num_correct = 0
    bowl_num_games = 0
    bowl_num_correct = 0
    yearly_num_games = []
    for _ in range(0, end_year - start_year + 1):
        yearly_num_games.append(0)
    yearly_num_correct = []
    for _ in range(0, end_year - start_year + 1):
        yearly_num_correct.append(0)
    weekly_num_games = []
    for _ in range(0, max_num_weeks):
        weekly_num_games.append(0)
    weekly_num_correct = []
    for _ in range(0, max_num_weeks):
        weekly_num_correct.append(0)

    for year in range(start_year, end_year + 1):

        year_idx = year - start_year

        teams, _ = the_kick_is_bad.read_teams(year)

        num_weeks = the_kick_is_bad.read_number_of_weeks(year)

        for week in range(1, num_weeks + 1):

            week_idx = week - 1

            print(f"Processing evaluation data from year {year}, week {week:02}...")

            rankings = read_rankings(year, week - 1)

            scores = the_kick_is_bad.read_scores(year, week)

            # Loop through scores to make predictions
            for game in scores["games"]:

                # Get the team names
                away_team = game["game"]["away"]["names"]["standard"]
                home_team = game["game"]["home"]["names"]["standard"]

                # Check if this is a valid game
                if game["game"]["gameState"] != "final":
                    continue

                # Get the actual results
                away_score = int(game["game"]["away"]["score"])
                home_score = int(game["game"]["home"]["score"])
                if away_score > home_score:
                    home_won = 0
                elif away_score < home_score:
                    home_won = 1
                else:
                    continue

                # Determine home field advantage
                # Assume all bowl games are neutral site
                home_field_advantage = 4

                # Get away team strength
                away_team_strength = rankings[away_team]["strength"]

                # Get home team strength and add home field advantage
                home_team_strength = rankings[home_team]["strength"] + home_field_advantage

                # Pick the winner based on team strength
                if home_team_strength >= away_team_strength:
                    prediction = 1
                else:
                    prediction = 0

                # Determine if the result was right
                if home_won == prediction:
                    is_correct = 1
                else:
                    is_correct = 0

                # Increment relevant result counters
                all_num_games += 1
                all_num_correct += is_correct
                # Conference/non-conference
                away_team_conference = teams[away_team]["conference"]
                home_team_conference = teams[home_team]["conference"]
                if away_team_conference == home_team_conference:
                    conf_num_games += 1
                    conf_num_correct += is_correct
                elif away_team != "FCS" and home_team != "FCS":
                    nonconf_num_games += 1
                    nonconf_num_correct += is_correct
                # Championship
                if (week == num_weeks - 1) and (away_team_conference == home_team_conference):
                    champ_num_games += 1
                    champ_num_correct += is_correct
                # FCS
                if away_team == "FCS" or home_team == "FCS":
                    fcs_num_games += 1
                    fcs_num_correct += is_correct
                # Yearly
                yearly_num_games[year_idx] += 1
                yearly_num_correct[year_idx] += is_correct
                # Weekly
                weekly_num_games[week_idx] += 1
                weekly_num_correct[week_idx] += is_correct

        # Add bowl week
        week_idx = num_weeks
        
        print(f"Processing evaluation data from year {year}, week 'bowl'...")

        scores = the_kick_is_bad.read_scores(year, "bowl")

        for game in scores["games"]:

            # Get the team names
            away_team = game["game"]["away"]["names"]["standard"]
            home_team = game["game"]["home"]["names"]["standard"]

            # Check if this is a valid game
            if game["game"]["gameState"] != "final":
                continue

            # Get the actual results
            away_score = int(game["game"]["away"]["score"])
            home_score = int(game["game"]["home"]["score"])
            if away_score > home_score:
                home_won = 0
            elif away_score < home_score:
                home_won = 1
            else:
                continue

            # Determine home field advantage
            # Assume all bowl games are neutral site
            home_field_advantage = 0

            # Get away team strength
            away_team_strength = rankings[away_team]["strength"]

            # Get home team strength and add home field advantage
            home_team_strength = rankings[home_team]["strength"] + home_field_advantage

            # Pick the winner based on team strength
            if home_team_strength >= away_team_strength:
                prediction = 1
            else:
                prediction = 0

            # Determine if the result was right
            if home_won == prediction:
                is_correct = 1
            else:
                is_correct = 0

            # Increment relevant result counters
            all_num_games += 1
            all_num_correct += is_correct
            # Bowl
            bowl_num_games += 1
            bowl_num_correct += is_correct
            # Yearly
            yearly_num_games[year_idx] += 1
            yearly_num_correct[year_idx] += is_correct
                

    # Calculate final results
    results["all"] = (all_num_correct / all_num_games) * 100
    results["conference"] = (conf_num_correct / conf_num_games) * 100
    results["non_conference"] = (nonconf_num_correct / nonconf_num_games) * 100
    results["championship"] = (champ_num_correct / champ_num_games) * 100
    results["fcs"] = (fcs_num_correct / fcs_num_games) * 100
    results["bowl"] = (bowl_num_correct / bowl_num_games) * 100
    for year_idx in range(0, end_year - start_year + 1):
        results[f"year {start_year + year_idx}"] = (yearly_num_correct[year_idx] / yearly_num_games[year_idx]) * 100
    for week_idx in range(0, max_num_weeks):
        results[f"week {1 + week_idx}"] = (weekly_num_correct[week_idx] / weekly_num_games[week_idx]) * 100

    # Save the evaluation results to file
    absolute_path = utils.get_abs_path(__file__)
    results_filename = f"{absolute_path}/model_evalation.json"
    utils.write_json(results, results_filename)


if __name__ == "__main__":
    evaluate_model()

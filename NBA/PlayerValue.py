from TeamAbbreviations import abb

import pandas as pd

# Constant for next 6 salary years, based on current contracts
SALARY_YEARS = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25', '2025-26']


def get_player_data(year):
    advanced_file = './' + year + '/PlayerAdvanced.csv'
    totals_file = './' + year + '/PlayerTotals.csv'
    contracts_file = './' + year + '/PlayerContracts.csv'

    # Import player stats
    player_advanced = pd.read_csv(advanced_file)
    player_totals = pd.read_csv(totals_file)
    player_contract = pd.read_csv(contracts_file)
    player100p = pd.read_csv("Player100p2020.csv")

    # Data cleanup
    player_advanced = player_advanced.drop_duplicates(subset='Rk')
    player_totals = player_totals.drop_duplicates(subset='Rk')
    player100p = player100p.drop_duplicates(subset='Rk')
    for index, row in player_advanced.iterrows():
        temp = row['Player']
        split = temp.split("\\")
        player_advanced.at[index, 'Player'] = split[0]
        player_totals.at[index, 'Player'] = split[0]
        player100p.at[index, 'Player'] = split[0]

    for index, row in player_contract.iterrows():
        temp = row['Player']
        split = temp.split("\\")
        player_contract.at[index, 'Player'] = split[0]
        for yr in SALARY_YEARS:
            if pd.isna(row[yr]):
                break
            temp = row[yr]
            split = temp.split("$")
            player_contract.at[index, yr] = float(split[1])

    return player_advanced, player_totals, player100p, player_contract


def calculate_player_value(player_advanced, player_totals, player100p):

    player_value = {}
    for index, row in player_advanced.iterrows():
        player = row['Player']
        advanced = row
        totals = player_totals[player_totals['Player'] == player]
        poss = player100p[player100p['Player'] == player]

        per = advanced['PER']
        minutes_played = advanced['MP']
        games_played = advanced['G']
        per_game_rating = (per * minutes_played) / (games_played * 48)

        usg = advanced['USG%']
        ts = advanced['TS%']
        ws = advanced['WS']
        vorp = advanced['VORP']

        points = totals['PTS']
        assists = totals['AST']
        rebounds = totals['TRB']
        blocks = totals['BLK']
        steals = totals['STL']
        fouls = totals['PF']
        turnovers = totals['TOV']

        personal_stats = (ts * points) + (1 * rebounds) + (2 * assists) + (4 * blocks) + (4 * steals) - (2 * fouls) - \
                         (2 * turnovers)
        personal_stats /= 100

        team_stat = 1.5 * (ws + vorp)
        usage = 0.5 * usg

        net_value = (0.5 * personal_stats) + (0.2 * per_game_rating) + (0.2 * team_stat) + (0.1 * usage)

        player_value[str(player)] = float(net_value)

        # print("Player: %s, Per game rating: %.2f, Personal stat: %.2f, Team stat: %.2f, Usage: %.2f,
        # Net Value: %.2f" % (player, per_game_rating, personal_stats, team_stat, usage, net_value))

    max_value = max(player_value.values())
    for p, v in player_value.items():
        normalized = (v * (10 ** 6)) / max_value
        player_value[p] = normalized

    sorted_player_value = sorted(player_value.items(), key=lambda item: item[1], reverse=True)
    print(sorted_player_value)
    return player_value


def calculate_player_salary(player_contract):
    player_salary = {}
    for index, row in player_contract.iterrows():
        player = row['Player']
        salary = 0
        count = 0
        for yr in SALARY_YEARS:
            if pd.isna(row[yr]):
                break
            salary += row[yr]
            count += 1
        if count == 0:
            continue
        avg_salary = salary / count
        player_salary[str(player)] = float(avg_salary)

    return player_salary


def calculate_overall_value(player_value, player_salary):
    overall_value = {}
    for p, v in player_value.items():
        if v < 500000:
            continue
        if p in player_salary:
            s = player_salary[p]
            net = v / s
            overall_value[p] = net

    sorted_overall_value = sorted(overall_value.items(), key=lambda item: item[1], reverse=True)
    print(sorted_overall_value)
    return overall_value


player_advanced, player_totals, player100p, player_contract = get_player_data('2020')
player_value = calculate_player_value(player_advanced, player_totals, player100p)
player_salary = calculate_player_salary(player_contract)
overall_value = calculate_overall_value(player_value, player_salary)
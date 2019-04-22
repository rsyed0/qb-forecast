from urllib.request import urlopen
from math import pow, log

# Default elo ranking provided
DEFAULT_ELO = 1200

# Volatility of the elo rankings
K = 20.0 

# To be implemented
ALIASES = {"Monta Vista": ["Offset","Quavo","Cupertino Scholars","Takeoff"], "BASIS": ["BASIS Silicon Valley"], "Neg 5": ["Neg5"], "Bellarmine": ["Bellarmine College Prep"]}

class DataLoad:

    def read_scoreboard(url,elo=None):
        """ Load data from a link on hsquizbowl.org """

        # Load HTML code as a str
        f = urlopen(url)
        html_data = f.read()
        line_data = [str(l) for l in html_data.splitlines()]
        data = []

        for line in line_data:
            # Parse for a game/score line
            if "<FONT SIZE=+1>" in line and "defeats" not in line:
                if "OT" in line:
                    data.append(line[line.index("<FONT SIZE=+1>")+14:-15])
                else:
                    data.append(line[line.index("<FONT SIZE=+1>")+14:-12])
                #print(line[line.index("<FONT SIZE=+1>")+14:-12])

        teams = set()
        games = []
        for line in data:
            game = dict()

            # Identify team names
            #print(line)
            team_strs = line.split(',')
            team_strs[1] = team_strs[1][1:]

            winner = team_strs[0][:team_strs[0].rfind(' ')]
            loser = team_strs[1][:team_strs[1].rfind(' ')]

            if not winner[-1].isupper():
                winner += " A"

            if not loser[-1].isupper():
                loser += " A"

            winner_school = winner[:-2]
            loser_school = loser[:-2]

            for school in list(ALIASES.keys()):
                if winner_school in ALIASES[school]:
                    winner = school+winner[-2:]
                if loser_school in ALIASES[school]:
                    loser = school+loser[-2:]

            #print("W: "+winner)
            #print("L: "+loser+"\n")

            teams.add(winner)
            teams.add(loser)

            game['date'] = 0
            game['season'] = 0
            game['neutral'] = 0
            game['playoff'] = 0

            game['team1'] = winner
            game['team2'] = loser
            game['score1'] = int(team_strs[0][team_strs[0].rfind(' ')+1:])
            game['score2'] = int(team_strs[1][team_strs[1].rfind(' ')+1:])
            game['result1'] = 1

            games.append(game)

        #print(len(teams))
        if elo is None:
            elo = dict()
            for team in teams:
                elo[team] = DEFAULT_ELO
        else:
            for team in teams:
                if team not in list(elo.keys()):
                    elo[team] = DEFAULT_ELO

        for game in games:
            # Update provisional elo rankings
            team1, team2 = game['team1'], game['team2']

            # Elo difference
            elo_diff = elo[team1] - elo[team2]

            game['elo1'] = elo[team1]
            game['elo2'] = elo[team2]

            # This is the most important piece, where we set elo_prob1 to our forecasted probability
            game['elo_prob1'] = 1.0 / (pow(10.0, (-elo_diff/400.0)) + 1.0)

            # If game was played, maintain team Elo ratings
            if game['score1'] != None:

                # Margin of victory is used as a K multiplier
                pd = abs(game['score1'] - game['score2'])
                mult = log(max(pd, 1) + 1.0) * (2.2 / (1.0 if game['result1'] == 0.5 else ((elo_diff if game['result1'] == 1.0 else -elo_diff) * 0.001 + 2.2)))

                # Elo shift based on K and the margin of victory multiplier
                shift = (K * mult) * (game['result1'] - game['elo_prob1'])

                # Apply shift
                elo[team1] += shift
                elo[team2] -= shift

        #print(elo)

        # Return dict with elo rankings/team names, and record games
        return [elo, games]

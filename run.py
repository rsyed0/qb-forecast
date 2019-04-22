from loaddata import DataLoad
from math import pow

def read_season(url_file="season.txt", game_file="season.csv", elo_file="elo.csv"):

    elo = None
    f = open(url_file, "r")
    urls = f.readlines()
    games = []
    url_num = 0

    for url in urls:
        url_num += 1
        print("Loading link "+str(url_num)+" of "+str(len(urls))+"...")
        result = DataLoad.read_scoreboard(url, elo)
        elo = result[0]
        for game in result[1]:
            games.append(game)

    # Save elo as CSV
    f = open(elo_file, "w")
    f.write("team,elo\n")

    for team in list(elo.keys()):
        print(team+": "+str(elo[team]))
        f.write(team+","+str(elo[team])+"\n")

    f.close()

    # Save games as CSV
    f = open(game_file, "w")

    keys = ["date","season","neutral","playoff","team1","team2","elo1","elo2","elo_prob1","score1","score2","result1"]
    for key in keys:
        f.write(key)
        if key != "result1":
            f.write(",")
        else:
            f.write("\n")

    for game in games:
        for key in keys:
            f.write(str(game[key]))
            if key != "result1":
                f.write(",")
            else:
                f.write("\n")

    f.close()

    return [elo, games]

def predict(team1, team2, elo):
    elo_diff = elo[team1] - elo[team2]
    return 1.0 / (pow(10.0, (-elo_diff/400.0)) + 1.0)

def main():
    elo = read_season()[0]
    for team in list(elo.keys()):
        print(team+": "+str(elo[team]))

if __name__ == "__main__":
    main()

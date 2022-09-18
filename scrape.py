import requests
from bs4 import BeautifulSoup

class Scrapper():
    
    ## 'Scrapper' object constructor
    def __init__(self):
        self.headers = {
            "User_Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }

    def get_soup(self, URL):
        response = requests.get(URL, headers=self.headers)

        html, status_code = response.text, response.status_code
        return BeautifulSoup(html, "lxml"), status_code

    def gameStats(self, number: int, match: str):
        url = f'https://www.vlr.gg/{number}/{match}/?game=all&tab=overview'
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml')
        stat_tables = soup.find_all('tbody')

        info={}

        ## Get team name
        teams = soup.find_all('div', {"class": "wf-title-med"})

        info['team-1'] = teams[0].text.strip()
        info['team-2'] = teams[1].text.strip()

        ## Gets the score
        info['team-1-score'] = soup.find('span', {'class': 'match-header-vs-score-winner'}).text.strip()
        info['team-2-score'] = soup.find('span', {'class': 'match-header-vs-score-loser'}).text.strip()

        ## Gets list of players from Team 1

        team_1_players = []

        containers = stat_tables[0].find_all('tr')
        for container in containers:
            player = container.find("div", {"class": "text-of"}).text.strip()

            team_1_players.append(
                player
            )


        info['team-1-players'] = team_1_players
        

        ## Gets list of players from Team 1

        team_2_players = []

        containers = stat_tables[1].find_all('tr')
        for container in containers:
            player = container.find("div", {"class": "text-of"}).text.strip()

            team_2_players.append(
                player
            )


        info['team-2-players'] = team_2_players
        

        ## Get average combat score for each player from Team 1 
        team_1_player_index = 1
        team_2_player_index = 1

        container = soup.find("div", attrs={'class': 'vm-stats-container'})  ## Access stat container
        tables = container.find_all("div", {'class': 'vm-stats-game'})       ## Access all stat tables
        all_map_stat_table = tables[1]                                       ## Access stat table for all maps
        all_map_stats_rows = all_map_stat_table.find_all('tr')               ## Access rows in stat table                 

        for tr in all_map_stats_rows:

            acs_kills_rows = tr.find_all('span', {"class": "side mod-side mod-both"})   ## Finds 'acs' and 'kills' stats 
            deaths_assists_rows = tr.find_all('span', {"class": "side mod-both"})       ## Finds 'deaths' and 'assists' stats

            player_stats = {}

            for i in range(0, len(acs_kills_rows), 2):
                ## Sets Team 1 player stats
                if(team_1_player_index < 5):
                    player_stats['acs'] = acs_kills_rows[0].text.strip()
                    player_stats['kills'] = acs_kills_rows[1].text.strip()
                    player_stats['deaths'] = deaths_assists_rows[0].text.strip()
                    player_stats['assists'] = deaths_assists_rows[1].text.strip()
                    info['team-1-player-'+str(team_1_player_index)+'-stats'] = player_stats
                    team_1_player_index += 1
                ## Sets Team 2 player stats
                else:
                    player_stats['acs'] = acs_kills_rows[0].text.strip()
                    player_stats['kills'] = acs_kills_rows[1].text.strip()
                    player_stats['deaths'] = deaths_assists_rows[0].text.strip()
                    player_stats['assists'] = deaths_assists_rows[1].text.strip()
                    info['team-2-player-'+str(team_2_player_index)+'-stats'] = player_stats
                    team_2_player_index += 1
                
        return info



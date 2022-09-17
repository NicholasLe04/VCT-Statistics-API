import requests
from bs4 import BeautifulSoup

class Scrapper():
    
    def __init__(self):
        self.headers = {
            "User_Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/14.0.3 Safari/7046A194A"
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

        container = soup.find("div", attrs={'class': 'vm-stats-container'})
        tables = container.find_all("div", {'class': 'vm-stats-game'})      ## Access all stat tables
        all_map_stat_table = tables[1]                                      ## Access stat table for all maps
        all_map_stats_rows = all_map_stat_table.find_all('tr') 
        #all_map_stats = all_map_stats_row.find('td'), {'class': 'mod-stat'} 
        # all_map_acs = all_map_stats[0].find_all('span', {"class": "side mod-side mod-both"})                                   

        for tr in all_map_stats_rows:

            acs_kills_rows = tr.find_all('span', {"class": "side mod-side mod-both"})

            player_stats = {}

            for i in range(0, len(acs_kills_rows), 2):
                if(team_1_player_index < 5):
                    player_stats['acs'] = acs_kills_rows[0].text.strip()
                    player_stats['kills'] = acs_kills_rows[1].text.strip()
                    info['team-1-player-'+str(team_1_player_index)+'-stats'] = player_stats
                    team_1_player_index += 1
                else:
                    player_stats['acs'] = acs_kills_rows[0].text.strip()
                    player_stats['kills'] = acs_kills_rows[1].text.strip()
                    info['team-2-player-'+str(team_2_player_index)+'-stats'] = player_stats
                    team_2_player_index += 1
                
            

                
                # if(team_1_player_index <= 5):
                #     info['team-1-player-'+str(team_1_player_index)+'-acs'] = acs_kills_rows[0].text.strip()
                #     info['team-1-player-'+str(team_1_player_index)+'-kills'] = acs_kills_rows[1].text.strip()
                #     team_1_player_index += 1
                # else:
                #     info['team-2-player-'+str(team_2_player_index)+'-acs'] = acs_kills_rows[0].text.strip()
                #     info['team-2-player-'+str(team_2_player_index)+'-kills'] = acs_kills_rows[1].text.strip()
                #     team_2_player_index += 1



        
        print(info)





matches = Scrapper()

matches.gameStats('130691', 'optic-gaming-vs-drx-valorant-champions-2022-lbf')


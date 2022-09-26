import requests
from bs4 import BeautifulSoup
import json


class Scrapper():
    
    ## Loads team page ID's to access team page urls
    with open('JsonFiles/teamids.json') as ids:
        teamIDs = json.load(ids)

    with open('JsonFiles/playerids.json') as ids:
        playerIDs = json.load(ids)

    with open('JsonFiles/flags.json') as flags:
        flagEmojis = json.load(flags)

    ## 'Scrapper' object constructor
    def __init__(self):
        self.headers = {
            "User_Agent": ""
        }

    #############################
    #                           #
    #         MATCH DATA        #
    #                           #
    #############################

    ## Gets and returns ARRAY of team names 
    #  example output: ['OpTic Gaming', 'Sentinels']
    #  example usage: 'ScrapperObject'.getTeams(url)[0] = 'OpTic Gaming'
    def getTeams(self, match_id):    
        html = requests.get('https://www.vlr.gg/' + str(match_id))
        soup = BeautifulSoup(html.content, 'lxml')

        # Finds the div's holding team names
        teams = soup.find_all('div', {"class": "wf-title-med"})
        return [teams[0].text.strip(), teams[1].text.strip()]       


    ## Gets and returns ARRAY of score from match 
    #  example output: [2,1]
    #  example usage: ScrapperObject'.getScore(url)[0] = 2
    def getScore(self, match_id):
        html = requests.get('https://www.vlr.gg/' + str(match_id))
        soup = BeautifulSoup(html.content, 'lxml')
        
        return [int(soup.find('span', {'class': 'match-header-vs-score-winner'}).text.strip()), 
                int(soup.find('span', {'class': 'match-header-vs-score-loser'}).text.strip())]
        

    ## Gets and returns DICTIONARY filled with ARRAYS of map scores 
    #  example ouput: {'map-1': [15, 13], 'map-2': [6, 13], 'map-3': [16, 14], 'map-4': [13, 5]}
    #  example usage: 'ScrapperObject'.getMapScores(url).get('map-1') = [15, 13]
    def getMapScores(self, match_id: int):
        html = requests.get('https://www.vlr.gg/' + str(match_id))
        soup = BeautifulSoup(html.content, 'lxml')
        map_scores = soup.find_all('div', {'class': 'score'})

        output = {}
        
        for i in range(0, len(map_scores), 2):
            output['map-' + str(int(i/2) + 1)] = [int(map_scores[i].text.strip()), int(map_scores[i+1].text.strip())]
        
        return output

    ## Gets and returns ARRAY filled with DICTIONARIES for each player's info/stats 
    def getPlayerStats(self, match_id: int):
        html = requests.get('https://www.vlr.gg/' + str(match_id))
        soup = BeautifulSoup(html.content, 'lxml')
        stat_tables = soup.find_all('tbody')    # Finds all table body elements
        player_index = 0

        output = []

        container = soup.find("div", attrs={'class': 'vm-stats-container'})  # Access stat container
        tables = container.find_all("div", {'class': 'vm-stats-game'})       # Access all stat tables
        all_map_stat_table = tables[1]                                       # Access stat table for all maps
        all_map_stats_rows = all_map_stat_table.find_all('tr')               # Access rows in stat table                 

        for tr in all_map_stats_rows:   # For each row in all map stat rows

            acs_kills_rows = tr.find_all('span', {"class": "side mod-side mod-both"})   # Finds 'acs' and 'kills' stats 
            #deaths_assists_rows = tr.find_all('span', {"class": "side mod-both"})       # Finds 'deaths' and 'assists' stats
            team_1 = stat_tables[2].find_all('tr')  # Finds the team 1 player stat elements
            team_2 = stat_tables[3].find_all('tr')  # Finds the team 2 player stat elements

            for i in range(0, len(acs_kills_rows), 2):  # Iterate through all acs and kill elements
                if (player_index < 5):
                    output.append([team_1[player_index].find("div", {"class": "text-of"}).text.strip(), int(acs_kills_rows[0].text.strip())])
                else:
                    output.append([team_2[player_index-5].find("div", {"class": "text-of"}).text.strip(), int(acs_kills_rows[0].text.strip())])
                player_index += 1

        return output


    ## Gets all game stats (Teams, score, players, acs, K/D/A)
    def getMatchStats(self, match_id):
        info={}

        ## Get team names
        info['teams'] = self.getTeams(match_id)

        ## Gets the final score
        info['score'] = self.getScore(match_id)

        ## Gets individual map scores
        info['map-scores'] = self.getMapScores(match_id)

        ## Get ACS, Kills, Deaths, and Assists for each player
        info['player-stats'] = self.getPlayerStats(match_id)
                

        return info

    ## Gets and returns url to the overview page of the most recent match on vlr.gg/matches/results
    def getRecentUrl(self):
        html = requests.get('https://www.vlr.gg/matches/results')
        soup = BeautifulSoup(html.content, 'lxml')

        url = 'https://www.vlr.gg' + soup.find('a', {'class': 'match-item'}).get('href')    # Gets and returns url to the overview page of the most recent match on vlr.gg/matches/results
        return url


    #############################
    #                           #
    #   INDIVIDUAL TEAM DATA    #
    #                           #
    #############################
    
    ##  Returns an ARRAY filled with DICTIONARIES of all the players IGNs and url's to their images
    #   example output: [{'name 1': 'vanity', 'image 1': 'https://owcdn.net/img/6224a530d0113.png'}, 'name 2': 'curry', 'image 2': 'https:/img/base/ph/sil.png'}, etc.]
    #   example usage: 'ScrapperObject'.getPlayers('cloud9') = [{'name 1': 'vanity', 'image 1': 'https://owcdn.net/img/6224a530d0113.png'}, etc.]
    def teamGetPlayers(self, team: str):
        url = 'https://www.vlr.gg/team/' + str(self.teamIDs.get(team.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml')
        player_table = soup.find_all('div', {'class': 'wf-card'})
        player_names = player_table[1].find_all('div', {'class': 'team-roster-item-name-alias'})    # Find all in-game names

        output = []
        
        # player_names = player_table.find_all('div', {'class': 'team-roster-item-name-alias'})
        player_image_urls = player_table[1].find_all('img')
        

        for i in range(5):  # player_data['name ' + str(i)] = player_images[i].get('src')
            output.append(
                {'name ' + str(i+1): player_names[i].text.strip(),
                'image ' + str(i+1): 'https:' + player_image_urls[i].get('src')}
            )

        return output

    def teamGetName(self, team: str):
        url = 'https://www.vlr.gg/team/' + str(self.teamIDs.get(team.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        return soup.find('h1', {'class': 'wf-title'}).text.strip()

    def teamGetLogo(self, team: str):
        url = 'https://www.vlr.gg/team/' + str(self.teamIDs.get(team.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        return 'https:' + soup.find('div', {'class': 'wf-avatar team-header-logo'}).find('img').get('src')



    ##############################
    #                            #
    #   INDIVIDUAL PLAYER DATA   #
    #                            #
    ##############################

    ## Returns player_name's team
    #  Example: scrapper.playerGetTeam('tenz') = 'Sentinels'
    def playerGetTeam(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        try:
            return soup.find_all('div', {'class': 'wf-card'})[2].find('div', {'style': 'font-weight: 500;'}).text.strip()
        except:
            return 'no team' 

    ## Returns 'player_name''s real name 
    #  Example: scrapper.playerGetName('tenz') = 'Tyson Ngo'
    def playerGetName(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        return soup.find('h2', {'class': 'player-real-name'}).text.strip()

    ## Returns player_name's username witch correct capitalization
    #  Example: scrapper.playerGetTeam('tenz') = 'TenZ'
    def playerGetUsername(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        return soup.find('h1', {'class': 'wf-title'}).text.strip()

    ## Returns player_name's picture or default image url
    #  Example: scrapper.playerGetPicture('tenz') = 'https://www.vlr.gg/img/base/ph/sil.png'
    def playerGetPicture(self, player_name:str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        image = 'https:' + soup.find('div', {'class': 'wf-avatar'}).find('img').get('src')
        if image == "https:/img/base/ph/sil.png":
            return  "https://www.vlr.gg/img/base/ph/sil.png"
        else:
            return image

    ## Returns player_name's country/region
    #  Example: scrapper.playerGetRegion('tenz') = 'CANADA'
    def playerGetRegion(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        return soup.find('div', {'class': 'ge-text-light'}).text.strip()

    ## Returns player_name's country/region flag emoji
    #  Example: scrapper.playerGetPicture('tenz') = ':flag_ca:'
    def playerGetRegionFlag(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower()))  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        region = soup.find('div', {'class': 'ge-text-light'}).text.strip()
        return self.flagEmojis.get(region)
        
    ## Returns player_name's average ACS over the past 90 days
    #  Example: scrapper.playerGetPicture('tenz') = '229.6'
    def playerGetGlobalACS(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower())) + '/?timespan=90d'  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        try:
            return float(soup.find('tbody').find('tr').find_all('td')[4].text.strip())
        except: 
            return 0.0

    ## Returns player_name's average K/D over the past 90 days
    #  Example: scrapper.playerGetPicture('tenz') = '1.2'
    def playerGetGlobalKD(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower())) + '/?timespan=90d'  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        try:
            return float(soup.find('tbody').find('tr').find_all('td')[5].text.strip())
        except:
            return 0.0
    
    ## Returns player_name's average kills per round over the past 90 days
    #  Example: scrapper.playerGetPicture('tenz') = '0.84'
    def playerGetGlobalKPR(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower())) + '/?timespan=90d'  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        try:
            return float(soup.find('tbody').find('tr').find_all('td')[8].text.strip())
        except:
            return 0.0

    ## Returns player_name's average assists per round over the past 90 days
    #  Example: scrapper.playerGetPicture('tenz') = '0.11'
    def playerGetGlobalAPR(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower())) + '/?timespan=90d'  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        try:
            return float(soup.find('tbody').find('tr').find_all('td')[9].text.strip())
        except:
            return 0.0

    ## Returns player_name's most played agent over the past 90 days
    #  Example: scrapper.playerGetPicture('tenz') = 'Chamber'
    def playerGetAgent(self, player_name: str):
        url = 'https://www.vlr.gg/player/' + str(self.playerIDs.get(player_name.lower())) + '/?timespan=90d'  # Navigate to the specified team page 
        html = requests.get(url)
        soup = BeautifulSoup(html.content, 'lxml') 
        try:
            agent_url = soup.find('tbody').find('tr').find('td').find('img').get('src')
            return agent_url[21:len(agent_url)-4]
        except:
            return 'no agent'

    

## TESTING 
scrapper = Scrapper()
url = scrapper.getRecentUrl()




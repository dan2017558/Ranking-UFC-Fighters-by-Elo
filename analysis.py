from bs4 import BeautifulSoup
import requests
import pandas as pd
from fighters import fighter_elos as elos

# Get ufc database and events
html_text = requests.get("http://ufcstats.com/statistics/events/completed?page=all").text
soup = BeautifulSoup(html_text, "lxml")
events = soup.find_all("a", class_="b-link b-link_style_black", href=True)  # doesn't include ufc 1

# Add ufc 1
html_text = requests.get("http://ufcstats.com/statistics/events/search?query=ufc%201&page=all").text
soup = BeautifulSoup(html_text, "lxml")
ufc1 = soup.find_all("a", class_="b-link b-link_style_black", href="http://ufcstats.com/event-details/6420efac0578988b")

events.append(ufc1[0])

# Initialize scores and track records
scores = {"win": 1, "draw": 0.5, "nc": False}
track_records = elos.copy()

def get_round(fight):
    # Compress the info data
    info = fight.text.replace("\n", " ").split()
    round_num = info[-2]
    return round_num

# Looping through each event in reverse chronological order
for event in reversed(events):

    # UFC event
    result_link = event["href"]
    text = requests.get(result_link).text
    soup = BeautifulSoup(text, "lxml")

    # Retrieve fights and other details
    fights = soup.find_all("tr", class_="b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click")
    fighters = soup.find_all("a", class_="b-link b-link_style_black")
    results = soup.find_all("i", class_="b-flag__text")

    # Loop through fights in reverse order
    for i in reversed(range(len(fighters) // 2)):
        round_num = int(get_round(fights[i]))
        fighter1_score = scores[results[i].text]

        if fighter1_score:
            # Update scores based on round_num stoppage
            if fighter1_score == 1:
                fighter1_score += round_num**-1
            fighter2_score = 1 - fighter1_score

            # Fighters' names
            fighter1 = fighters[i * 2].text.strip()
            fighter2 = fighters[i * 2 + 1].text.strip()

            # Calculate win probability
            fighter1_win_prob = (1 + 10**((elos[fighter2][0] - elos[fighter1][0]) / 400))**-1
            fighter2_win_prob = 1 - fighter1_win_prob

            # Calculate new elo
            fighter1_elo_change = round(150 * (fighter1_score - fighter1_win_prob), 2)
            fighter2_elo_change = round(150 * (fighter2_score - fighter2_win_prob), 2)

            # Update Elo ratings
            elos[fighter1][0] = round(elos[fighter1][0] + fighter1_elo_change, 2)
            elos[fighter2][0] = round(elos[fighter2][0] + fighter2_elo_change, 2)

            # Track records
            track_records[fighter1].append([fighter1, elos[fighter1][0], fighter2, fighter1_elo_change])
            track_records[fighter2].append([fighter2, elos[fighter2][0], fighter1, fighter2_elo_change])

# Print results sorted by Elo ratings
result = {k: v for k, v in sorted(track_records.items(), key=lambda item: item[1], reverse=True)}
for key in result:
    for i in range(1, len(result[key])):  # Skip the first entry
        print(f"{result[key][i][0]},{result[key][i][1]},{result[key][i][2]},{result[key][i][3]}")

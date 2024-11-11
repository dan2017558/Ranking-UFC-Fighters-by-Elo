from bs4 import BeautifulSoup
import requests
from fighters import fighters as fighters

# get ufc database and events
html_text = requests.get("http://ufcstats.com/statistics/events/completed?page=all").text
soup = BeautifulSoup(html_text, "lxml")
events = soup.find_all("a", class_ = "b-link b-link_style_black", href=True) # doesn't include ufc 1

# add ufc 1
html_text = requests.get("http://ufcstats.com/statistics/events/search?query=ufc%201&page=all").text
soup = BeautifulSoup(html_text, "lxml")
ufc1 = soup.find_all("a", class_ = "b-link b-link_style_black", href="http://ufcstats.com/event-details/6420efac0578988b")

events.append(ufc1[0])

# looping through each event in chronological order

scores = {"win": 1, "draw": 0.5, "nc": False}

for event in range(len(events) - 1, -1, -1):
    
    print(f"{len(events) - event} / {len(events)} completed")  # loading progression
    result_link = events[event]["href"]  # get event results link
    text = requests.get(result_link).text

    soup = BeautifulSoup(text, "lxml")
    results = soup.find_all("i", class_ = "b-flag__text")  # possibilities: nc win draw 
    names = soup.find_all("a", class_ = "b-link b-link_style_black")  # get fighter names
    
    for i in range(len(names)//2 - 1, -1, -1): # each fight in chronological order
        
        fighter1_score = scores[results[i].text]

        if fighter1_score:
            
            # opponents score
            fighter2_score = 1 - fighter1_score

            # names
            fighter1 = names[i*2].text.strip()
            fighter2 = names[(i*2)+1].text.strip()

            if fighter1 == 0.5:
                print(fighter1)

            # calculate win likelihood
            # win probibility -> P(A wins) = 1 / {1 + 10^[(RB - RA) / 400]}
            fighter1_win_probibility = (1 + 10**((fighters[fighter2] - fighters[fighter1])/400))**-1
            fighter2_win_probibility = 1 - fighter1_win_probibility

            # calculate new elo -> New elo = elo + 32(score - win probiblity)
            fighters[fighter1] = fighters[fighter1] + 32*(fighter1_score - fighter1_win_probibility)
            fighters[fighter2] = fighters[fighter2] + 32*(fighter2_score - fighter2_win_probibility)


# print results
result = {k: v for k, v in sorted(fighters.items(), key=lambda item: item[1], reverse=True)}
for key in result:
    print(f"{key}, {result[key]}")
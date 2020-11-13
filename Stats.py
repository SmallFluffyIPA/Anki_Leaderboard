import time
from datetime import date, timedelta
import datetime

from aqt import mw
from aqt.utils import showInfo

def Stats(season_start, season_end):
	config = mw.addonManager.getConfig(__name__)
	new_day = datetime.time(int(config['newday']),0,0)
	time_now = datetime.datetime.now().time()
	Streak = streak(config, new_day, time_now)

	cards_past_30_days = reviews_past_31_days(new_day, time_now)
	total_cards, retention = reviews_and_retention_today(new_day, time_now)
	time_today = time_spend_today( new_day, time_now)

	league_reviews, league_retention = league_reviews_and_retention(season_start, season_end)
	league_time = league_time_spend(season_start, season_end)

	return(Streak, total_cards, time_today, cards_past_30_days, retention, league_reviews, league_time, league_retention)


def get_reviews_and_retention(start_date, end_date):
    start = int(start_date.timestamp()*1000)
    end = int (end_date.timestamp()*1000)
    reviews = mw.col.db.scalar("SELECT COUNT(*) FROM revlog WHERE id >= ? AND id < ?", start, end) 
    flunked_total = mw.col.db.scalar("SELECT COUNT(*) FROM revlog WHERE ease == 1 AND id >= ? AND id < ?", start, end) 
    
    if reviews == 0:
        return 0, 0
    
    retention = round((100/reviews)*(reviews-flunked_total) ,1)
    return reviews, retention

def get_time_spend(start_date, end_date):
    start = int(start_date.timestamp()*1000)
    end = int(end_date.timestamp()*1000)
    
    time = mw.col.db.scalar("SELECT SUM(time) FROM revlog WHERE id >= ? AND id < ?", start, end)
    time = round(time / 60000, 1)
    return time


###LEADERBOARD###

def streak(config, new_day, time_now):
	new_day_shift_in_ms= int(config['newday'])*60*60*1000
	date_list = []
	Streak = 0

	date_list = mw.col.db.list("SELECT DISTINCT strftime('%Y-%m-%d',datetime((id-?)/1000, 'unixepoch')) FROM revlog ORDER BY id DESC;", new_day_shift_in_ms)
	
	if time_now < new_day:
		start_date = date.today() - timedelta(days=1)
	else:
		start_date = date.today()

	end_date = date(2006, 10, 15)
	delta = timedelta(days=1)
	while start_date >= end_date:
		if start_date.strftime("%Y-%m-%d") in date_list:
			Streak = Streak + 1
		else:
			break
		start_date -= delta

	return Streak

def reviews_past_31_days(new_day, time_now):
	# Start of next day because time < end_day
	if time_now < new_day:
		end_day = datetime.datetime.combine(date.today() + timedelta(days=1), new_day)
	else:
		end_day = datetime.datetime.combine(date.today() + timedelta(days=2), new_day)

	start_day = datetime.datetime.combine(date.today() - timedelta(days=30), new_day)
	reviews, _ =  get_reviews_and_retention(start_day, end_day)
	return reviews

def reviews_and_retention_today(new_day, time_now):
	if time_now < new_day:
		start_day = datetime.datetime.combine(date.today() - timedelta(days=1), new_day)
	else:
		start_day = datetime.datetime.combine(date.today(), new_day)
	return get_reviews_and_retention(start_day, start_day+timedelta(days=1))

def time_spend_today(new_day, time_now):	
	if time_now < new_day:
		start_day = datetime.datetime.combine(date.today() - timedelta(days=1), new_day)
	else:
		start_day = datetime.datetime.combine(date.today(), new_day)

	return get_time_spend(start_day, start_day + timedelta(days=1))

###LEAGUE###

def league_reviews_and_retention(season_start, season_end):
	return get_reviews_and_retention(season_start, season_end)

def league_time_spend(season_start, season_end):
	return get_time_spend(season_start, season_end)

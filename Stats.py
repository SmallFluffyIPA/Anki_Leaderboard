import time
from datetime import date, timedelta
import datetime
from aqt import mw
from os.path import dirname, join, realpath
from aqt.utils import showInfo, tooltip

def Stats():

	###STREAK, REVIEWS PAST 31 DAYS###
	config = mw.addonManager.getConfig(__name__)
	new_day = datetime.time(int(config['newday']),0,0)
	time_now = datetime.datetime.now().time()
	reviews = mw.col.db.list("SELECT id FROM revlog")
	
	###STREAK####
	
	newday = int(config['newday'])
	date_list = []
	Streak = 0
	for i in reviews:
		normal = time.strftime('%Y-%m-%d', time.localtime(int(i)/1000.0))
		i = time.strftime('%Y-%m-%d-%H', time.localtime(int(i)/1000.0))
		i = i.split("-")
		if int(i[3]) < newday:
			old_date = datetime.date(int(i[0]), int(i[1]), int(i[2]))
			one_day = datetime.timedelta(1)
			new_date = old_date - one_day
			date_list.append(str(new_date))
		else:
			date_list.append(normal)
	
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

	###REVIEWS PAST 31 DAYS###
	
	if time_now < new_day:
		start_day = datetime.datetime.combine(date.today(), new_day)
	else:
		start_day = datetime.datetime.combine(date.today() + timedelta(days=1), new_day)

	end_day = datetime.datetime.combine(date.today() - timedelta(days=30), new_day)

	cards_past_30_days = 0

	for i in reviews:
		i = datetime.datetime.fromtimestamp(i/1000.0)
		if i >= end_day and i <= start_day:
			cards_past_30_days = cards_past_30_days + 1

	#REVIEWS TODAY AND RETENTION###

	if time_now < new_day:
			start_day = datetime.datetime.combine(date.today() - timedelta(days=1), new_day)
	else:
		start_day = datetime.datetime.combine(date.today(), new_day)

	total_cards = 0
	flunked_total = 0
	data = mw.col.db.execute("SELECT * FROM revlog")
	for i in data:
		id_time = i[0]
		flunked = i[3]
		id_time = datetime.datetime.fromtimestamp(int(id_time)/1000.0)
		if id_time > start_day:
			total_cards += 1
			###RETENTION###
			if flunked == 1:
				flunked_total += 1
	try:
		retention = round(100 - (100/total_cards*flunked_total), 1)
	except:
		retention = ""

	###TIME SPEND TODAY###
	
	time_today = 0
	for i in data:
		id_time = i[0]
		id_time = datetime.datetime.fromtimestamp(int(id_time)/1000.0)
		if id_time > start_day:
			time_today = time_today + int(i[7])
	time_today = round(time_today/60000, 1)

	return(Streak, total_cards, time_today, cards_past_30_days, retention)
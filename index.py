#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.contrib.fixers           import ProxyFix
from pytg                              import Telegram
from flask                             import Flask
from flask                             import request
from flask                             import render_template
from flask_basicauth                   import BasicAuth
from pygal.style                       import Style
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval     import IntervalTrigger
from shutil                            import copyfile
import atexit
import datetime
import jinja2
import pygal
import random
import time
import subprocess
import os

app                               = Flask(__name__)
LOGIN                             = 'admin'
PSWRD                             = 'kogzgsf19'
FORCE                             = False
HM                                = 'please log in:'
app.config['BASIC_AUTH_USERNAME'] = LOGIN
app.config['BASIC_AUTH_PASSWORD'] = PSWRD
app.config['BASIC_AUTH_FORCE']    = FORCE
app.config['BASIC_AUTH_REALM']    = HM
basic_auth                        = BasicAuth(app)
tg                                = Telegram(
                                    telegram    = "tg/bin/telegram-cli",
                                    pubkey_file = "tg/tg-server.pub",
                                    port        = 4550)
receiver                          = tg.receiver
sender                            = tg.sender
APP_ROOT                          = os.path.dirname(
                                    os.path.abspath(__file__))
db                                = "db/db.txt"
requests_today                    = 0

def null_requests():
    global requests_today
    requests_today = 0

def updb():
    copyfile('db/db.txt', 'db/dblog.txt')
    global requests_today
    steps = 0
    db    = 'db/db.txt'
    pdb   = open(db,'r')
    res   = pdb.read().splitlines()
    pdb.close()
    if requests_today + len(res) < 250:
        udb = open(db, 'w')
        for line in res:
            tmp            = line.split(':')
            chname         = tmp[0]
    	    requests_today += 1
    	    chid           = sender.resolve_username(chname)['id']
    	    seek           = 'participants_count'
            temp           = sender.channel_info(chid)
            temp           = temp.get(seek, None)
            if tmp[1].split(',')[0]=='':
    	        if temp == None:
    		        udb.write(str('%s%s###%s\n' % (line,0,datetime.datetime.now().strftime ("%d.%m.%Y %H.%M"))).decode('utf-8'))
                else:
    		        udb.write(str('%s%s###%s\n' % (line,temp,datetime.datetime.now().strftime ("%d.%m.%Y %H.%M"))).decode('utf-8'))
            else:
    	        if temp == None:
    		        udb.write(str('%s,%s###%s\n' % (line,0,datetime.datetime.now().strftime ("%d.%m.%Y %H.%M"))).decode('utf-8'))
                else:
    		        udb.write(str('%s,%s###%s\n' % (line,temp,datetime.datetime.now().strftime ("%d.%m.%Y %H.%M"))).decode('utf-8'))
    	    if steps >= 0:
    	        if steps >= 10:
    		        time.sleep(20)
    		        steps = 0
    	        else:
    	    	    time.sleep(5)
            steps += 1
        udb.close()
        return True
    else:
	    return False

def cover_db():
    copyfile('~/db/db.txt', '~/db/dblog.txt')

def check_at_symbol(chname):
    if chname[0] == '@':
        chname = chname.replace('@','')
    return chname

@app.before_first_request
def initialize():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
    	func=null_requests,
    	trigger=IntervalTrigger(seconds=86400),
    	id='checker_job',
    	name='Checking if it is requests limit for today',
    	replace_existing=False)
    scheduler.add_job(
        func=updb,
	    trigger=IntervalTrigger(seconds=86400),
        id='updating_job',
        name='Updating channels db every 24 hours',
        replace_existing=False)
    scheduler.add_job(
    	func=cover_db,
    	trigger=IntervalTrigger(seconds=14399),
    	id='coverdb',
    	name='covers existing db to be safe',
    	replace_existing=False)
    atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def index():
    return render_template("index.html", title="ANAGRAM | The first and the best")

@app.route('/add/<channelnames>')
def adding(channelnames):
    channelnames = channelnames.split(',')
    for i in range(0,len(channelnames)):
        channelnames[i] = check_at_symbol(channelnames[i])
        channelnames[i] = channelnames[i].replace('\n', '')
    global requests_today
    if requests_today+len(channelnames) < 250:
        for channelname in channelnames:
            requests_today += 1
            channels = []
            f = open(db, 'r')
            lines = f.read().splitlines()
            f.close()
            for line in lines:
                channels.append(line.split(':')[0])
            if channelname not in channels:
                try:
                    chid = sender.resolve_username(channelname.rstrip())['id']
                except:
                    chid = channelname
                chid = chid.replace('\n', '')
                sender.channel_join(chid)
                a = open(db, 'a')
                a.write("%s:\n" % channelname)
                a.close()
                time.sleep(5)
        return render_template("added.html", title="ANAGRAM | Succefully added!", channelname = channelname)
    else:
        return render_template("runoutofrequests.html", title="ANAGRAM | Ran out of requests!")

@app.route('/delete/<channelnames>')
def delete(channelnames):
    channelnames = channelnames.split(",")
    for i in range(0, len(channelnames)):
        channelnames[i] = check_at_symbol(channelnames[i])
    global requests_today
    if requests_today+len(channelnames) < 250:
        for channelname in channelnames:
            requests_today += 1
            found          = False
            channels       = []
            channels_res   = []
            f              = open(db, 'r')
            lines          = f.read().splitlines()
            f.close()
            w              = open(db, 'w')
            for line in lines:
                if line.split(':')[0] != channelname:
                    w.write("%s\n" % line)
                else:
                    try:
                        chid = sender.resolve_username(channelname.rstrip())['id']
                    except:
                        chid = channelname
                    sender.channel_leave(chid)
                    found = True
        return render_template("deleted.html", title = "ANAGRAM | Successfully deleted!", channelname = channelname)
    else:
        return render_template("runoutofrequests.html", title = "ANAGRAM | Ran out of requests, try later")

@app.route('/info/<channelname>')
def info(channelname):
    channelname = check_at_symbol(channelname)
    global requests_today
    if requests_today + 1 < 250:
        requests_today += 1
        chid = sender.resolve_username(channelname)['id']
        seek = u'participants_count'
        tmp  = sender.channel_info(chid)
        res  = tmp.get(seek, None)
        if res != None:
            return render_template("info.html", title="ANAGRAM | Channel info up to date", channelname = channelname, count = res)
        else:
            return render_template("notfound.html", title="ANAGRAM | Channel not found!", channelname = channelname)
    else:
        return render_template("notfound.html", title="ANAGRAM | Too many requests for today", channelname = channelname)

@app.route("/update")
def update():
    if updb():
        return render_template("updated.html", title="ANAGRAM | Successful update")
    else:
        return render_template("history.html", title="ANAGRAM | Update was done before")

@app.route("/history")
def history():
    cdb     = open(db,'r')
    res     = cdb.read().splitlines()
    rands   = []
    charts  = []
    i       = 0
    c_style = Style(
    	background='transparent',
    	plot_background='#FFFFFF',
    	opacity='.2',
      	opacity_hover='.6',
    	colors=('#53A0E8',)
    )
    for channel in res:
        i         += 1
        p         = 0
        rnums     = []
        xlabels   = []
        iterator  = channel.split(':')[1].split(',')
        bar_chart = pygal.Line(fill=True, show_x_labels=False, style=c_style)
        bar_chart.title = channel.split(':')[0]
        for xs in iterator:
            date = xs.split('###')[1]
            num  = p
        xlabels.append(date)
        p += 1
        bar_chart.x_labels = xlabels
        for nums in iterator:
	        rnums.append(int(nums.split('#')[0]))
	bar_chart.add(channel.split(':')[0], rnums)
    bar_chart.render_to_file('{}/static/{}.svg'.format(APP_ROOT, i))
    rands.append(random.randint(1, 120492198))
    return render_template("history.html", title="ANAGRAM | History line as graphs", charts = i, rands = rands)

@app.route("/history_alt", methods=['POST','GET'])
def hstory_alt():
    cdb = open(db,'r')
    if request.method == 'POST':
    	sd          = datetime.datetime.strptime(request.form['startdate'], '%m/%d/%Y')
    	ed          = datetime.datetime.strptime(request.form['enddate'], '%m/%d/%Y')
    	channel_tmp = ''
    	channels    = []
    	arr_result  = []
    	lines       = cdb.read().splitlines()
    	for line in lines:
    	    splitted      = line.split(':')
    	    channel_name  = splitted[0]
    	    channel_tmp   = splitted[1].split(',')
    	    channels_temp = []
    	    for channel in channel_tmp:
        		update_date = datetime.datetime.strptime(channel.split('###')[1].split(' ')[0], '%d.%m.%Y')
        		if update_date >= sd and update_date <= ed:
        		    channels_temp.append(channel)
        if len(channels_temp) != 0:
            arr_result.append('%s:%s' % (channel_name, ','.join(channels_temp)))
    	res = arr_result
    else:
        res = cdb.read().splitlines()
        return render_template("history_alt.html", title="ANAGRAM | History line as table", channels = res)


@app.route("/channels")
def channels():
    cdb = open(db, 'r')
    res = cdb.read().splitlines()
    return render_template("channels.html", title="ANAGRAM | Channels database", data = res)

@app.route("/ad", methods=['POST','GET'])
def ad_repost():
    if request.method == 'POST':
    	acceptors = request.form['accs']
    	acceptors = acceptors.replace(' ','')
    	donors = request.form['dnrs']
    	donors = donors.replace(' ','')
    	if acceptors != '' and donors != '':
    	    times = request.form['tms']
    	    if times == '':
    	        times = 9999
    	    lag = request.form['lag']
    	    if lag == '':
    	        lag = 90
    	    age = request.form['age']
    	    if age == '':
    	        age = 30
    	    subprocess.call("nohup python ./mainAD.py '%s' '%s' %s %s %s &" % (acceptors, donors, times, lag, age), shell=True)
    	    return render_template("ad.html", title="ANAGRAM | A-D repost started!")
    	else:
    	    return render_template("aderror.html", title="ANAGRAM | Error")
    else:
	    return render_template("ad.html", title="ANAGRAM | A-D repost request page")

@app.route("/grubtg", methods=["POST","GET"])
def grubtg():
    if request.method == 'POST':
    	to_send    = request.form['snd']
    	to_send    = to_send.replace(' ','')
    	to_grub_tg = request.form['grbtg']
    	to_grub_tg = to_grub_tg.replace(' ','')
    	exp_pst    = request.form['num']
    	if to_send != '':
    	    subprocess.call("nohup python ./grub.py '%s' '%s' %s &" % (to_grub_tg, to_send, exp_pst), shell=True)
    	    return render_template("grubtg.html", title="ANAGRAM | GRUB started!")
    	else:
    	    return render_template("grubtg.html", title="ANAGRAM | Error")
    else:
	    return render_template("grubtg.html", title="ANAGRAM | GRUB request page")

# @app.route("/grubinsta", methods=["POST","GET"])
# def grubinsta():
#     if request.method == 'POST':
#         to_send      = request.form['snd']
#         to_send      = to_send.replace(' ','')
#         to_grub_inst = request.form['grbinst']
#         to_grub_inst = to_grub_inst.replace(' ','')
#         exp_pst      = request.form['num']
#         if to_send != '':
#             subprocess.call("nohup python ./instaAD.py '%s' '%s' '%s' %s &" % ('', to_grub_inst, to_send, exp_pst), shell=True)
#             return render_template("grubinsta.html", title="ANAGRAM | GRUB started!")
#         else:
#             return render_template("grubinsta.html", title="ANAGRAM | Error")
#     else:
#         return render_template("grubinsta.html", title="ANAGRAM | GRUB request page")

app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001)

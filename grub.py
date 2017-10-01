#!/usr/bin/python

##################################################
##################################################
########## Created by Romanov Alexandr ###########
####### Current version: 0.2v (15.09.2016) #######
########## Contact me via tlgrm: @rmnff ##########
##################################################
##################################################

from __future__    import unicode_literals
from pytg          import Telegram
from pytg.receiver import Receiver
from pytg.sender   import Sender
from pytg.utils    import coroutine
import sys
import os
import thread
import math
import datetime
import time
import random
import re
import requests
import urllib
import json
import calendar

PATH_TO_DOWNLOADED = "/Users/alexofcats/.telegram-cli/downloads/"

class acceptor_object(object):
    clist = []
    rlist = []
    hlist = []
    count = 1
    start = 0
    end   = count-1

    def __init__(self, l):
        self.clist = l
        self.count = len(l)
        self.end = self.count-1

    def get_arr(self):
        return self.rlist

    def check_offset(self):
        vfc = self.clist.pop(0)
        vfh = self.hlist.pop(0)
        vfr = self.rlist.pop(0)
        self.clist.append(vfc)
        self.hlist.append(vfh)
        self.rlist.append(vfr)

    def reveal_all(self, sender):
        found = False
        for item in self.clist:
            item = item.replace('@', '')
            item = item.replace(' ', '_')
            if not found:
                new_cont = sender.resolve_username(item)
                self.rlist.append(new_cont['id'])

    def drop_history(self):
        self.hlist = []

    def get_histories(self, sender):
        limit = 1
        for item in self.rlist:
            hist = sender.history(item, limit*10, 0)
            self.hlist.append(hist)

class donor_object(object):
    clist = []
    rlist = []
    hlist = []
    count = 1
    start = 0
    end   = count-1

    def __init__(self, l):
        self.clist = l
        self.count = len(l)
        self.end = self.count-1

    def get_arr(self):
        return self.rlist

    def check_offset(self, curr_pos):
        if curr_pos < self.end:
            curr_pos += 1
        else:
            curr_pos = 0
        return curr_pos

    def reveal_all(self, sender):
        found = False
        for item in self.clist:
            item = item.replace('@', '')
            item = item.replace(' ', '_')
            if not found:
                new_cont = sender.resolve_username(item)
                self.rlist.append(new_cont['id'])

def decode_to_utf8(item):
    return str(item).decode('utf-8')

def get_time_format():
    date_full = str(datetime.datetime.now())
    date_now = date_full.split(' ')[0]
    time_now = date_full.split(' ')[1]
    time_exp = time_now.split(':')
    return (int(time_exp[0])*60)+int(time_exp[1])

def get_item(arr, offset):
    if offset < arr.count:
        return arr.rlist[offset]

def get_news(hist, ctime):
    diff = []
    for item in hist[0]:
        diff.append(ctime - float(item["date"]))
    minimal = min(diff)
    i = 0
    for i in range(0,(len(diff))):
        if diff[i] == minimal:
            return i

def send(sender, donor, history=None, db_forwarded=None):
    ctime = time.time()
    num = get_news(history, ctime)
    text = history[0][num]
    if text not in db_forwarded:
        media = False
        if text.get('media',None):
            if text['media'].get('type',None) != 'webpage':
                try:
                    path  = sender.load_photo(text['id'])
                    media = True
                except:
                    return [False, False]
        if media:
            try:
                sender.send_photo(donor,path)
                print("photo sent")
            except:
                try:
                    sender.send_video(donor,path)
                    print("GIF sent")
                except:
                    return False
            print("deleting temporary files")
            os.system("rm -rf %s" % path)
        else:
            if(len(text['text']) > 1500):
                print("splitting the message")
                n = 1500
                texts = [text['text'][i:i+n] for i in range(0, len(text['text']), n)]
                for strt in range(1,len(texts)):
                    crtxt = texts[strt]
                    prevtxt = texts[strt-1]
                    if crtxt[0] != ' ':
                        dplet = crtxt.split(' ')
                        texts[strt-1] = u"%s%s" % (prevtxt, dplet[0])
                        dplet.pop(0)
                        texts[strt] = ' '.join(dplet)
                    elif crtxt[0] == ' ':
                        crtxt[0].replace(' ','')
                for tmp in texts:
                    sender.msg(donor, tmp)
                    print("text message's part sent")
            else:
                sender.msg(donor,text['text'])
        db_forwarded.append(text)
        return [True, True]
    return [False, True]

def form_acceptors(acc_tg, first=True):
    if acc_tg != '':
        print("Acceptors set")
        acceptor = acceptor_object(acc_tg)
        if first: acceptor.reveal_all(sender)
        acceptor_len = len(acc_tg)
    else:
        print("No telegram acceptors")
        acceptor = None
        acceptor_len = 0.5
    return [acceptor, acceptor_len]

def main(arguments, tg, receiver, sender):
    result = form_acceptors(arguments[1].split(','))
    acceptor = result[0]
    acceptor_len = result[1]
    donor = donor_object(arguments[2].split(','))
    if donor.clist[0] != '': donor.reveal_all(sender)
    total_len = int(math.floor(acceptor_len))
    changed = 1
    posts_made = 1
    posts_exp = int(int(arguments[3])*total_len)
    acceptor_offset = 0
    donor_offset = 0
    db_forwarded = []
    while posts_made <= posts_exp:
        sent = [False, True]
        if acceptor != None:
            if sent[1]:
                acceptor.drop_history()
                acceptor.get_histories(sender)
            history = acceptor.hlist
        else:
            history = []
        donor_cur = get_item(donor, donor_offset)
        sent = send(sender, donor_cur, history, db_forwarded)
        if sent[0] or sent[1]:
            if acceptor != None:
                acceptor.check_offset()
            if sent[0]:
                posts_made += 1
                delay = random.randint(2,4)
                time.sleep(delay)
            if not sent[0]:
                if changed == total_len:
                    changed = 1
                    delay   = random.randint(30,90)
                    time.sleep(delay)
                else:
                    changed += 1

if __name__ == '__main__':
    tg = Telegram(
        telegram = "tg/bin/telegram-cli",
        pubkey_file = "tg/tg-server.pub",
        port = 4652)
    receiver = tg.receiver
    sender   = tg.sender
    print("%s, %s, %s, %s" % (sys.argv[0],sys.argv[1],sys.argv[2],sys.argv[3]))
    main(sys.argv, tg, receiver, sender)  # executing main function

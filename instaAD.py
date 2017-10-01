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
import datetime
import time
import random
import re
import requests
import urllib
import json

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
        self.end   = self.count-1

    def get_arr(self):
        return self.rlist

    def check_offset(self, curr_pos):
        if curr_pos < self.end:
            return curr_pos+1
        else:
            return 0

    def reveal_all(self, sender):
        found = False
        for item in self.clist:
            item = item.replace('@', '')
            item = item.replace(' ', '_')
            if not found:
                new_cont = sender.resolve_username(item)
                self.rlist.append(new_cont['id'])

    def get_histories(self, limit, sender):
        for item in self.rlist:
            hist = sender.history(item, limit*100, 0)
            self.hlist.append(hist)

    def get_history(self, chid, history):
        res = 0
        for i in range(len(self.rlist)):
            if self.rlist[i] == chid:
                res = i
        return history[res]

class donor_object(object):
    clist = []
    rlist = []
    hlist = []
    count = 1
    start = 0
    end   = count - 1

    def __init__(self, l):
        self.clist = l
        self.count = len(l)
        self.end   = self.count-1

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

class insta_object(object):
    clist    = []
    db_ready = []
    end      = 0

    def __init__(self, l):
        self.clist = l
        if self.clist[0]!='':
            self.db_ready = self.get_photos_captions()
        else:
            self.db_ready = []
        self.end = len(self.db_ready)-1

    def get_db(self):
        return self.db_ready

    def check_offset(self, curr_pos):
        if curr_pos < self.end:
            curr_pos += 1
        else:
            curr_pos = 0
        return curr_pos

    def get_photos_captions(self, usernames=None):
        usernames = self.clist
        db_tmp = []
        maximum = 0
        for username in usernames:
            photos = []
            sturl = "https://www.instagram.com/%s/media" % username
            url = sturl
            data = {"items":[{"id":1}]}
            while(data["items"][-1].get("id",None) != None and maximum < 20):
                response = requests.get(url)
                data = response.json()
                for photo in data['items']:
                    try:
                        caption = photo["caption"]["text"]
                    except:
                        caption = ''
                    photos.append(
                        {
                            "caption" : caption,
                            "url" : photo["images"]["standard_resolution"]["url"]
                        }
                    )
                maximum += 20
                try:
                    url = "%s?max_id=%s" % (sturl, data["items"][-1].get("id",None))
                except:
                    break
            db_tmp.append({"usrname" : username, "photos" : photos})
        return db_tmp

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

def get_random_msg(history, already_sent, inst):
    if not inst:
        num = random.randint(0,len(history)-1)
        return history[num]
    else:
        rnd = 0
        num = 0
        return history[rnd]["photos"][num]["url"]

def preload_inst(needed):
    needed = needed.replace('/s640x640', '').split('?')[0]
    try:
    	imgname = needed.split('/')[-1].split('?')[0]
    	path = "{}{}".format(PATH_TO_DOWNLOADED, imgname)
    	urllib.urlretrieve(needed, path)
    	return path
    except:
        return False

def send(sender, donor, text, db_forwarded):
    if text not in db_forwarded and text != None:
        media = False
        if type(text) is unicode:
            print("loading instagram photos")
            path  = preload_inst(text)
            media = True
        elif text.get('media',None) != None:
            try:
                sender.load_photo(text['id'])
                media = True
            except:
                return False
        if media:
            try:
                sender.send_photo(donor,path)
                print("photo sent")
            except:
                try:
                    sender.send_video(donor,path)
                    print("GIF/Video/Audio sent")
                except:
                    return False
            print("deleting temporary files")
            os.system("rm -rf %s" % path)
            db_forwarded.append(text)
        else:
            sender.msg(donor,text['text'])
        return True
    else:
        return False

def main(arguments):
    age_max = 1
    acceptor = acceptor_object(arguments[1].split(','))
    if acceptor.clist[0]!='':
        print("Acceptors set")
        acceptor.reveal_all(sender)
        acceptor.get_histories(age_max, sender)
    else:
        print("No telegram acceptors")
        acceptor = None
    if arguments[2].split(',')[0] != '':
        print("Instagram acceptors set")
        acceptor_inst = insta_object(arguments[2].split(','))
    else:
        acceptor_inst = None
    print("Donors set")
    donor = donor_object(arguments[3].split(','))
    donor.reveal_all(sender)
    post_num = 0
    post_exp = int(arguments[4])*donor.count
    time_inf = get_time_format()
    time_need = time_inf
    acceptor_offset = 0
    acceptor_inst_offset = 0
    donor_offset = 0
    db_forwarded = []
    while post_num < post_exp:
        sent = False
        inst = False
        if True:
            if acceptor != None and acceptor_inst != None:
                chosen = random.randint(0,1)
            elif acceptor != None and acceptor_inst == None:
                chosen = 1
            elif acceptor == None and acceptor_inst != None:
                chosen = 0
            if chosen == 1 and acceptor != None:
                print("Telegram chosen")
                acceptor_cur = get_item(acceptor, acceptor_offset)
                history = acceptor.get_history(acceptor_cur, acceptor.hlist)
                inst = False
            elif chosen == 0 and acceptor_inst != None:
                print("Instagram chosen")
                acceptor_cur = acceptor_inst.get_db()
                history = acceptor_inst.get_db()
                inst = True
            print("Setting donor...")
            donor_cur = get_item(donor, donor_offset)
            print("Searching for random message")
            text = get_random_msg(history, db_forwarded, inst)
            print("Sending message...")
            sent = send(sender, donor_cur, text, db_forwarded)
            if sent:
                delay = random.randint(1,3)
                time.sleep(delay)
                post_num += 1
                if acceptor != None:
                    acceptor_offset = acceptor.check_offset(acceptor_offset)
                if acceptor_inst != None:
                    acceptor_inst_offset = acceptor_inst.check_offset(acceptor_inst_offset)
                donor_offset = donor.check_offset(donor_offset)
                if acceptor != None:
                    if acceptor_offset == 0:
                        rfirst = acceptor.rlist.pop(0)
                        acceptor.rlist.append(rfirst)
                        hfirst = acceptor.hlist.pop(0)
                        acceptor.hlist.append(hfirst)
        else:
            time_inf = get_time_format()

if __name__ == '__main__':
    tg = Telegram(
        telegram="tg/bin/telegram-cli",
        pubkey_file="tg/tg-server.pub",
        port=4550)
    receiver = tg.receiver
    sender   = tg.sender
    main(sys.argv)

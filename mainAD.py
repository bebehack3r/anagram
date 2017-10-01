#!/usr/bin/python
# -*- coding: utf-8 -*-

##################################################
##################################################
########## Created by Romanov Alexandr ###########
###### Current version: 0.2.7v (14.09.2017) ######
########## Contact me via tlgrm: @rmnff ##########
##################################################
##################################################

from __future__    import unicode_literals
from pytg          import Telegram
from pytg.receiver import Receiver
from pytg.sender   import Sender
from pytg.utils    import coroutine
import sys
import datetime
import random
import time

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

    def check_offset(self, curr_pos):
        return curr_pos+1 if curr_pos < self.end else 0

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
    end   = count-1

    def __init__(self, l):
        self.clist = l
        self.count = len(l)
        self.end = self.count-1

    def get_arr(self):
        return self.rlist

    def check_offset(self, curr_pos):
        curr_pos = curr_pos+1 if curr_pos < self.end else 0
        return curr_pos

    def reveal_all(self, sender):
        found = False
        for item in self.clist:
            original = item
            item = item.replace('@', '')
            item = item.replace(' ', '_')
            print original
            if not found:
                try:
                    new_cont = sender.resolve_username(item)
                    self.rlist.append(new_cont['id'])
                except:
                    self.clist.remove(original)
            time.sleep(1)

def decode_to_utf8(item):
    return str(item).decode('utf-8')

def get_time_format():
    date_full = str(datetime.datetime.now())
    date_now  = date_full.split(' ')[0]
    time_now  = date_full.split(' ')[1]
    time_exp  = time_now.split(':')
    return (int(time_exp[0])*60)+int(time_exp[1])

def get_item(arr, offset):
    if offset < arr.count:
        return arr.rlist[offset]

def get_real_item(arr, offset):
    if offset < arr.count:
        return arr.clist[offset]

def get_random_msg(arr):
    num = random.randint(0,len(arr)-1)
    return arr[num]

def send(sender, donor, text, db_forwarded):
    if db_forwarded != False:
        if text not in db_forwarded:
            db_forwarded.append(text)
            sender.fwd(donor, text)
            return True
    else:
        sender.msg(donor, text)
        return True
    return False

def main(arguments):
    age_max  = int(arguments[5])
    acceptor = acceptor_object(arguments[1].split(','))
    acceptor.reveal_all(sender)
    acceptor.get_histories(age_max, sender)
    donor = donor_object(arguments[2].split(','))
    donor.reveal_all(sender)
    post_num = 0
    post_exp = int(arguments[3])*donor.count
    time_inf = get_time_format()
    time_need = time_inf
    acceptor_offset = 0
    donor_offset = 0
    db_forwarded = []
    run_off = 1
    prevs = ["парень очень интересно пишет :)", "блин, не могу не поделиться с вами", "друзья, подписывайтесь, потому что паря точно шарит за крипту)", "наконец-то разобрался более-менее в том, как вообще это все работает", "если верить, то скоро будут новости про ICO и куда лучше инвестировать"]
    while post_num < post_exp:
        sent = False
        #if time_inf == time_need:
        try:
            acceptor_cur = get_item(acceptor, acceptor_offset)
            history = acceptor.get_history(acceptor_cur, acceptor.hlist)
            donor_real_cur = get_real_item(donor, donor_offset)
            donor_cur = get_item(donor, donor_offset)
            preview = get_random_msg(prevs)
            text = get_random_msg(history)
            sender.channel_join(donor_real_cur)
            print donor_real_cur
            send(sender, donor_cur, preview, False)
            time.sleep(1)
            sent = send(sender, donor_cur, text.id, db_forwarded)
            if sent:
                delay = random.randint(1,3)
                time.sleep(delay)
                post_num += 1
                acceptor_offset = acceptor.check_offset(acceptor_offset)
                donor_offset = donor.check_offset(donor_offset)
                if acceptor_offset == 0:
                    rfirst = acceptor.rlist.pop(0)
                    acceptor.rlist.append(rfirst)
                    hfirst = acceptor.hlist.pop(0)
                    acceptor.hlist.append(hfirst)
        except:
            pass
        #else:
        #    time_inf = get_time_format()
        if post_num / run_off == donor.count:
            run_off += 1
            time.sleep(arguments[4])


if __name__ == '__main__':
    tg = Telegram(
        telegram="tg/bin/telegram-cli",
        pubkey_file="tg/tg-server.pub",
        port=4558)
    receiver = tg.receiver
    sender   = tg.sender
    main(sys.argv)

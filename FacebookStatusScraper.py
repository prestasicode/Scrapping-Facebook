#!/usr/bin/env python
# encoding: utf-8

import csv
from datetime import datetime
from dateutil import tz
import json
import time
from termcolor import colored
import urllib2

def convert_to_local_time(date_str):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    return datetime.strptime(date_str[0:-5], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=from_zone).astimezone(to_zone).strftime('%Y-%m-%d %H:%M:%S')

def get_epoch_timestamp(date_str):
    return int(time.mktime(datetime.strptime(date_str, '%Y-%m-%d').timetuple()))

def request_until_succeed(url, max_tries=10, time_to_sleep=5):
    req = urllib2.Request(url)
    n_tries = 0
    success = False
    while success is False:
        n_tries += 1
        if n_tries > max_tries:
            break
        try: 
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print '\n[%s] %s' (datetime.now(), e)
            time.sleep(time_to_sleep*n_tries)
            print '[%s] Error for URL:\n\t%s\n' % (datetime.now(), url)
    # End of while loop.
    try:
        output = response.read()
    except:
        output = None
    # End of try/except statement.
    return output

#==============================#
# All about COMMENTS (replies) #
#==============================#
def get_replies_of_comment_id(comment_id, access_token):
    base = "https://graph.facebook.com/v2.6"
    node = "/" + comment_id + "/comments" 
    parameters = "/?access_token=%s" % (access_token)        
    url = base + node + parameters
    
    list_of_replies = list()
    has_next_page = True
    d = json.loads(request_until_succeed(url))
    
    while has_next_page:
        if d and 'data' in d and d['data']:
            for reply in d['data']:
                try:
                    reply_dict = {'reply_id'             : reply['id'],
                                  'reply_created_time'   : reply['created_time'],
                                  'reply_message'        : reply['message'],
                                  'reply_from_user_name' : reply['from']['name'],
                                  'reply_from_user_id'   : reply['from']['id']
                                 }
                    list_of_replies.append(reply_dict)
                except:
                    pass
                # End of try/except statement.
            # if there is no next page, we're done.
            if 'paging' in d and 'next' in d['paging']:
                d = json.loads(request_until_succeed(d['paging']['next']))
            else:
                has_next_page = False
            # End of if/else statement.
        else:
            has_next_page = False
        # End of if/else statement.
    # End of while loop.
    return list_of_replies

#============================#
# All about COMMENTS (likes) #
#============================#    
def get_likes_of_comment_id(comment_id, access_token):
    base = "https://graph.facebook.com/v2.6"
    node = "/" + comment_id + "/likes" 
    parameters = "/?access_token=%s" % (access_token)
    url = base + node + parameters
    
    list_of_likes = list()
    has_next_page = True
    d = json.loads(request_until_succeed(url))
    
    while has_next_page:
        if d and 'data' in d and d['data']:
            for like in d['data']:
                try:
                    like_dict = {'like_from_user_name' : like['name'],
                                 'like_from_user_id'   : like['id']
                                }
                    list_of_likes.append(like_dict)
                except:
                    pass
                # try/except statement.
            # if there is no next page, we're done.
            if 'paging' in d and 'next' in d['paging']:
                d = json.loads(request_until_succeed(d['paging']['next']))
            else:
                has_next_page = False
            # End of if/else statement.
        else:
            has_next_page = False
        # End of if/else statement.
    # End of while loop.
    return list_of_likes

#===============================================================#
# All about the JSON/DICTIONARY output (FB Page ID's FEED Data) #
#===============================================================#
def get_fb_page_feed_data(page_id, access_token, no_of_status_posts, likes_limit=1, comments_limit=100, start_ts=None, end_ts=None):
    base = "https://graph.facebook.com/v2.6"
    #node = "/" + page_id + "/feed" 
    node = "/" + page_id + "/posts" 
    #parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(%s).summary(true),comments.limit(%s).summary(true),shares&limit=%s&access_token=%s" % (likes_limit, comments_limit, no_of_status_posts, access_token)
    parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(%s).summary(true),comments.limit(%s).summary(true),reactions.limit(0).summary(true),shares&limit=%s&access_token=%s" % (likes_limit, comments_limit, no_of_status_posts, access_token)
    if start_ts is not None:
        parameters += '&since=%d' % start_ts
    if end_ts is not None:
        parameters += '&until=%d' % end_ts
    url = base + node + parameters
    return json.loads(request_until_succeed(url)) # Returns a Dict object

#====================================================#
# All about the JSON/DICTIONARY output (Status Data) #
#====================================================#
def get_status_data(status_id, access_token, likes_limit=1, comments_limit=100):
    base = "https://graph.facebook.com/v2.6"
    node = "/" + status_id + "/" 
    #parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(%s).summary(true),comments.limit(%s).summary(true),shares&limit=1&access_token=%s" % (likes_limit, comments_limit, access_token)
    parameters = "/?fields=message,link,created_time,type,name,id,likes.limit(%s).summary(true),comments.limit(%s).summary(true),reactions.type(LIKE).limit(0).summary(true).as(reactions_like),reactions.type(LOVE).limit(0).summary(true).as(reactions_love),reactions.type(WOW).limit(0).summary(true).as(reactions_wow),reactions.type(HAHA).limit(0).summary(true).as(reactions_haha),reactions.type(SAD).limit(0).summary(true).as(reactions_sad),reactions.type(ANGRY).limit(0).summary(true).as(reactions_angry),shares&limit=1&access_token=%s" % (likes_limit, comments_limit, access_token)
    url = base + node + parameters
    # return json.loads(request_until_succeed(url))
    output_dict = json.loads(request_until_succeed(url))
    print colored(json.dumps(output_dict), 'yellow')
    return output_dict

###########################################
#                                         #
# Scrape Page ID (this is the MAIN shit!) #
#                                         #
###########################################
def scrape_fb_page_feed_status(page_id, access_token, likes_limit=1, comments_limit=50, list_of_status_ids=None, start_ts=None, end_ts=None, is_simple_mode=False):
    
    ########################################################
    # Check if "is_simple_mode" to determine the file_name #
    ########################################################
    if is_simple_mode:
        file_name = 'output/%s_%s_fb_page_feed_SIMPLE_MODE.csv' % (page_id, datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    else:
        file_name = 'output/%s_%s_fb_page_feed.csv' % (page_id, datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    # End of if/else statement.
    
    ####################
    # Open the file... #
    ####################
    with open(file_name, 'wb') as f:

        csv_f = csv.writer(f)
        if is_simple_mode:
            header = ['Status ID', 'Status Type', 'Status Link', 'Status Name', 'Status Created Time', 'Status Message', 'Status Shares Count', 'Status Likes Count', 'Status Comments Count']
        else:
            header = ['Status ID', 'Status Type', 'Status Link', 'Status Name', 'Status Created Time', 'Status Message', 'Status Shares Count', 'Status Likes Count', 'Status Comments Count', 'Comment ID', 'Comment Created Time', 'Comment Message', 'Comment From', 'Comment Likes Count', 'Reply ID', 'Reply Created Time', 'Reply Message', 'Reply From', 'Reply Likes Count']
        # End of if/else statement.
        csv_f.writerow(header)

        has_next_page = True
        num_processed = 0 # Keep a count on how many we've processed.
        scrape_starttime = datetime.now()

        ##########################################################
        # Check if "is_simple_mode" (for printing purposes only) #
        ##########################################################
        if is_simple_mode:
            print "Scraping \"%s\" Facebook Page (simple mode): %s\n" % (page_id, scrape_starttime)
        else:
            print "Scraping \"%s\" Facebook Page (normal mode): %s\n" % (page_id, scrape_starttime)
        # End of if/else statement.

        ############################################################################
        # If "list_of_status_ids" contains a list, read the statuses from the list #
        ############################################################################
        if list_of_status_ids is not None and isinstance(list_of_status_ids, list):
            statuses = dict()
            statuses['data'] = list_of_status_ids
        else:
            if is_simple_mode:
                no_of_status_posts = 20
                statuses = get_fb_page_feed_data(page_id, access_token, no_of_status_posts, likes_limit=1, comments_limit=1, start_ts=start_ts, end_ts=end_ts)
            else:
                no_of_status_posts = 5
                statuses = get_fb_page_feed_data(page_id, access_token, no_of_status_posts, likes_limit=likes_limit, comments_limit=comments_limit, start_ts=start_ts, end_ts=end_ts)
            # End of if/else statement.
        # End of if/else statement.

        #######################################################################
        # Continue looping this while loop until there's no more "next pages" #
        #######################################################################
        while has_next_page:
            for status in statuses['data']:

                ##########################################################################################################
                # If "list_of_status_ids" contains a list (or is not None), the "status" is actually the "status_id".    #
                # To get the real status Dict object, we call the function "get_status_data" with the "status/status_id" #
                # in its parameters.                                                                                     #
                ##########################################################################################################
                if list_of_status_ids is not None and isinstance(list_of_status_ids, list):
                    status = get_status_data(status, access_token, likes_limit=likes_limit, comments_limit=comments_limit)
                # End of if statement.

                try:
                    status_id             = status['id']
                    status_type           = status['type']
                    status_link           = status['link'] if 'link' in status else '<no link>'
                    status_name           = status['name'] if 'name' in status else '<no name>'
                    status_created_time   = convert_to_local_time(status['created_time'])
                    status_message        = status['message'] if 'message' in status else '<no message>'
                    status_shares_count   = unicode(status['shares']['count']) if ('shares' in status and 'count' in status['shares']) else u'0'
                    status_likes_count    = unicode(status['likes']['summary']['total_count']) if ('likes' in status and 'summary' in status['likes']) else u'0'
                    status_comments_count = unicode(status['comments']['summary']['total_count']) if ('comments' in status and 'summary' in status['likes']) else u'0'

                    temp_list_status = [status_id,status_type,status_link,status_name,status_created_time,status_message,status_shares_count,status_likes_count,status_comments_count]
                    temp_list_status = [x.encode('utf-8') for x in temp_list_status]

                    ########################################################
                    # If "is_simple_mode", write the data to the CSV file. #
                    ########################################################
                    if is_simple_mode:
                        csv_f.writerow(temp_list_status)
                    ###########
                    # Else... #
                    ###########
                    else:
                        ############################
                        # If there are comments... #
                        ############################
                        if 'comments' in status and 'data' in status['comments'] and status['comments']['data']:

                            comments = status['comments']
                            has_more_comments = True
                            while has_more_comments:

                                for comment in comments['data']:
                                    comment_id           = comment['id']
                                    comment_created_time = convert_to_local_time(comment['created_time'])
                                    comment_message      = comment['message']
                                    comment_from         = '%s (%s)' % (comment['from']['name'], comment['from']['id'])
                                    try:
                                        comment_likes_count = unicode(len(get_likes_of_comment_id(comment_id, access_token)))
                                    except:
                                        comment_likes_count = u'0'
                                    
                                    temp_list_comment = [comment_id,comment_created_time,comment_message,comment_from,comment_likes_count]
                                    temp_list_comment = [x.encode('utf-8') for x in temp_list_comment]
                                    temp_list_comment = temp_list_status + temp_list_comment

                                    ########################
                                    #                      #
                                    # Second level replies #
                                    #                      #
                                    ########################
                                    replies = get_replies_of_comment_id(comment_id, access_token)

                                    #######################################################################
                                    # If there are replies...                                             #
                                    # Extract all the replies, and for each reply, write to the CSV file. #
                                    #######################################################################
                                    if replies:
                                        for r in replies:
                                            reply_id           = r['reply_id']
                                            reply_created_time = convert_to_local_time(r['reply_created_time'])
                                            reply_message      = r['reply_message']
                                            reply_from         = '%s (%s)' % (r['reply_from_user_name'], r['reply_from_user_id'])
                                            try:
                                                reply_likes_count = unicode(len(get_likes_of_comment_id(reply_id, access_token)))
                                            except:
                                                reply_likes_count = u'0'
                                            
                                            temp_list_reply = [x.encode('utf-8') for x in [reply_id, reply_created_time, reply_message, reply_from, reply_likes_count]]
                                            temp_list_reply = temp_list_comment + temp_list_reply
                                            
                                            csv_f.writerow(temp_list_reply)
                                        # End of for loop (for replies).
                                    #############################################################
                                    # Else, if there aren't any replies, write to the CSV file. #
                                    #############################################################
                                    else:
                                        csv_f.writerow( temp_list_comment )
                                    # End of if/else statement.
                                # End of for loop (for comments).

                                if 'paging' in comments and 'next' in comments['paging']:
                                    comments = json.loads(request_until_succeed( comments['paging']['next'] ))
                                    if comments and 'data' in comments and comments['data']:
                                        pass 
                                    else:
                                        has_more_comments = False
                                    # End of if/else statement.
                                else:
                                    has_more_comments = False
                                # End of if/else statement.
                            # End of while loop.
                        ##################################################################
                        # Else if there aren't any comments, just write to the CSV file. #
                        ##################################################################
                        else:
                            csv_f.writerow( temp_list_status )
                        # End of if/else statement.
                    # End of if/else statement (on whether it's "simple mode" or not)
                except:
                    pass
                # End of try/except statement.

                ###################################################################
                # Output progress occasionally to make sure code is not stalling. #
                ###################################################################
                num_processed += 1
                if num_processed % 100 == 0:
                    if is_simple_mode:
                        print "%s Statuses Processed (by simple mode): %s" % (num_processed, datetime.now())
                    else:
                        print "%s Statuses Processed (by normal mode): %s" % (num_processed, datetime.now())
                # End of if statement.
            # End of for loop (for status).
            
            # if there is no next page, we're done.
            if 'paging' in statuses.keys() and 'next' in statuses['paging']:
                statuses = json.loads(request_until_succeed(statuses['paging']['next']))
                if statuses and 'data' in statuses and statuses['data']:
                    pass
                else:
                    has_next_page = False
                # End of if/else statement.
            else:
                has_next_page = False
            # End of if/else statement.
        # End of while loop.  
        print "\nDone!\n%s Statuses Processed in %s" % (num_processed, datetime.now() - scrape_starttime)
    # End of with open.

#===============#
# Program usage #
#===============#
def usage(program_name):
    print 'Usage: %s [-p|--page-id FBpageID] [-a|--app-id FBappID] [-t|--app-secret FBappsecret] [-s, --start-date yyyy-mm-dd] [-e, --end-date yyyy-mm-dd] [-S|--simple] [-h|--help]' % program_name
    opts = [('-p, --page-id','The Facebook handle that you\'d like to scrape.'),
            ('-a, --app-id','The Facebook app id used to scrape'),
            ('-t, --app-secret','The Facebook app secret (token) used to scrape'),
            ('-s, --start-date','The start date, scrape posts from 00:00:00 of this date onward (local time). Date format: yyyy-mm-dd'),
            ('-e, --end-date','The end date, scrape posts up to 23:59:59 of this date (local time). Date format: yyyy-mm-dd'),
            ('-S, --simple','Use SIMPLE mode if this flag is on, otherwise use NORMAL mode.'),
            ('-h, --help','Print this usage help')]
    for o, m in opts:
        print '\t%s: %s' % (o,m)

#======#
# Main #
#======#
if __name__ == "__main__":
    import sys, getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:a:t:s:e:Sh", ["page-id=", "app-id=", "app-secret=", "start-date", "end-date", "simple","help"])
    except getopt.GetoptError as err:
        print str(err)
        usage(sys.argv[0])
        sys.exit(2)

    print_help = False
    app_id     = '631289457043115' #'814941615282783'
    app_secret = 'c7da9b49e15fa5e8848d1f933823056c' # '6c27c730fae4caf43e126a003939d8b4'
    page_id    = 'sohruiyong' # 'leehsienloong' # 125845680811480'
    simple     = False
    start_ts   = None
    end_ts     = None

    for o, a in opts:
        if o in ("-p","--page-id"):
            page_id = a
        elif o in ("-a", "--app-id"):
            app_id = a
        elif o in ("-t", "--app-secret"):
            app_secret = a
        elif o in ("-s","--start-date"):
            start_date = a
            try:
                start_ts = get_epoch_timestamp(start_date)
            except ValueError:
                assert False, "Invalid start date"
        elif o in ("-e","--end-date"):
            end_date = a
            try:
                end_ts = get_epoch_timestamp(end_date) + 24 * 3600 - 1
            except ValueError:
                assert False, "Invalid end date"
        elif o in ("-h", "--help"):
            print_help = True
        elif o in ("-S", "--simple"):
            simple = True
        else:
            assert False, "unhandled option"

    if print_help:
        usage(sys.argv[0])
        sys.exit(0)

    access_token = app_id + '|' + app_secret
    print '\naccess_token: %s' % access_token
    print 'page_id: %s\n' % page_id
    scrape_fb_page_feed_status(page_id, access_token, start_ts=start_ts, end_ts=end_ts, is_simple_mode=simple)
# End of main
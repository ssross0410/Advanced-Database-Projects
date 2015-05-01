import urllib, urllib2, json
import sys
import re
import collections
from threading import *
from socket import *
import string

# define global variable
api_key = 'AIzaSyDRXrrGJAJDCZr0i3xak_y0oMsOztLmqL4'

# 6 high level types above
#TODO did not find TV actor example
Type = {
    '/people/person/place_of_birth'             : {'type' : 'Person','entry' : 'Place of birth'},
    '/people/person/date_of_birth'              : {'type' : 'Person','entry' : 'Birthday'},
    '/people/person/sibling_s'      : {'type' : 'Person', 'entry' : 'Siblings',},
    '/people/person/spouse_s'       : {'type' : 'Person', 'entry' : 'Spouses'},
    '/people/deceased_person/cause_of_death': {'type' : 'Person', 'entry' : 'Death'},
    '/people/deceased_person/date_of_death' : {'type' : 'Person', 'entry' : 'Death'},
    '/people/deceased_person/place_of_death': {'type' : 'Person', 'entry' : 'Death'},

    '/book/author/works_written'        : {'type' : 'Author', 'entry' : 'Books'},
    '/book/book_subject/works'      : {'type' : 'Author', 'entry' : 'Books about'},
    '/influence/influence_node/influenced'  : {'type' : 'Author', 'entry' : 'Influenced'},
    '/influence/influence_node/influenced_by': {'type' : 'Author', 'entry' : 'Influenced By'},

    
    '/film/actor/film'              : {'type' : 'Actor', 'entry':'Films'},
    '/tv/tv_actor'              : {'type': 'Actor', 'entry':'tv_actor'},

    '/organization/organization_founder/organizations_founded'  : {'type':'BusinessPerson', 'entry' : 'Founded'},
    '/business/board_member/leader_of'              : {'type':'BusinessPerson', 'entry' : 'Leadership'},
    '/business/board_member/organization_board_memberships'     : {'type':'BusinessPerson', 'entry': 'Board Member'},

    '/sports/sports_league/teams'           : {'type':'League', 'entry':'Teams'},
    '/organization/organization/slogan'     : {'type':'League', 'entry':'Slogan'},
    '/sports/sports_league/championship'        : {'type':'League', 'entry':'Championship'},
    '/sports/sports_league/sport'           : {'type':'League', 'entry':'Sport'},
    '/common/topic/official_website'        : {'type':'League', 'entry':'OfficialWebsite'},

    '/sports/sports_team/arena_stadium'         : {'type':'SportsTeam', 'entry':'Arena'},
    '/sports/sports_team/championships'         : {'type':'SportsTeam', 'entry':'Championships'},
    '/sports/sports_team/coaches'               : {'type':'SportsTeam', 'entry':'Coaches'},
    '/sports/sports_team/founded'               : {'type':'SportsTeam', 'entry':'Founded'},
    '/sports/sports_team/league'                : {'type':'SportsTeam', 'entry':'Leagues'},
    '/sports/sports_team/location'              : {'type':'SportsTeam', 'entry':'Location'},
    '/sports/sports_team/roster'                : {'type':'SportsTeam', 'entry':'PlayersRoaster'},
    '/sports/sports_team/sport'             : {'type':'SportsTeam', 'entry':'Sport'},

    '/common/topic/description'     : {'type' : 'General', 'entry' : 'Descriptions'}
}
TypefindList = {
    'Person'        : [ '/people/person/place_of_birth',    '/people/person/date_of_birth',         '/people/person/sibling_s',
                    '/people/person/spouse_s',      '/people/deceased_person/date_of_death',    '/people/deceased_person/place_of_death',           '/people/deceased_person/cause_of_death'    
                    ],
    'Author'        : [ '/book/author/works_written',       '/book/book_subject/works',             '/influence/influence_node/influenced',
                    '/influence/influence_node/influenced_by'],
    'Actor'         : [ '/film/actor/film'],
    'BusinessPerson'    : [ '/organization/organization_founder/organizations_founded', '/business/board_member/leader_of', '/business/board_member/organization_board_memberships' ],
    
    'League'        : [ '/sports/sports_league/teams', '/organization/organization/slogan', '/sports/sports_league/championship',
                    '/sports/sports_league/sport', '/common/topic/official_website'],
    'SportsTeam'        : [ '/sports/sports_team/arena_stadium', "/sports/sports_team/championships", '/sports/sports_team/coaches',
                    '/sports/sports_team/founded',  '/sports/sports_team/league', '/sports/sports_team/location',
                    '/sports/sports_team/roster', '/sports/sports_team/sport'],
    'Descriptions'      : [ '/common/topic/description']
}
    
Compound = {
    '/film/actor/film'              :   [   '/film/performance/character'   , 
                                    '/film/performance/film'    ],

    '/people/person/sibling_s'          :   [   '/people/sibling_relationship/sibling'  ],

    '/people/person/spouse_s'           :   [   '/people/marriage/spouse'   ,
                                    '/people/marriage/from'     ,
                                    '/people/marriage/to'       ],

    '/business/board_member/leader_of'      :   [   '/organization/leadership/organization' ,
                                    '/organization/leadership/role'     , 
                                    '/organization/leadership/title'    ,
                                    '/organization/leadership/from'     , 
                                    '/organization/leadership/to'       ],

    '/business/board_member/organization_board_memberships'     :   [   '/organization/organization_board_membership/organization'  , 
                                            '/organization/organization_board_membership/role'      , 
                                            '/organization/organization_board_membership/title'     , 
                                            '/organization/organization_board_membership/from'      ,
                                            '/organization/organization_board_membership/to'        ],

    '/sports/sports_league/teams'       :   [   '/sports/sports_league_participation/team'  ],
    '/sports/sports_team/coaches'       :   [   '/sports/sports_team_coach_tenure/coach'    ,
                                '/sports/sports_team_coach_tenure/position' ,
                                '/sports/sports_team_coach_tenure/from'     ,
                                '/sports/sports_team_coach_tenure/to'       ],

    '/sports/sports_team/league'        :   [   '/sports/sports_league_participation/league'    ],

    '/sports/sports_team/roster'        :   [   '/sports/sports_team_roster/player' ,
                                '/sports/sports_team_roster/position'   ,
                                '/sports/sports_team_roster/number' ,
                                '/sports/sports_team_roster/from'   ,
                                '/sports/sports_team_roster/to'     ]
    
}
# global query
Query = ""
# print parameter
printPara = {
    'Hline' : 95
}
# for the entity name
Name = ""
# for the entity type
entityType = {
    'Author' : False,
    'Actor'  : False,
    'BusinessPerson' : False,
    'League'    : False,
    'SportsTeam'    :False,
    'Person'    :False
}

# extracted information that needs to be printed
InfoBox = {
    'Person' : {},
    'Author' : {},
    'Actor'  : {},
    'BusinessPerson'  : {},
    'League'    : {},
    'SportsTeam'    : {},
    'Descriptions'  : {}
}

# print variable
Hspace = "         "
Vspace = "        "
Hline = "--------------------------------------------------------------------------------------------------"
EntrySpace = "                "
ValueSpace = "                                                                                 "

service_url = 'https://www.googleapis.com/freebase/v1/search'
interest_url = 'https://www.googleapis.com/freebase/v1/topic'

# check if the result is able to be created into box
Isfinish = False

DataParams = {
        'query': "",
        'key': api_key
}
TopicParams = {
       # 'filter': 'suggest',
        'key': api_key
}
urlData = service_url + '?' 
urlTopic = interest_url
target = {
    'name': "",
    'mid' : ""
}

# the main function
def main():
    global api_key
    api_key = sys.argv[2]
    if len(sys.argv) == 7:
        option = sys.argv[3]            # single query or a batch of queries
        query = sys.argv[4]             # the actual query
        queryType = sys.argv[6]         # infobox or question
        if option == '-q':
            if queryType == 'question':
                answer(api_key, query)
            elif queryType == 'infobox':
                infobox(query)
            else:
                error()
        elif option == '-f':
            queryFile = open(query, "r")
            # read the file line by line
            for line in queryFile:
                if queryType == 'question':
                    print "Question: " + line
                    answer(api_key, line)
                elif queryType == 'infobox':
                    print "Infobox of: " + line
                    infobox(line)
                else:
                    error()
        else:
            error()
    else:
        error()


def reset():
    global Name
    global entityType
    global InfoBox
    global Isfinish
    global target
    global DataParams
    global urlData
    global urlTopic
    
    Name = ""
    entityType = {
        'Author' : False,
        'Actor'  : False,
        'BusinessPerson' : False,
        'League'    : False,
        'SportsTeam'    :False,
        'Person'    :False
    }
    InfoBox = {
        'Person' : {},
        'Author' : {},
        'Actor'  : {},
        'BusinessPerson'  : {},
        'League'    : {},
        'SportsTeam'    : {},
        'Descriptions'  : {}
    }
    Isfinish = False
    target = {
        'name': "",
        'mid' : ""
    }
    DataParams = {
            'query': "",
            'key': api_key
    }
    urlData = service_url + '?'
    urlTopic = interest_url
def infobox(query):
    reset()
    getInput(query)
    getData()

###########################################################
def createInfobox(response):
    global Name
    global Query
    counter = 0
    while Isfinish == False and counter < len(response['result']):
        if counter != 0 and counter%5 == 0:
            print str(counter) + ' Search API result entries were considered. None of them of a supported type.'
        target["name"] = response['result'][counter]['name']
        target["mid"] = response['result'][counter]['mid']
        Name = target["name"].encode("utf-8")
        Name = checkPrint(Name)
        # TODO receive properties of interest from Freebase Topic API
        getInterest()   
        counter += 1
    #print counter
    #print len(response['result'])
    if counter >= len(response['result']) and Isfinish == False:
        print "No related information about query [" + Query + "] was found!"
########################## ###################################
def getInput(query):
    global DataParams
    global urlData
    global Query

    # #TODO hard coding for now
    # query = Query
    #print "this is query", query
    #print "this is key", DataParams['key']
    DataParams['query'] = query
    Query = query
    urlData += urllib.urlencode(DataParams)
    #print "this urlData", urlData
    
############################################################
def getData():
    global urlData
    #print "####################################################"
    response = json.loads(urllib.urlopen(urlData).read())
    #print response
    createInfobox(response)
#   print target['name']
#   print target['mid']
############################################################
def getInterest():
    global target
    global TopicParams
    global urlTopic

    url = urlTopic + target['mid'] + '?' + urllib.urlencode(TopicParams)    
    response = json.loads(urllib.urlopen(url).read())
    #TODO extract information
    extractInfo(response)
###########################################################
def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]
def Print():
    global Hspace
    global Vspace
    global EntrySpace
    global Hline
    global InfoBox
    global printPara
    global entityType
    global Name
    global ValueSpace

    # for the title 
    leftspace = ""
    titleName = Name
    titletype = "("
    for i in entityType:
        if entityType[i] == True and i != 'Person':
            titletype += i + " "
    titletype += ")"
    if len(titletype) > 2:
        titleName += titletype
    numSpace = (len(Hline)-len(titleName))/2
    leftspace = leftspace.ljust(numSpace)
    rightspace = ""
    if 2*len(leftspace) + len(titleName) < len(Hline):
        rightspace = leftspace + " "
    else:
        rightspace = leftspace
    print Hspace, Hline
    counter = 0
    print Vspace, "|" + leftspace + titleName + rightspace + "|"
    print Hspace, Hline
    ######################################################
    # first entry should be the name
    rightspace = ""
    rightspace = rightspace.ljust(len(ValueSpace) - len(Name))
    subentrySpace = ""
    subentrySpace = subentrySpace.ljust(len(EntrySpace) - len("Name"))
    print Vspace, "| Name" + subentrySpace + Name + rightspace + "|"
    #####################################################
    

    if (entityType["Person"] == True):
        helpPrint("Person")
        
    if (entityType["Author"] == True):
        helpPrint("Author")
        
    if (entityType["Actor"] == True):
        helpPrint("Actor")
        
    if (entityType["BusinessPerson"] == True):
        helpPrint("BusinessPerson")
        
    if (entityType["League"] == True):
        helpPrint("League")
        
    if (entityType["SportsTeam"] == True):
        helpPrint("SportsTeam")
        
    helpPrint("Descriptions")
    print Hspace, Hline

def checkPrint(info):
    p = ''
    for i in info:
        if i in string.printable:
            p = p + i
        else:
            p = p + '?' 
    return p
def helpPrint(curType):
    global EntrySpace
    global ValueSpace
    for key in InfoBox[curType].keys():
        if key == 'name':
            continue
        
        print Hspace, Hline
        # fid = open("check", 'w')

        if key == "Descriptions":
            subentrySpace = ""
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            res = split_len(InfoBox[curType]['Descriptions'], len(ValueSpace))
            rightspace = ""
            rightspace = rightspace.ljust(len(ValueSpace) - len(res[0]))
            p = checkPrint(res[0])
            print Vspace, "| " + key + subentrySpace + p + rightspace + "|"
            # fid.write(res[0] + "\n")
            for r in range(1,len(res)):
                rightspace = ""
                rightspace = rightspace.ljust(len(ValueSpace) - len(res[r]))
                p = checkPrint(res[r])
                print Vspace, "| " + EntrySpace + p + rightspace + "|"
                # fid.write(res[r] + "\n")
        elif key == "Films":
            character = "Character                              "
            film = " Film Name                               "
            subentrySpace = ""
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            print Vspace,   "| " + key + subentrySpace[1:len(subentrySpace)] + \
                    "|" + character + \
                    "|" + film + "|"
            print Vspace, "| " + EntrySpace + "----------------------------------------------------------------------------------"
            res = InfoBox[curType][key].split('\n')
            for i in range(0, len(res) - 1, 2):
                cspace = ""
                fspace = ""
                if res[i] == "null":
                    p = ""
                    res[i] = p.ljust(len(character))
                else:
                    if len(res[i]) > len(character):
                        res[i] = checkPrint(res[i])
                        res[i] = res[i][0:len(character)-4]
                        res[i] = res[i] + ' ...'
                cspace = cspace.ljust(len(character) - len(res[i]))
                        

                if res[i + 1] == "null":
                    p = ""
                    res[i + 1] = p.ljust(len(film))
                else:
                    if len(res[i + 1]) > len(film):
                        res[i + 1] = checkPrint(res[i + 1])
                        res[i + 1] = res[i + 1][0:len(film)-4]
                        res[i + 1] = res[i + 1] + ' ...'
                fspace = fspace.ljust(len(film) - len(res[i + 1]))
                print   Vspace, "| " + EntrySpace[1:len(EntrySpace)] + "|" + res[i] + cspace + "|" + res[i + 1] +  fspace + "|" 
        elif key == 'PlayersRoaster':
            name = "Name             "
            position = " Position             "
            number = " Number             "
            FROM = " From/To           "
            subentrySpace = ""
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            print Vspace,   "| " + key + subentrySpace[1:len(subentrySpace)] + \
                    "|" + name + \
                    "|" + position + \
                    "|" + number + \
                    "|" + FROM + "|"    
            print Vspace, "| " + EntrySpace + "----------------------------------------------------------------------------------"  
            #print InfoBox[curType][key]
            res = InfoBox[curType][key].split('\n')
            for i in range(0, len(res) - 4, 5):
                naspace = ""
                pspace = ""
                nuspace = ""
                fspace = ""
                if res[i] == "null":
                    p = ""
                    res[i] = p.ljust(len(name))
                else:
                    if len(res[i]) > len(name):
                        res[i] = checkPrint(res[i])
                        res[i] = res[i][0:len(name)-4]
                        res[i] = res[i] + ' ...'
                naspace = naspace.ljust(len(name) - len(res[i]))
                        

                if res[i + 1] == "null":
                    p = ""
                    res[i + 1] = p.ljust(len(position))
                else:
                    if len(res[i + 1]) > len(position):
                        res[i + 1] = checkPrint(res[i + 1])
                        res[i + 1] = res[i + 1][0:len(position)-4]
                        res[i + 1] = res[i + 1] + ' ...'
                pspace = pspace.ljust(len(position) - len(res[i + 1]))
                
                if res[i + 2] == "null":
                    p = ""
                    res[i + 2] = p.ljust(len(nuspace))
                else:
                    if len(res[i + 2]) > len(number):
                        res[i + 2] = checkPrint(res[i + 2])
                        res[i + 2] = res[i + 2][0:len(number)-4]
                        res[i + 2] = res[i + 2] + ' ...'
                nuspace = nuspace.ljust(len(number) - len(res[i + 2]))
                
                # from and to all null
                
                if res[i + 3] == 'null' and res[i + 4] == "null":
                    p = ""
                    From_To = p.ljust(len(FROM))
                elif res[i + 4] == "null":
                    From_To = res[i + 3] + ' / now'
                    if len(From_To) > len(FROM):
                        From_To = checkPrint(From_To)
                        From_To = From_To[0:len(FROM)-4]
                        From_To = From_To + ' ...'                      
                    fspace = fspace.ljust(len(FROM) - len(From_To))
                elif res[i + 4] != "null" and res[i + 3] != "null":
                    From_To = res[i + 3]+' / '+res[i + 4]
                    if len(From_To) > len(FROM):
                        From_To = checkPrint(From_To)
                        From_To = From_To[0:len(FROM)-4]
                        From_To = From_To + ' ...'                      
                    fspace = fspace.ljust(len(FROM) - len(From_To))                     

                print   Vspace, "| " + EntrySpace[1:len(EntrySpace)] + "|" + res[i] + naspace + "|" + res[i + 1] +  pspace + "|" + res[i + 2] + nuspace + "|" + From_To + fspace + "|"      
        elif key == 'Coaches':
            name = "Name                    "
            position = " Position                    "
            FROM = " From/To                  "
            subentrySpace = ""
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            print Vspace,   "| " + key + subentrySpace[1:len(subentrySpace)] + \
                    "|" + name + \
                    "|" + position + \
                    "|" + FROM + "|"    
            print Vspace, "| " + EntrySpace + "----------------------------------------------------------------------------------"  
            #print InfoBox[curType][key]
            res = InfoBox[curType][key].split('\n')
            for i in range(0, len(res) - 3, 4):
                naspace = ""
                pspace = ""
                nuspace = ""
                fspace = ""
                if res[i] == "null":
                    p = ""
                    res[i] = p.ljust(len(name))
                else:
                    if len(res[i]) > len(name):
                        res[i] = checkPrint(res[i])
                        res[i] = res[i][0:len(name)-4]
                        res[i] = res[i] + ' ...'
                naspace = naspace.ljust(len(name) - len(res[i]))
                        

                if res[i + 1] == "null":
                    p = ""
                    res[i + 1] = p.ljust(len(position))
                else:
                    if len(res[i + 1]) > len(position):
                        res[i + 1] = checkPrint(res[i + 1])
                        res[i + 1] = res[i + 1][0:len(position)-4]
                        res[i + 1] = res[i + 1] + ' ...'
                pspace = pspace.ljust(len(position) - len(res[i + 1]))
                
                # from and to all null
                
                if res[i + 2] == 'null' and res[i + 3] == "null":
                    p = ""
                    From_To = p.ljust(len(FROM))
                elif res[i + 3] == "null":
                    From_To = res[i + 2] + ' / now'
                    if len(From_To) > len(FROM):
                        From_To = checkPrint(From_To)
                        From_To = From_To[0:len(FROM)-4]
                        From_To = From_To + ' ...'                      
                    fspace = fspace.ljust(len(FROM) - len(From_To))
                elif res[i + 3] != "null" and res[i + 2] != "null":
                    From_To = res[i + 2]+' / '+res[i + 3]
                    if len(From_To) > len(FROM):
                        From_To = checkPrint(From_To)
                        From_To = From_To[0:len(FROM)-4]
                        From_To = From_To + ' ...'                      
                    fspace = fspace.ljust(len(FROM) - len(From_To))                     

                print   Vspace, "| " + EntrySpace[1:len(EntrySpace)] + "|" + res[i] + naspace + "|" + res[i + 1] +  pspace + "|" + From_To + fspace + "|"           
        elif key == 'Board Member' or key == 'Leadership':
            organization = "Organization            "
            role = " Role            "
            title = " Title            "
            FROM = " From-To           "
            subentrySpace = ""
            # the "|" should included in the subentrySpace
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            print Vspace, "| " + key + subentrySpace[1:len(subentrySpace)] + "|" + organization +"|" + role + "|" + title + "|" + FROM + "|"
            print Vspace, "| " + EntrySpace + "----------------------------------------------------------------------------------"
            #print InfoBox[curType][key]
            res = InfoBox[curType][key].split('\n')
            for i in range(0, len(res) - 4, 5):
                ospace = ""
                rspace = ""
                tspace = ""
                fspace = ""
                if res[i] == "null":
                    p = ""
                    res[i] = p.ljust(len(organization))
                else:
                    if len(res[i]) > len(organization):
                        res[i] = checkPrint(res[i])
                        res[i] = res[i][0:len(organization)-4]
                        res[i] = res[i] + ' ...'
                ospace = ospace.ljust(len(organization) - len(res[i]))
                        

                if res[i + 1] == "null":
                    p = ""
                    res[i + 1] = p.ljust(len(role))
                else:
                    if len(res[i + 1]) > len(role):
                        res[i + 1] = checkPrint(res[i + 1])
                        res[i + 1] = res[i + 1][0:len(role)-4]
                        res[i + 1] = res[i + 1] + ' ...'
                rspace = rspace.ljust(len(role) - len(res[i + 1]))
                
                if res[i + 2] == "null":
                    p = ""
                    res[i + 2] = p.ljust(len(title))
                else:
                    if len(res[i + 2]) > len(title):
                        res[i + 2] = checkPrint(res[i + 2])
                        res[i + 2] = res[i + 2][0:len(title)-4]
                        res[i + 2] = res[i + 2] + ' ...'
                tspace = tspace.ljust(len(title) - len(res[i + 2]))
                
                # from and to all null
                
                if res[i + 3] == 'null' and res[i + 4] == "null":
                    p = ""
                    From_To = p.ljust(len(FROM))
                elif res[i + 4] == "null":
                    From_To = res[i + 3] + ' / now'
                    if len(From_To) > len(FROM):
                        From_To = checkPrint(From_To)
                        From_To = From_To[0:len(FROM)-4]
                        From_To = From_To + ' ...'                      
                    fspace = fspace.ljust(len(FROM) - len(From_To))
                elif res[i + 4] != "null" and res[i + 3] != "null":
                    From_To = res[i + 3]+' / '+res[i + 4]
                    if len(From_To) > len(FROM):
                        From_To = checkPrint(From_To)
                        From_To = From_To[0:len(FROM)-4]
                        From_To = From_To + ' ...'                      
                    fspace = fspace.ljust(len(FROM) - len(From_To))                     

                print   Vspace, "| " + EntrySpace[1:len(EntrySpace)] + "|" + res[i] + ospace + "|" + res[i + 1] +  rspace + "|" + res[i + 2] + tspace + "|" + From_To + fspace + "|"
        elif key == 'Spouses':
            subentrySpace = ""
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            res = InfoBox[curType][key].split('\n')
            content = res[0] + " "
            if res[1] != "null" and res[2] != "null":
                content += "("+res[1] + " / " + res[2] + ")"
            elif res[1] != "null":
                content += "(" + res[1] + " / " + "now" + ")"
            rightspace = ""
            rightspace = rightspace.ljust(len(ValueSpace) - len(content))           
            print Vspace, "| " + key + subentrySpace + content + rightspace + "|"
            for i in range(3, len(res)-2, 3):
                content = res[i] + " "
                if res[i + 1] != "null" and res[i + 2] != "null":
                    content += "(" + res[i + 1] + " / " + res[i + 2] + ")"
                elif res[i + 1] != "null":
                    content += res[i + 1]
                rightspace = ""
                rightspace = rightspace.ljust(len(ValueSpace) - len(content))           
                print Vspace, "| " + EntrySpace + content + rightspace + "|"
            
        else:
            subentrySpace = ""
            subentrySpace = subentrySpace.ljust(len(EntrySpace) - len(key))
            res = InfoBox[curType][key].split('\n')
            if len(res[0]) > len(ValueSpace):
                    res[0] = res[0][0:len(ValueSpace) - 4]
                    res[0] = res[0] + ' ...'
            rightspace = ""
            rightspace = rightspace.ljust(len(ValueSpace) - len(res[0]))
            p = checkPrint(res[0])
            print Vspace, "| " + key + subentrySpace + p + rightspace + "|"
            
            for index in range(1,len(res)):
                if len(res[index]) > len(ValueSpace):
                    res[index] = res[index][0:len(ValueSpace) - 4]
                    res[index] = res[index] + ' ...'
                rightspace = ""
                rightspace = rightspace.ljust(len(ValueSpace) - len(res[index]))
                p = checkPrint(res[index])
                print Vspace,"| " + EntrySpace + p + rightspace +"|"
        # fid.close()
    
def extractCompound(info, Property):
    global Compound
    global InfoBox
    global Type
    global entityType
    global TypefindList
    
    for val in info:
        for tofind in Compound[Property]:
            if tofind in val['property']:
                if len(val['property'][tofind]['values']) > 0:
                    for i in val['property'][tofind]['values']:
                        content = i['text'].encode("utf-8")
                        try:
                            if tofind == '/sports/sports_team_roster/position':
                                InfoBox[Type[Property]['type']][Type[Property]['entry']] += content + ". "
                            else:
                                InfoBox[Type[Property]['type']][Type[Property]['entry']] += content + '\n'
                        except:
                            if tofind == '/sports/sports_team_roster/position':
                                InfoBox[Type[Property]['type']][Type[Property]['entry']] = content + " "
                            else:
                                InfoBox[Type[Property]['type']][Type[Property]['entry']] = content + '\n'
                else:
                    content = "null"
                    try:
                        InfoBox[Type[Property]['type']][Type[Property]['entry']] += content + '\n'
                    except:
                        InfoBox[Type[Property]['type']][Type[Property]['entry']] = content + '\n'
            else:
                content = "null"
                try:
                    InfoBox[Type[Property]['type']][Type[Property]['entry']] += content + '\n'
                except:
                    InfoBox[Type[Property]['type']][Type[Property]['entry']] = content + '\n'

            
            if tofind == '/sports/sports_team_roster/position' and content != "null":
                InfoBox[Type[Property]['type']][Type[Property]['entry']] +=  '\n'


def findType(response):
    global infoBox
    global entityType
    for t in response["property"]:
        if '/people/person' in t:
            entityType['Person'] = True
    if entityType['Person'] == True :
        for t in response["property"]:
            if '/book/author' in t:
                entityType['Author'] = True
            if '/film/actor'  in t or '/tv/tv_actor' in t:
                entityType['Actor'] = True
            if '/organization/organization_founder' in t or '/business/board_member' in t:
                entityType['BusinessPerson'] = True
    else:
        for t in response["property"]:
            if '/sports/sports_league' in t:
                entityType['League'] = True
                break
            elif '/sports/sports_team' in t or '/sports/professional_sports_team' in t:
                entityType['SportsTeam'] = True
                break 
        
def checkType(response):
    global entityType
    for i in entityType:
        if entityType[i] == True:
            return True
    return False
def extractInfo(response):
    global Isfinish
    global Type
    global InfoBox
    global Name
    global entityType
    global TypefindList
        
    InfoBox['name'] = Name
    findType(response)
    if (checkType(response) == False) :
        return

    if (entityType["Person"] == True):
        helpExtract("Person", response)
    if (entityType["Author"] == True):
        helpExtract("Author", response)
    if (entityType["Actor"] == True):
        helpExtract("Actor", response)
    if (entityType["BusinessPerson"] == True):
        helpExtract("BusinessPerson", response)
    if (entityType["League"] == True):
        helpExtract("League", response)
    if (entityType["SportsTeam"] == True):
        helpExtract("SportsTeam", response)

    helpExtract("Descriptions", response)
    Isfinish = True
    Print()

def helpExtract(curType, response):
    global Isfinish
    for tofind in TypefindList[curType]:
        if  tofind in response["property"]:
            
            t = tofind
            T = tofind
            if Type[T]['type'] == 'General' or entityType[Type[T]['type']] == True :
                # empty value for original json
                try:
                    a = response['property'][t]['valuetype']
                except:
                    continue
                if response['property'][t]['valuetype'] == "compound":
                    extractCompound(response['property'][t]['values'], T)
                else:
                    if t == '/people/deceased_person/cause_of_death':
                            try:
                                InfoBox[curType][Type[T]['entry']] += ' cause: ('
                            except:
                                InfoBox[curType][Type[T]['entry']] = ' cause: ('
                    elif t == '/people/deceased_person/place_of_death':
                            try:
                                InfoBox[curType][Type[T]['entry']] += ' at ' + response['property'][t]['values'][0]['text'] + ", "
                            except:
                                InfoBox[curType][Type[T]['entry']] = ' at ' + response['property'][t]['values'][0]['text'] + ", "
                            continue

                    elif t == '/people/deceased_person/date_of_death':
                            try:
                                InfoBox[curType][Type[T]['entry']] += response['property'][t]['values'][0]['text'] + " "
                            except:
                                InfoBox[curType][Type[T]['entry']] = response['property'][t]['values'][0]['text'] + " "
                            continue
                    elif t == '/common/topic/description':
                        InfoBox[curType][Type[T]['entry']] = response['property'][t]['values'][0]['value'].replace("\n", " ").encode("utf-8")
                        continue
                    for val in response['property'][t]['values']:
                        try:
                            if t == '/people/deceased_person/cause_of_death' :
                                InfoBox[curType][Type[T]['entry']] += val['text'].encode("utf-8") + " "
                            else:
                                InfoBox[curType][Type[T]['entry']] += val['text'].encode("utf-8") + '\n'
                    
                        
                        except:
                            if t == '/people/deceased_person/cause_of_death' :
                                InfoBox[curType][Type[T]['entry']] = val['text'].encode("utf-8") + " "
                            else:
                                InfoBox[curType][Type[T]['entry']] = val['text'].encode("utf-8") + '\n'
                    if t == '/people/deceased_person/cause_of_death':
                            try:
                                InfoBox[curType][Type[T]['entry']] += ')'
                            except:
                                InfoBox[curType][Type[T]['entry']] = ')'


    

##################################
############# PART2 ##############
    
# the main method to answer the query
def answer(key, query):
    validQuery = checkValid(query)
    if not validQuery:
        print 'Wrong question!!! Please comply strictly with "who created <X>?" format!'
    else:
        baseURL = 'https://www.googleapis.com/freebase/v1/mqlread?'
        bookQuery = '[{ \
                        "/book/author/works_written": [{ \
                                "a:name": null, \
                                "name~=": "' + validQuery + '" \
                        }], \
                        "id": null, \
                        "name": null, \
                        "type": "/book/author" \
                    }]'
        
        bookURL = baseURL + 'query=' + bookQuery + '&key=' + key

        organQuery = '[{ \
                        "/organization/organization_founder/organizations_founded": [{ \
                                "a:name": null, \
                                "name~=": "' + validQuery + '" \
                        }], \
                        "id": null, \
                        "name": null, \
                        "type": "/organization/organization_founder" \
                    }]'
        
        organURL = baseURL + 'query=' + organQuery + '&key=' + key
        
        bookAnswer = json.loads(urllib.urlopen(bookURL).read())
        organAnswer = json.loads(urllib.urlopen(organURL).read())

        # combine the two answers and sort by personInfo name
        answer = bookAnswer["result"] + organAnswer["result"]
        # sort the answer by name
        answer.sort(key=lambda x: x["name"])

        printResults(answer, validQuery)


# Checks if the query is in the 'Who created <X>?' format
def checkValid(query):
    query = query.lower()
    # print query       
    matchedQuery = re.match("who created (.*).* ?", query[:-1])
    if matchedQuery:
        return matchedQuery.group(1)        
    else:
        return False

# print the results
def printResults(answer, validQuery):
    rowNum = 1
    index = 0
    print "\n\n"
    if not answer:
        print "It seems no one created [" + validQuery + "]"
    samePersonInfo = []
    # check if there is any person do the same role in the answer dict
    for num in range(len(answer)):
        personInfo = answer[num]
        if num != 0 and personInfo["name"] == answer[num-1]["name"] and personInfo["type"] == answer[num-1]["type"]:
            continue
        if index < len(answer)-1:
            nextPersonInfo = answer[index+1]
            while nextPersonInfo["name"] == personInfo["name"] and nextPersonInfo["type"] == personInfo["type"]:
                samePersonInfo.append(nextPersonInfo)
                index += 1
                if index == len(answer):
                    break
                nextPersonInfo = answer[index+1]
        
        row = str(rowNum) + ". "
        if personInfo["type"] == "/book/author":
            row += personInfo["name"] + " (as Author) created "
            for work in personInfo["/book/author/works_written"]:
                row += "<" + work["a:name"] + ">, "
                for samePerson in samePersonInfo:
                    for works in samePerson["/book/author/works_written"]:
                        row += "<" + works["a:name"] + ">, "
        elif personInfo["type"] == "/organization/organization_founder":
            row += personInfo["name"] + " (as BusinesspersonInfo) created "
            for org in personInfo["/organization/organization_founder/organizations_founded"]:
                row += "<" + org["a:name"] + ">, "
                for samePerson in samePersonInfo:
                    for works in samePerson["/organization/organization_founder/organizations_founded"]:
                        row += "<" + works["a:name"] + ">, "        

        print row
        rowNum += 1
        index += 1
        samePersonInfo = []
    print "\n\n"

def error():
    print 'Usage:' + "\n" + ' \
    1. -key <account_key> -q <query> -t [infobox|question]' + "\n" + ' \
         If the type is infobox (i.e., -t infobox) the system tries to find the most relevant entity to the query <query> and create an infobox about it.' + "\n" + ' \
         If the type is question (i.e., -t question), the system tries to answer the question if it is of type "Who created [X]?".' + "\n" + ' \
         Note that the query has to be given as a single parameter.' + "\n" + ' \
    2. -key <account_key> -f <file_with_queries> -t [infobox|question]' + "\n" + ' \
         If the type is infobox (i.e. -t infobox) the system reads the file <file_with_queries> and treats each line as a query for infobox creation.' + "\n" + ' \
         If the type is question (i.e., -t question), the system treats each line of the <file_with_queris> files as a "Who created [X]?" question and tries to answer it.' + "\n" + ' \
         Note that the file name has to be given as a single parameter.' + "\n" + ' \
    3. -key <account_key>' + "\n" + ' \
         A shell is spawned for interactive queries (either for infobox creation or question answering). This functionality is not required for your implementation.' + "\n" + ' \
    4. --help | -h' + "\n" + ' \
         What you see :)'
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\n"
        exit()
    

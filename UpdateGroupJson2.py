import pywikibot
import json
from datetime import datetime, timezone

site = pywikibot.Site('en', 'wikipedia');
metawiki = pywikibot.Site('meta', 'meta');

def globalallusers(site,group):
    agugen = pywikibot.data.api.ListGenerator('globalallusers',\
                               aguprop='groups', site=site)
    if group:
        agugen.request['agugroup'] = group
    return agugen

def sortkeys(key):
    sortkeyDict = {
        "sysop" : "A",
        "arbcom" : "ARB",
        "bureaucrat" : "B",
        "checkuser" : "CU",
        "oversight" : "CV",
        "interface-admin" : "IA",
        "abusefilter" : "EFM",
        "abusefilter-helper" : "EFH",
        "accountcreator" : "ACC",
        "autoreviewer" : "AP",
        "extendedmover" : "PM",
        "filemover" : "FM",
        "massmessage-sender" : "MMS",
        "patroller" : "NPR",
        "reviewer" : "PCR",
        "rollbacker" : "RB",
        "global-renamer" : "GRe",
        "global-rollbacker" : "GRb",
        "templateeditor" : "TE",
        "otrs-member" : "OTRS",
        "steward" : "S"
    }
    return sortkeyDict[key]

combinedJsDataPage = pywikibot.Page(site,
                         "User:MDanielsBot/markAdmins-Data.js")
combinedJsonDataPage = pywikibot.Page(site,\
                          "User:MDanielsBot/markAdmins-Data.json")

# localGroups = ["abusefilter", "abusefilter-helper", "accountcreator",\
#           "autoreviewer", "bureaucrat", "checkuser", "extendedmover",\
#           "filemover", "interface-admin", "massmessage-sender", "oversight",\
#           "patroller", "reviewer", "rollbacker", "sysop", "templateeditor"]
localGroups = ["abusefilter", "abusefilter-helper", "accountcreator",\
          "bureaucrat", "checkuser", "extendedmover", "filemover",\
          "interface-admin", "massmessage-sender", "oversight",\
          "sysop", "templateeditor"]
extraLocalGroups = ["autoreviewer", "patroller", "reviewer", "rollbacker"]
globalGroups = ["otrs-member" , "steward", "global-rollbacker"]
metaGroups = ["global-renamer"]
arbcomJson = pywikibot.Page(site, "User:AmoryBot/crathighlighter.js/arbcom.json").get()
arbcom_members = json.loads(arbcomJson)

outputDict = {}

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +\
      " -- Starting!", flush=True)

for group in localGroups:
    for user in site.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in globalGroups:
    for user in globalallusers(site, group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]
            
for user in arbcom_members:
    if user in outputDict.keys():
        outputDict[user].append("arbcom")
    else:
        outputDict[user] = ["arbcom"]

for group in extraLocalGroups:
    for user in site.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in metaGroups:
    for user in metawiki.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +\
      " -- Computing output...", flush=True)

# Sort our flags
for item in outputDict:
    outputDict[item].sort(key=sortkeys)

# Construct combined JSON page
pageTop = "mw.hook('userjs.script-loaded.markadmins').fire("
outputJson = json.dumps(outputDict, sort_keys=True,\
                     indent=4, separators=(',', ': '), ensure_ascii=False)
pageBottom = ");"

newText = pageTop + outputJson + pageBottom;
oldJspage = combinedJsDataPage.get()
oldJsonpage = combinedJsonDataPage.get()
    
if (newText != oldJspage or outputJson != oldJsonpage):
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")\
             + " -- Updated!", flush=True)
    combinedJsDataPage.put(newText, "Update markadmins data")
    combinedJsonDataPage.put(outputJson, "Update markadmins data")
else:
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")\
             + " -- No changes", flush=True);
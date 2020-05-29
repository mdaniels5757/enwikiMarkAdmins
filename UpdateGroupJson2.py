import pywikibot
import json
from datetime import datetime, timezone

site = pywikibot.Site('en', 'wikipedia');

def globalallusers(site,group):
    agugen = pywikibot.data.api.ListGenerator('globalallusers',\
                               aguprop='groups', site=site)
    if group:
        agugen.request['agugroup'] = group
    return agugen


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
globalGroups = ["otrs-member" , "steward"]
arbcom_members = json.loads(pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/arbcom.json").get())

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

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +\
      " -- Computing output...", flush=True)

# Construct combined JSON page
pageTop = "mw.hook('userjs.script-loaded.markadmins').fire("
outputJson = json.dumps(outputDict, sort_keys=True,\
                     indent=4, separators=(',', ': '), ensure_ascii=False)
pageBottom = ");"

newText = pageTop + outputJson + pageBottom;

if (newText != combinedJsDataPage.get()):
    combinedJsDataPage.put(newText, "Update markadmins data")
    combinedJsonDataPage.put(outputJson, "Update markadmins data")
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")\
             + " -- Updated!", flush=True)
else:
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")\
             + " -- No changes", flush=True);
import pywikibot
import json

site = pywikibot.Site('en', 'wikipedia');
combinedJsonPage = pywikibot.Page(site, "User:MDanielsBot/markAdmins-Data.js")

# First, get all of the jsons!
adminJson = pywikibot.Page(site, "User:Amalthea_(bot)/userhighlighter.js/sysop.js").get()
arbcomJson = pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/arbcom.json").get()
cratJson = pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/bureaucrat.json").get()
cuJson = pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/checkuser.json").get()
intadminJson = pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/interface-admin.json").get()
osJson = pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/oversight.json").get()
stewardJson = pywikibot.Page(site, "User:Amorymeltzer/crathighlighter.js/steward.json").get()

admins = json.loads(adminJson)
arbcom_members = json.loads(arbcomJson)
crats = json.loads(cratJson)
cus = json.loads(cuJson)
intadmins = json.loads(intadminJson)
osers = json.loads(osJson)
stewards = json.loads(stewardJson)

# Process admins first, then stewards, then the rest.
outputDict = {}

for user in admins:
    if user in outputDict.keys():
        outputDict[user].append("sysop")
    else:
        outputDict[user] = ["sysop"]

for user in stewards:
    if user in outputDict.keys():
        outputDict[user].append("steward")
    else:
        outputDict[user] = ["steward"]

for user in arbcom_members:
    if user in outputDict.keys():
        outputDict[user].append("arbcom")
    else:
        outputDict[user] = ["arbcom"]

for user in crats:
    if user in outputDict.keys():
        outputDict[user].append("bureaucrat")
    else:
        outputDict[user] = ["bureaucrat"]

for user in cus:
    if user in outputDict.keys():
        outputDict[user].append("checkuser")
    else:
        outputDict[user] = ["checkuser"]

for user in intadmins:
    if user in outputDict.keys():
        outputDict[user].append("interface-admin")
    else:
        outputDict[user] = ["interface-admin"]

for user in osers:
    if user in outputDict.keys():
        outputDict[user].append("oversight")
    else:
        outputDict[user] = ["oversight"]

# Construct combined JSON page
pageTop = "mw.hook('userjs.script-loaded.markadmins').fire("
outputJson = json.dumps(outputDict, sort_keys=True,\
                     indent=4, separators=(',', ': '), ensure_ascii=False)
pageBottom = ");"

newText = pageTop + outputJson + pageBottom;
combinedJsonPage.put(newText, "Update markadmins data")
#print(newText)
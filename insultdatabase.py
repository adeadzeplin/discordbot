LIST_OF_ADJECTIVES = ["derpy","poopy","nazi","boiled","onion-breathed","belligerent","pre-pubescent","thorny","homophobic","calloused","vain","patronizing","defective","broken","unshaven","horny","defensive","unibrowed","bitchy","cruel","worthless","hostile","insufferable","dense","cavernous", "thick","feeble-minded","ape-like","nasty","impolite","clumsy","stupid","rude","ripe","dim-witted","gelatenous","shit","poopy","pussy-breath","dick-breath","tiny", "ugly","meanie","motherfuckin", "stank","wet","nick-lookin", "soggy","big","small","fat", "cancerous","cringe", "ass","stinky"]
LIST_OF_NOUNS = ["fart","benis","ape","mouthbreather","troglodyte","arse","scab","joke","brute","dandelion","orangutan","grunt","noob","dingleberry","wart","NPC","goblin","turd","twat","wanker","worm","idiot","oaf","baby", "motherfucker","cunt","ass","lobotomite","maggot", "cooter","bitch", "titty", "cum-stain","cum","cum-hole", "dickhead","bussy"]
import pickle


def updateAdjs(adj_list):
    pathname = f"adjectives.pickle"
    with open(pathname, "wb") as f:
        pickle.dump(adj_list, f)

def updateNouns(noun_list):
    pathname = f"nouns.pickle"
    with open(pathname, "wb") as f:
        pickle.dump(noun_list, f)

def loadADJs():
    try:
        with open("adjectives.pickle", "rb") as f:
             list_of_adjectives = pickle.load(f)
    except:
        list_of_adjectives = LIST_OF_ADJECTIVES
    return list_of_adjectives

def loadNOUNs():
    try:
        with open("nouns.pickle", "rb") as f:
             list_of_nouns = pickle.load(f)
    except:
        list_of_nouns = LIST_OF_NOUNS
    return list_of_nouns

def verify_new_noun(newnoun):
    if isinstance(newnoun,str):
        if len(newnoun.split(" ")) == 1:
            existsFlag = False
            noun_db = loadNOUNs()
            for nown in noun_db:
                if nown.lower() == newnoun.lower():
                    print("someone tried to add an existing word")
                    existsFlag = True
                    break
            if existsFlag == False:
                noun_db.append(newnoun.lower())
                updateNouns(noun_db)

                returnmessage = "the word: " + newnoun + " was added to the nowns database"
            else:
                returnmessage = f"the word: " + newnoun.lower() + " already exists in the nouns database"
        else:
            returnmessage = f"incorect word formating " + newnoun.lower()
    else:
        returnmessage = f"incorect word formating " + newnoun.lower()
    print(returnmessage)
    return returnmessage


def verify_new_adj(newadj):
    if isinstance(newadj,str):
        if len(newadj.split(" "))==1:
            existsFlag = False
            adj_db = loadADJs()
            for adj in adj_db:
                if adj.lower() == newadj.lower():
                    existsFlag = True
                    break
            if existsFlag == False:
                adj_db.append(newadj.lower())
                updateAdjs(adj_db)
                returnmessage = "the word: "+ newadj.lower()+" was added to the adj database"
            else:
                returnmessage = f"the word: "+ newadj.lower()+" already exists in the adj database"
        else:
            returnmessage = f"incorect word formating "+ newadj.lower()
    else:
        returnmessage = f"incorect word formating " + newadj.lower()
    print(returnmessage)
    return returnmessage

def printoutDB():
    response = "Nouns:\n"
    nouns = loadNOUNs()
    nouns.sort()
    adjs = loadADJs()
    adjs.sort()
    for n in nouns:
        response += " " + n
    response += "\nAdjectives:\n"
    for a in adjs:
        response += " " + a
    return response


if __name__ == "__main__":
    verify_new_adj('flimSY god')
    print(loadADJs())
    verify_new_noun('PEE_PISSER')
    print(loadNOUNs())
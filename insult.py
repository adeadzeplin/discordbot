import numpy as np

import insultdatabase


italics = '*'
# underital_f = "__*"
# underital_b = "*__"
bold = '**'

# underbold_f = '__**'
# underbold_b = '**__'

bolditalic = '***'

# underbolditalic_f = '__***'
# underbolditalic_b = '***__'

underline = '__'
strikethrough = '~~'
none = ''
textmods = [none,underline,bolditalic,bold,italics]

def getAdjs(num):
    temp_adj =''
    adj_list = insultdatabase.loadADJs()
    for i in range(num):
        temp_adj += adj_list[np.random.randint(len(adj_list)-1)]
        temp_adj += " "
    return temp_adj
def getNoun():
    temp_noun =''
    noun_list = insultdatabase.loadNOUNs()
    temp_noun += noun_list[np.random.randint(len(noun_list)-1)]
    temp_noun += " "
    return temp_noun

def insult(*, formated=True,adjmax=2,article = True):
    insultstring = ""

    if np.random.random() >= 0.9:
        RandAdjNum = np.random.randint(0, adjmax)
    else:
        if adjmax == 1:
            RandAdjNum = 1
        else:
            RandAdjNum = np.random.randint(1,adjmax)
    insultstring += getAdjs(RandAdjNum) + getNoun()
    vowelFlag = False
    for vowel in "aeiou":
        if vowel == insultstring[0]:
            vowelFlag = True
            break

    txtmod = textmods[np.random.randint(len(textmods)-1)]
    if formated == True:
        insultstring = txtmod + insultstring + txtmod

    if article == True:
        if vowelFlag == True:
            insultstring = "an " + insultstring
        else:
            insultstring = "a " + insultstring

    return insultstring

if __name__ == '__main__':
    print(insult())
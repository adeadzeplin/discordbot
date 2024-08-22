import numpy as np

import insultdatabase

# TODO: Consider moving text formatting constants to a separate configuration file
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
    """
    Generate a string of random adjectives.
    
    :param num: Number of adjectives to generate
    :return: String of adjectives
    """
    # TODO: Implement error handling for invalid 'num' values
    temp_adj =''
    adj_list = insultdatabase.loadADJs()
    for i in range(num):
        temp_adj += adj_list[np.random.randint(len(adj_list)-1)]
        temp_adj += " "
    return temp_adj

def getNoun():
    """
    Generate a random noun.
    
    :return: String containing a single noun
    """
    temp_noun =''
    noun_list = insultdatabase.loadNOUNs()
    temp_noun += noun_list[np.random.randint(len(noun_list)-1)]
    temp_noun += " "
    return temp_noun

def insult(*, formated=True,adjmax=2,article = True):
    """
    Generate an insult string.
    
    :param formated: Whether to apply text formatting
    :param adjmax: Maximum number of adjectives to use
    :param article: Whether to include an article ('a' or 'an')
    :return: Generated insult string
    """
    # REVIEW: Consider breaking this function into smaller, more manageable functions
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

# TODO: Implement comprehensive error handling throughout the script
# TODO: Add unit tests for each function
# REVIEW: Consider the ethical implications of an insult generator
# TODO: Implement logging for better debugging and monitoring
# TODO: Optimize performance, especially for larger datasets
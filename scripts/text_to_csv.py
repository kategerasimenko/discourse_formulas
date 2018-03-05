from scripts.feature_extraction import *
import re
import html

def get_data(rawtext,filename,delete_speakers):
    data = [['Text_id', 'Text', 'Len', 'Subject', 'Object',  'Predicate', 'Emotions',  'Imperative', 'Question',
             'First', 'NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ']]
    
    rawtext = html.unescape(rawtext)
    rawtext = rawtext.replace('¬','')
    if delete_speakers:
        rawtext = PREP_delete_speakers(rawtext)
    linedtext = TextByLines(rawtext)
    allpseudoclauses_raw = []
    allpseudoclauses = []
    disc_target = []

    for j in linedtext.lines:
        curlinesplitted = splitbylist(j, ['.',',','?','!',' - ',':',';',' или ',' и ','(',')', '\n','…','"','—',' – ','»','”'])
        firstalreadybeen = False
        firstthree = 1
        for i in curlinesplitted:
            if re.findall('[А-яЁё]', i, flags=re.DOTALL):
                disc, i = is_discourse(i.strip())
                disc_target.append(disc)
                if firstthree <= 3:
                    allpseudoclauses.append(Pseudoclause(i, str(disc), True))
                else:
                    allpseudoclauses.append(Pseudoclause(i, str(disc), False))
                firstthree += 1

    for n in range(len(allpseudoclauses)):
        new_words = allpseudoclauses[n].text.strip('.,?!-:;()…"—–{}«»“”/\\').strip()
        row = [filename[:-4], new_words, len(new_words.split())]

        if len(allpseudoclauses[n].subject) > 0:
            row.append(1)
        else:
            row.append(0)

        if allpseudoclauses[n].object == '<<not required>>':
            row.append(0)
        elif allpseudoclauses[n].object:
            row.append(1)
        else:
            row.append(-1)

        if allpseudoclauses[n].predicate != 'no predicate':
            row.append(1)
        else:
            row.append(0)

        if allpseudoclauses[n].emotions:
            row.append(1)
        else:
            row.append(0)
        if allpseudoclauses[n].imperativeness:
            row.append(1)
        else:
            row.append(0)
        if allpseudoclauses[n].isquestion:
            row.append(1)
        else:
            row.append(0)
        if allpseudoclauses[n].firstinline:
            row.append(1)
        else:
            row.append(0)
        POS_list = []
        for i in ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ']:
            POS_list.append(allpseudoclauses[n].POS_vector[i])
        row += POS_list
        data.append(row)
    return data


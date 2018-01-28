#import pymorphy2_dicts
# pymorphy2_dicts.get_path()


import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

#NOUN	имя существительное	хомяк
#ADJF	имя прилагательное (полное)	хороший
#ADJS	имя прилагательное (краткое)	хорош
#COMP	компаратив	лучше, получше, выше
#VERB	глагол (личная форма)	говорю, говорит, говорил
#INFN	глагол (инфинитив)	говорить, сказать
#PRTF	причастие (полное)	прочитавший, прочитанная
#PRTS	причастие (краткое)	прочитана
#GRND	деепричастие	прочитав, рассказывая
#NUMR	числительное	три, пятьдесят
#ADVB	наречие	круто
#NPRO	местоимение-существительное	он
#PRED	предикатив	некогда
#PREP	предлог	в
#CONJ	союз	и
#PRCL	частица	бы, же, лишь
#INTJ	междометие	ой

#def compare_by_alph(str1, str2, alph = 'abcdefghijklmnopqrstuvwxyz'):
#    alph = alph.split('')

def index_in_array(value, array):
    for i in range(len(array)):
        if array[i] == value:
            return i
    return len(array)

def sort_dic_by_key_order(dic, default_key_order = ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ'], key_order = []):
    out = []
    if key_order == []:
        key_order = default_key_order


class TextByLines:
    def __init__(self, intext):
        self.text = intext
        self.lines = self.text.split('\n')


def joinarrays(a1, a2):
    for i in a2:
        a1.append(i)
    return a1

    
def PREP_delete_speakers (text):
    new_text = re.sub('\n *[А-ЯЁ ]+?(?: ?\(.+?\))? ?[.:]', '\n', text)
    if len(new_text) > len(text) - 500:
        print('speakers not in uppercase')
        new_text = re.sub('\n *[А-яЁё]+?(?: ?\(.+?\))? ?[.:]','\n',text)
    return new_text

    
def is_discourse(text):
    if ('}}' in text and not text.startswith('}}')) or ('{{' in text and not text.endswith('{{')):
        d = 1
        before = re.search('(^[^{}]+?\\w+.*?){{', text)
        if before is not None:
            d = 0
        else:
            after = re.search('}}([^{}]+?\\w+.*)', text)
            if after is not None:
                d = 0
    else:
        d = 0
    text = text.replace('{{', '')
    text = text.replace('}}', '')
    return d, text.lower()


def splitbylist (a, splist):
    for i in splist:
        a = a.replace(i, i+'<<splitter>>')
    out = a.split('<<splitter>>')
    return out


def isverb(word):
    level = 0
    wordparse = morph.parse(word)
    Vfeatures = {}
    for i in wordparse:
        level += 1
        if i.tag.POS == 'VERB':
            Vfeatures['person'] = i.tag.person
            Vfeatures['number'] = i.tag.number
            Vfeatures['gender'] = i.tag.gender
            Vfeatures['transitivity'] = i.tag.transitivity
            return [True, level, Vfeatures]
    return [False, level, Vfeatures]


def isnoun(word):
    level = 0
    wordparse = morph.parse(word)
    Nfeatures = {}
    for i in wordparse:
        level += 1
        if i.tag.POS == 'NOUN' or i.tag.POS == 'NPRO':
            Nfeatures['person'] = i.tag.person
            Nfeatures['number'] = i.tag.number
            Nfeatures['gender'] = i.tag.gender
            Nfeatures['case'] = i.tag.case
            return [True, level, Nfeatures]
    return [False, level, Nfeatures]


def isimperative(word):
    level = 0
    wordparse = morph.parse(word)
    for i in wordparse:
        level += 1
        if i.tag.POS == 'VERB' and i.tag.mood == 'impr':
            return [True, level]
    return [False, level]


def agreement(verb, noun):
    Vfeatures = isverb(verb)[2]
    for j in morph.parse(noun):
        counter = 1
        if Vfeatures == {}:
            Vfeatures = {'person':None, 'number':None, 'gender':None}
        if Vfeatures['person'] != None and Vfeatures['person'] != j.tag.person and j.tag.person != None:
            counter = 0
        if Vfeatures['number'] != None and Vfeatures['number'] != j.tag.number and j.tag.number != None:
            counter = 0
        if Vfeatures['gender'] != None and Vfeatures['gender'] != j.tag.gender and j.tag.gender != None:
            counter = 0
        if counter == 1 and j.tag.case == 'nomn' and (j.tag.POS == 'NOUN' or j.tag.POS == 'NPRO'):
            return True
    return False

def define_POS(word, predicate_occupied = 0):
    parse = morph.parse(word)
    if predicate_occupied == 0:
        out = parse[0].tag.POS
        return out
    else:
        for i in parse:
            if i.tag.POS != 'VERB':
                return i.tag.POS
    return parse[0].tag.POS
 
class Pseudoclause():
    def __init__(self, clausetext, marking, firstinline):
        self.marked_as = marking
        self.firstinline = firstinline
        self.dmp = 0 #discourse marker points
        self.decision = False
        self.text = clausetext
        self.predicate = 'no predicate'
        self.words = []
        self.subject = ''
        self.subjectposition = 50
        self.object = ''
        self.POS_vector = {}
        self.transitivity = 'irrelevant'
        self.emotions = False
        if re.findall('!', self.text) != []:
            self.emotions = True
        self.isquestion = False
        if re.findall('\?', self.text) != []:
            self.isquestion = True

        #выявление и обработка предиката
        levelcounter = 50
        for i in self.text.split():
            curword = i.strip(',.?-!:;()"«»“”')
            self.words.append(curword.lower())
            verblikeness = isverb(curword)
            if verblikeness[0] == True and verblikeness[1] < levelcounter:
                levelcounter = verblikeness[1]
                self.transitivity = verblikeness[2]['transitivity']
                self.predicate = curword
        for i in ['NOUN', 'ADJF', 'ADJS', 'COMP', 'VERB', 'INFN', 'PRTF', 'PRTS', 'GRND', 'NUMR', 'ADVB', 'NPRO', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ']:
            self.POS_vector[i] = 0
        for curword in self.words:
            if curword != self.predicate:
                try:
                    self.POS_vector[define_POS(curword, 1)] += 1
                except:
                    continue
            else:
                try:
                    self.POS_vector['VERB'] += 1
                except:
                    continue            
        self.imperativeness = isimperative(self.predicate)[0]

        #выявление и обработка субъекта
        for i in range(len(self.words)):
            if agreement (self.predicate, self.words[i]) == True:
                self.subject = self.words[i]
                self.subjectposition = i
                break

        # выявление и обработка объекта
        if self.transitivity == 'tran':
            for i in range(len(self.words)):
                for j in morph.parse(self.words[i]):
                    if (((j.tag.POS == 'NOUN' or j.tag.POS == 'NPRO') and j.tag.case == 'accs') or j.tag.POS == 'INFN') and i != self.subjectposition and morph.parse(self.words[i-1])[0].tag.POS != 'PREP':
                        self.object = self.words[i]
        else:
            self.object = '<<not required>>'

    def get_features(self):
        features = {}
        # features['marked_as'] = self.marked_as
        features['text'] = self.text
        features['subject'] = self.subject
        features['emotions'] = self.emotions
        features['imperativeness'] = self.imperativeness
        features['isquestion'] = self.isquestion
        features['length'] = self.length
        features['predicate'] = self.predicate
        features['object'] = self.object
        features['transitivity'] = self.transitivity
        features['firstinline'] = self.firstinline
        features['isNu'] = self.isNu
        features['isDa'] = self.isDa
        features['POS_vector'] = self.POS_vector
        return features

    def __repr__(self):
        out  = ''
        features = self.get_features()
        for i in features:
            out += i
            out += ': '
            out += str(features[i])
            out += '\n'
        out += '===\nTARGET:\n'
        out += self.marked_as
        return out
        
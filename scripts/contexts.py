import re
from collections import deque, OrderedDict

def PREP_delete_speakers (text,repl = ''):
    new_text = re.sub('\n[\t ]*[А-ЯЁ ]+?(?: ?\(.+?\))?[.:]', '\n'+repl, text)
    if len(new_text) > len(text) - 500:
        new_text = re.sub('\n[\t ]*[А-яЁё]+?(?: ?\(.+?\))?[.:]','\n'+repl,text)
    return new_text


def get_etiquette():
    with open('./scripts/etiquette_list.txt', 'r', encoding='utf-8-sig') as f:
        etiquette = {x.strip() for x in f.readlines()}
    return etiquette

 
def table_for_app(table,text,speakers):
    etiquette = get_etiquette()
    formula_table = open('formula_list.csv','w',encoding='utf-8-sig')
    formula_table.write(';'.join(['document','left context','formula','','','unique','count'])+'\n')
    contexts(text,table,formula_table,etiquette,speakers)
    formula_table.close()

    
def go_through_texts(table,speakers,new):
    textlist = list(OrderedDict.fromkeys([x[0] for x in table]))
    print(textlist)
    etiquette = get_etiquette()
    formula_table = open(new+'formula_list.csv','w',encoding='utf-8-sig')
    formula_table.write(';'.join(['document','left context','formula','','','unique','count'])+'\n')
    for file in textlist:
        try:
            text = open('./texts/'+file+'.txt','r',encoding='cp1251').read()
        except:
            text = open('./texts/'+file+'.txt','r',encoding='utf-8-sig').read()
        new_table = table_for_text(table,file)
        annotated_text = contexts(text,new_table,formula_table,etiquette,speakers)
        annotated_textfile = open(new+file+'_annotated.txt','w',encoding='utf-8-sig')
        annotated_textfile.write(annotated_text)
        annotated_textfile.close()        
    formula_table.close()


def table_for_text(table,textname):
    new_table = [x for x in table if x[0] == textname]
    return new_table


def regstr(formula):
    regstr = '['
    for i in formula:
        regstr += i+i.upper()+']['
    return regstr[:-1]


def regstr_splitters():
    regstr = '(?:'
    one_symbols = '['
    splitters = ['\.',',','\?','!',' -','\:',';',' ?или',' ?и','\}','\{',
                 ' -- ', '\(','\)', '\n+','…','"','—','–','»','«','[0-9]+','[A-z]+']
    for spl in splitters:
        if len(spl) == 1 or ('\\' in spl and len(spl) == 2) :
            one_symbols += spl[-1]
        else:
            regstr += spl+'|'
    regstr += one_symbols+']|)'
    return regstr


def del_conj(string):
    if string.endswith(' или'):
        return string[:-4]
    if string.endswith(' и'):
        return string[:-2]
    return string


def contexts(text,table,formula_table,etiquette,speakers):
    unique_deque = deque()
    text = text.replace(';',',')
    if speakers:
        text = PREP_delete_speakers(text,'\t')
    annotated_text = text
    spl = regstr_splitters()
    for n,row in enumerate(table):
        if type(row[3]) == str:
            unique_deque.append((row[3],row[4]))
        if row[1] in etiquette:
            row[2] = 1
        if row[2] == 1:
            if unique_deque:
                unique = unique_deque.popleft()
            else:
                unique = ('','')
            if n == 0:
                context = 'no context'
            else:
                if n == 1:
                    re_cl_context = '('+regstr(del_conj(table[n-1][1]))+' ?'+spl+'{1,3}\\s*?'+\
                                    spl+'{0,3} ?)('+regstr(del_conj(row[1]))+' ?'+spl+')'
                else:
                    re_cl_context = '('+regstr(del_conj(table[n-2][1]))+' ?'+spl+'{1,3}\\s*?'+\
                                    spl+'{0,3} ?'+regstr(del_conj(table[n-1][1]))+' ?'+spl+'{1,3}\\s*?'+\
                                    spl+'{0,3} ?)('+regstr(del_conj(row[1]))+' ?'+spl+')'
                phrase = re.search(re_cl_context,text)
                if not phrase:
                    context = 'context not found'
                else:
                    cl_context = phrase.group()
                    context_only = phrase.group(1)
                    formula_only = phrase.group(2)
                    annotated_text = annotated_text.replace(context_only+formula_only,context_only+'{{'+formula_only+'}}')
                    context_re = re.search('[.…!?]{1,3} ?[–—»)]?\s*?((?:[«(А-яЁёA-z0-9][^.…!?]*?[.…!?]{1,3}[»)]?\s*?){2}[^.…!?]*?'+re.escape(cl_context)+')',text)
                    if context_re is not None:
                        context = context_re.group(1)
                    else:
                        context = cl_context
                    context = re.sub('(\r?\n)+',' ',context)
                    context = context[:(len(context)-(len(row[1])+1))]
            formula_table.write(';'.join([row[0],context,row[1],'','',unique[0],str(unique[1])])+'\n')

    return annotated_text


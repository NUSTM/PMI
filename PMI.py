#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author:kou
@date:2014-11
"""

from __future__ import division 
from collections import defaultdict
import sys
reload(sys)
sys.setdefaultencoding('utf8') 
import math

LOG_LIM = 1E-300
endtag = [ '。/w', '？/w', '！/w', '；/w', '?/w', '!/w','./w']
#endtag = ['./m', '!/m', '?/m', '。/w', '？/w', '！/w', '；/w', '，/w', ',/w']
#endtag = [ '。/PU', '？/PU', '！/PU', './PU']
#endtag = ['但是/c','就是/d','只是/c','不过/c','可是/c','但/c']

def seedwords():  
    """
    get and expand seedwords
    """
    fpos = open('pos.txt','r')
    fneg = open('neg.txt','r')
    posdic = []
    negdic = []
    for word in fpos.readlines():
        posdic.append(word.strip().split()[0])
    for word in fneg.readlines():
        negdic.append(word.strip().split()[0])    
    return posdic, negdic

def read_text(path):  
    """
    read source file
    """
    sourfile = open(path,'r')
    get_doc_list = []
    for line in sourfile.readlines():
        line = line.replace('/NN','/n')
        line = line.replace('/VA','/a')
        line = line.replace('/AD','/d')
        line = line.replace('/VV','/v')
        line = line.replace('/CC','/cc')        
        get_doc_list.append(line)
    return get_doc_list

def constr_wordbag(get_doc_list, posdic, negdic):
    """
    construct wordbag
    """
    word_bag = []
    get_word_tag = {}
    for line in get_doc_list:  
        word_and_tag = line.split() 
        for word in word_and_tag:  
            if word in endtag:
                continue
            temp = word.split('/')  
            #排除一些英文字符
            if len(temp) != 2 :
                #print word
                continue
            if len(temp[1]) == 0 or temp[1] == ' ':
                #print word
                continue
            getword = temp[0]
            gettag = temp[1]
            if getword not in word_bag:
                word_bag.append(getword)   
            if not get_word_tag.has_key(getword):
                get_word_tag.update({getword:gettag})
    #把种子词库中的词添加到词袋中
    for word in posdic:
        if word not in word_bag:
            word_bag.append(word)  
        if not get_word_tag.has_key(word):
            get_word_tag.update({word:'a'})        
    for word in negdic:
        if word not in word_bag:
            word_bag.append(word)     
        if not get_word_tag.has_key(word):
            get_word_tag.update({word:'a'})  
    f = open('wordbag.txt','w')
    word_bag.sort()
    for i in word_bag:
        f.write(i+'\n')
    f.close()
    return word_bag, get_word_tag

def buidl_samp(get_doc_list, get_term_dict):   
    """
    tag word weather show in each line
    """
    doc_num = len(get_doc_list)
    term_num = len(get_term_dict)
    get_show_info = [[]*1 for i in range(term_num+1)]  #记录每个词的出现信息
    for i in range(doc_num):
        line = get_doc_list[i]   #一段评论
        word_and_tag = line.split()  #获得单个词
        for term_info in word_and_tag:
            temp = term_info.split('/')
            if len(temp) != 2:
                continue  
            if len(temp[1]) == 0 or temp[1] == ' ' :
                continue            
            word = temp[0]
            if get_term_dict.has_key(word):
                term_id = get_term_dict[word]
                #if i not in get_show_info[term_id]:   #记录单词在第i句话中出现,多次出现算一次
                get_show_info[term_id].append(i)
            else:
                print 'can\'t find!'
    return get_show_info

def pair(w1, w2):
    return (min(w1, w2), max(w1, w2))
 
def build_samp_xy(get_doc_list, get_term_dict):
    doc_num = len(get_doc_list)
    term_num = len(get_term_dict) 
    px = defaultdict(list)
    pxy = defaultdict(list)
    for i in range(doc_num):
        line = get_doc_list[i]   #一段评论
        word_and_tag = line.split()  #获得单个词  
        wordlist = []
        for term_info in word_and_tag:
            temp = term_info.split('/')
            if len(temp) != 2:
                continue  
            if len(temp[1]) == 0 or temp[1] == ' ' :
                continue  
            wordlist.append(temp[0])
        sent = list(set(wordlist))
        for j in range(len(sent)):  #遍历短句中的每一个单词                
                px[sent[j]].append(i)
                for k in range(j+1,len(sent)):
                    pxy[pair(sent[j],sent[k])].append(i)  #单词共现+1    
    return px,pxy
    
def getPMI(w1, w2, N):
        common = len(pxy[pair(w1,w2)]) + 1
        if len(px[w1]) == 0 :
            print 'w1',w1
            exit
        if len(px[w2]) == 0:
            print 'w2',w2
            exit
        if float(common) == 0:
            print 'c',common
            exit
        return math.log(2,float(common)*N / (len(px[w1]) * len(px[w2])))    
    
def getpmi_xy(px, pxy, term_dict, N ):
    pos = [x.strip() for x in open('pos.txt','r').readlines()]
    neg = [x.strip() for x in open('neg.txt','r').readlines()]
    fr = open('posPMI.txt','w')
    frn = open('negPMI.txt','w')
    for pw in pos:
        for w in term_dict:
            common = len(pxy[pair(pw,w)]) + 1
            if len(px[pw]) == 0 :
                #print 'pw',pw
                continue
            if len(px[w]) == 0:
                #print 'w',w
                continue
            if float(common) == 0:
                continue
            getpmi = math.log(2,float(common)*N / (len(px[pw]) * len(px[w])))              
            fr.write(pw + ' ' + w + '  ' + str(getpmi) + '\n')
    for nw in neg:
        for w in term_dict:
            common = len(pxy[pair(nw,w)]) + 1
            if len(px[nw]) == 0 :
                #print 'nw',nw
                continue
            if len(px[w]) == 0:
                #print 'w',w
                continue
            if float(common) == 0:
                continue
            getpmi = math.log(2,float(common)*N / (len(px[nw]) * len(px[w])))   
            frn.write(nw + ' ' + w + '  ' + str(getpmi) + '\n')  
    fr.close()
    frn.close()      
    
        
def get_pmi(show_info, term_dict, posdic, negdic, doc_term_list):
    """
    get everywords' pmi value to seedwords
    """
    sum_line = len(doc_term_list)   #获得语料数
    sum_term = len(term_dict)+1   #获得单词数
    poslist = []
    neglist = []
    for word in posdic:
        posword_id = term_dict[word]  #获得积极种子词的编号
        poslist.append(posword_id)   #积极种子词的编号列表
    getpospmi = [[0]*sum_term for i in range(len(poslist))]
    for word in negdic:
        negword_id = term_dict[word]
        neglist.append(negword_id)   #消极词的编号
    getnegpmi = [[0]*sum_term for i in range(len(neglist))]
    for i in range(len(poslist)):
        posword = poslist[i]  #对其中的每个pos的词遍历
        for everyword in range(1, sum_term):
            if everyword == posword:  #如果是单词本身，不计算PMI值
                continue
            tempset_pw = set(show_info[posword])  #分别查看两个词的出现信息
            tempset_ew = set(show_info[everyword])
            #取交集，一起出现的次数
            inter = list(tempset_pw.intersection(tempset_ew)) 
            common = len(inter) + 1   #防止出现0
            pos_num = len(list(show_info[posword]))  #积极的词出现的次数
            other_num = len(list(show_info[everyword]))  #其他单词出现的次数
            if pos_num == 0 or other_num == 0:
                continue
            res = (common * sum_line)/(pos_num * other_num)
            pmi = math.log(2, res)
            getpospmi[i][everyword] = pmi
            
    for i in range(len(neglist)):
        negword = neglist[i]
        for everyword in range(1, sum_term):
            if everyword == negword:
                continue
            tempset_nw = set(show_info[negword])
            tempset_ew = set(show_info[everyword])
            inter = list(tempset_nw.intersection(tempset_ew))
            common = len(inter) + 1  
            neg_num = len(list(show_info[negword]))
            other_num = len(list(show_info[everyword]))
            if neg_num == 0 or other_num == 0:              
                continue
            res = (common*sum_line)/(neg_num*other_num)
            pmi = math.log(res)
            getnegpmi[i][everyword] = pmi
    return getpospmi, getnegpmi, poslist, neglist
    
def get_so(pospmi, negpmi, poslist, neglist, term_dict, word_tag, id_dict):
    """
    get sentiment orientation value of each word
    """
    so_value = [0.0] * (len(term_dict)+1)  #初始化情感得分
    for word in term_dict:  #遍历每个单词,如果是种子词，则跳过
        if term_dict[word]  in poslist or term_dict[word]  in neglist:
            continue
        term_id = term_dict[word]  
        tag = word_tag[word]
        if tag.startswith('a'):
            p_value = 1
        elif tag.startswith('v'):
            p_value = 0
        elif tag.startswith('n'):
            p_value = 0
        else:
            p_value = 0
        sump = 0
        sumn = 0
        for pos in range(len(poslist)):   
            #sump += pospmi[poslist.index(pos)][term_id]   
            sump += pospmi[pos][term_id]
        for neg in range(len(neglist)):
            sumn += negpmi[neg][term_id]
            #sumn += negpmi[neglist.index(neg)][term_id]         
        so_value[term_id] = p_value * (sump-1.2*sumn)
        #so_value[term_id] = (sump-sumn)
        #print so_value[term_id]
    #print 'so',so_value   
    return so_value
def generate_senti(so_value, index_dict):
    """
    get words' sentiment according to sentiment orientation value
    """
    posdict = {}
    negdict = {}
    for i in range(1,len(so_value)):
        word = index_dict[i]
        score = so_value[i]
        if  score > 0:   #得分大于0，则为积极的
            posdict.update({word:score})
        elif score < 0:  #得分小于0，则为消极的
            score = 0 - score
            negdict.update({word:score})
        else:   #否则为中性或者为种子词，不考虑
            continue
            
    poslist = sorted(posdict.iteritems(), key=lambda posdict:posdict[1], 
                     reverse=True)
    neglist = sorted(negdict.iteritems(), key=lambda negdict:negdict[1],
                     reverse=True) 
    fr = open('sovalue.txt','w')
    for item in poslist:
        fr.write(item[0]+'\t'+str(item[1])+'\n')
    for item in neglist:
        fr.write(item[0]+'\t'+str(item[1])+'\n')
        
        
    fpos = open('respos.txt','w')
    fneg = open('resneg.txt','w')
    for item in poslist:
        fpos.write(item[0]+'\t'+str(item[1])+'\n')
    for item in neglist:
        fneg.write(item[0]+'\t'+str(item[1])+'\n')
  
def tsplit(string, delimiters):
    """Behaves str.split but supports multiple delimiters."""
    delimiters = tuple(delimiters)
    stack = [string,]
    for delimiter in delimiters:
        for i, substring in enumerate(stack):
            substack = substring.split(delimiter)
            stack.pop(i)
            for j, _substring in enumerate(substack):
                stack.insert(i+j, _substring)
    return stack      
        
if __name__ == '__main__':
    POS_DIC, NEG_DIC = seedwords()
    ftest = open('test.txt', 'w')
    doc_list = read_text('all.txt')
    term_set, word_tag = constr_wordbag(doc_list, POS_DIC, NEG_DIC)  #word_tag是字典
    term_dict = dict(zip(term_set, range(1, len(term_set)+1))) 
    id_dict = {}
    for k,v in term_dict.iteritems():
        id_dict.update({v:k})
    #print len(term_set),len(term_dict)
    
    sent_list = []
    f_sent = open('subsent.txt','w')
    for doc in doc_list:
        #temp = tsplit(doc.strip(),('。/w','！/w', '；/w', '？/w','!/w','./w', '?/w'))
        temp = tsplit(doc.strip(),('。/PU','！/PU', '；/PU', '？/PU','!/PU','./PU', '?/PU'))
        if len(temp) == 0:
            continue
        for i in temp:
            if len(i.strip()) != 0:
                sent_list.append(i)   #切分子句
                f_sent.write(i + '\n')
    f_sent.close()
    
    px,pxy = build_samp_xy(sent_list, term_dict)
    getpmi_xy(px, pxy, term_dict,len(sent_list))
    
    print 'end'

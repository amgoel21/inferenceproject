import pandas as pd
import numpy as np
import random

alphabet = pd.read_csv('data/alphabet.csv',header=None)
alphabet = (alphabet.values)[0]
letters=[]
for i in range(len(alphabet)):
    letters.append(str(alphabet[i]))
ALPHASIZE = len(letters)
tonum={}
for i in range(len(letters)):
    tonum[letters[i]]=i
probs = pd.read_csv("data/letter_probabilities.csv",header=None)
probs = list(probs.loc[0].values)
probs=np.log2(probs)
trans = pd.read_csv("data/letter_transition_matrix.csv",header=None)
trans=trans.to_numpy()
trans[trans==0] = 1e-9
trans=np.log2(trans)

def decode1(ciphertext: str, has_breakpoint: bool,f0 =tuple(i for i in range(ALPHASIZE)),iters=5000 ) -> str:
    ITERS = iters
    acceptcount=0
    numbers = to_number(ciphertext)
    current = f0
    n = len(ciphertext)
    results={}
    results[current]=1
    funclist=list(current)
    templist=list(current)
    i=0
    while(i<ITERS and acceptcount<2000):
        # if(i%100 == 0):
        #     print(i)
        i=i+1
        c1 = random.randint(0,ALPHASIZE-1)
        c2 = random.randint(0,ALPHASIZE-2)
        if(c1==c2):
            c2 = ALPHASIZE-1
        #funclist = list(current)
        templist[c2]=funclist[c1]
        templist[c1]=funclist[c2]
        #current0=tuple(funclist)
        r=0
        for j in range(n):
            if(j==0):
                r=r+probs[templist[numbers[0]]] - probs[current[numbers[0]]]
            else:
                denom = trans[current[numbers[j]],current[numbers[j-1]]]
                numer =  trans[templist[numbers[j]],templist[numbers[j-1]]]
                r=r+numer-denom           
        a=min(1,2**r)
        acceptcount+=1
        if(random.random()<a):
            acceptcount=0
            funclist[c1]=templist[c1]
            funclist[c2]=templist[c2]
            current = tuple(templist)
        else:
            templist[c1]=funclist[c1]
            templist[c2]=funclist[c2]
        
        if(current in results):
            results[current]+=1
        else:
            results[current]=1
    maxf = max(results,key = lambda x:results[x])
    ll=0
    for j in range(n):
            if(j==0):
                ll+=probs[maxf[numbers[0]]]
            else:  
                ll+=trans[maxf[numbers[j]],maxf[numbers[j-1]]]
    decodednumbers=[]
    for i in range(len(numbers)):
        decodednumbers.append(maxf[numbers[i]])
    plaintext=""
    for j in range(len(decodednumbers)):
        plaintext+=letters[decodednumbers[j]]
    return plaintext,-1*ll/len(ciphertext),maxf

def decode(ciphertext: str, has_breakpoint: bool) -> str:
    if(has_breakpoint == False):
        text,ll,cipher = decode1(ciphertext,False,iters=10000)
        print(text)
        return text
    currentbreakpoint = len(ciphertext)//2
    minbound=0
    maxbound=len(ciphertext)
    badentropy=True
    f01=tuple(i for i in range(ALPHASIZE))
    f02=tuple(i for i in range(ALPHASIZE))

    while(badentropy):
        #print(currentbreakpoint)
        p1,e1,c1=decode1(ciphertext[:currentbreakpoint],has_breakpoint=False,f0=f01)
        #print("E1: "+str(e1))
        p2,e2,c2 = decode1(ciphertext[currentbreakpoint:],has_breakpoint=False,f0=f02)
        #print("E2: "+str(e2))
        f01=c1
        f02=c2
        if(e1>3.6 and e1>e2):
            if(currentbreakpoint<maxbound):
                maxbound=currentbreakpoint
            currentbreakpoint = (currentbreakpoint+minbound)//2
        elif(e2>3.6 and e2>e1):
            if(currentbreakpoint>minbound):
                minbound=currentbreakpoint
            currentbreakpoint = (currentbreakpoint+maxbound)//2
        else:
            badentropy=True
            break
    print(p1+p2)
    return p1+p2



    

def to_number(s):
    ans=[]
    for i in range(len(s)):
        ans.append(tonum[s[i]])
    return ans

# with open('../data/sample/ciphertext_breakpoint.txt','r') as f:
#     ciphertext=f.read()
# print(ciphertext)
# print('test')
# print(decode(ciphertext,True))






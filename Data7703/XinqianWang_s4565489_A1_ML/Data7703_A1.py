import sys
import math
import heapq
import pandas as pd
import numpy as np
'''
Return a dictionary with the items in y and the number each value appears.
'''
def Count_Dictionary(y):
    y_dict = {}
    for ys in y:
        if ys in y_dict:
            y_dict[ys]=y_dict[ys]+1
        else:
            y_dict[ys] = 1
    return y_dict

#calculateP(X|Y)
def Prob(X,Y,x,y): 
    
    if len(X) != len(Y):
        print('wrong')
    else:
        count = 0
        x_list = []
        for i in range(len(X)):
            if X[i]==x:
                x_list.append(i)
        for j in x_list:
            if Y[j]==y:
                count = count+1
        y_dict = Count_Dictionary(Y)
        x_dict = Count_Dictionary(X)
        k=count/len(x_list)
        if k == 0:
            return 1
        return (k)*(x_dict[x]/len(X))*(len(Y)/y_dict[y])

'''
Calculate the Entropy
'''
def Calculate_Entropy(x,y=[]):  # X: detremistic attribute, Y: other attributes
    lenx = len(x)
    x_dict = Count_Dictionary(x)
    if len(y)<=0:
        return -1*sum((x_x/lenx)*math.log((x_x/lenx),2) for x_x in x_dict.values())
    else:
        leny = len(y)
        y_dict = Count_Dictionary(y)
        return sum((y_dict[yy]/leny)*sum(-1*Prob(x,y,xx,yy)*math.log(Prob(x,y,xx,yy),2) for xx in x_dict) for yy in y_dict)


'''
Calculating the IG and return the largest IG with the row number
import: numpy.ndarray
output: dictionary = [attributes of the row picked] : [ndarray which have been splited]
'''
def Decision_Making(data):
    Entropy_Y = Calculate_Entropy(data.T[-1])
    Entropy_Calculate_List = data.T[:-1]
    Information_Gain_List = [Entropy_Y-Calculate_Entropy(data.T[-1],i) for i in Entropy_Calculate_List]
    Row_picked=Information_Gain_List.index(max(Information_Gain_List))
    Row_list=list(set(data.T[Row_picked]))
    Row_Collection= [
        [j for j in range(len(data.T[Row_picked])) if data.T[Row_picked][j]==i]
        for i in Row_list]
    
    data = np.delete(data, Row_picked, 1)
    dict_test = {}
    for i,rc in enumerate(Row_Collection):
        dict_test[Row_list[i]] = data[rc]
    return dict_test,Row_picked

# Ending Algorithm, with two ways, only one attribute lefts and coming to the max deepth
def If_Decision_End(data,maxDeepth):
    if len(list(set(data[:,-1])))==1:
        return True
    if len(data.T)<maxDeepth:
        return True
    return False

#Output data with a perfact form
def OutPut_Makeing(data):
    end = list(data[:,-1])
    maxlabel = max(end,key=end.count)
    return maxlabel

#DO some transforms to the data
def Node_Generation(data,maxDeepth):
    _V = {}
    def Node_Dictionary_Generation(data,L):
        if If_Decision_End(data,maxDeepth):
            return OutPut_Makeing(data)
        A,rowN = Decision_Making(data)

        for a in A:
            _V[tuple(L + [a]+[rowN])] = Node_Dictionary_Generation(A[a],L + [a]+[rowN])
            
        return _V

    def Node_Dictionary_Revise(_V,A={}):
        for x in _V:
            if type(_V[x])==str:
                A[x] = _V[x]
        return A
    
    _V = Node_Dictionary_Generation(data,[])
    A = Node_Dictionary_Revise(_V)
    A1 = {}
    A2=[]
    for a in A:
        YNvalue=A[a]
        k1=[]
        k2=[]
        for i in range(len(a)):
            if i%2==0:
                k1.append(a[i])
            if i%2==1:
                k2.append(a[i])
        A1[tuple(k1)] = YNvalue
        if k2 not in A2:
            A2.append(k2)
    return A,A1,A2

#After we do an iternation we delete the column and save the no of its column at the same time
def Prediction_Process(C,k,i=0,feature=[]):
    if i == len(k):
        return tuple(feature)
    else:
        n=k[i]
        f=C[n]
        CC = C
        del CC[n]
        return Prediction_Process(CC,k,i+1,feature+[f])


#Suppose the Trainning data and test data with the totally same format
def Data7703_Assignment1(dataTrain,maxDeepth,dataTest):
    maxDeepth = dataTrain.shape[1] - maxDeepth + 1
    if maxDeepth < 2:
        print('Error Information:')
        print("you input the wrong deepth, it must be less than the length of features")
    else:
        #Generating the Model with the data Training
        A,A1,A2 = Node_Generation(dataTrain,maxDeepth)
        print(A1)
        #separate the testa Data
        Test_Answer = dataTest[:,-1] #Test Answer is the answer of the real data
        #Test_Answer = Test_Answer.tolist()
        Test_Result = []  #Tese Result is the prediction
        dataTest = dataTest.tolist()
        '''
        Test_Result = [A1.get(Prediction_Process(C,k,i=0,feature=[]), None)
                       for t in dataTest for k in A2 
                       if A1.get(Prediction_Process(C,k,i=0,feature=[]), None)!=None]
        '''
        for t in dataTest:
            for k in A2:
                C = t.copy()
                key = Prediction_Process(C,k,i=0,feature=[])
                P = A1.get(key, None)
                if P != None:
                    Test_Result.append(P)
        
        Test_Result = np.array(Test_Result)
        return Test_Answer,Test_Result

def main(argv):
   TrainFileName,maxDeepth,TestFileName = argv

   maxDeepth = int(maxDeepth)
   
   data_train = pd.read_csv(TrainFileName, sep='\s+', header = 0)
   data_train=data_train.values

   data_test = pd.read_csv(TestFileName, sep='\s+', header = 0)
   data_test=data_test.values
   
   Test_Answer,Test_Result = Data7703_Assignment1(data_train,maxDeepth,data_test)
   nAccurate = np.sum(Test_Answer == Test_Result)
   l = len(Test_Result)
   print('accuracy is',nAccurate/l)
   return nAccurate/l

if __name__ == "__main__":
   main(sys.argv[1:])

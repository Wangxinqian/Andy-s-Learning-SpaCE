import sys
import numpy as np
from numpy import linalg as LA
import heapq
import time

# Combine all these as a function
def PCA(trainFile,trainFileLabels,testFile,testFileLabels,K):
    start = time.time()
    
    faces_train = np.loadtxt(trainFile)
    faces_train_labels = np.loadtxt(trainFileLabels)
    faces_test = np.loadtxt(testFile)
    faces_test_labels = np.loadtxt(testFileLabels)

    
    Accuracy=0
    
    #TRAIN
    Mean_matrix = np.mean(faces_train,axis = 0)
    Z_Matrix= faces_train - Mean_matrix
    S2_Matrix =np.dot(Z_Matrix.T,Z_Matrix)
    w, v = LA.eig(S2_Matrix.T)
    v = v.T
    v = np.around(v, decimals=4)
    w = np.around(w, decimals=2)
    #v = v.astype(np.float)
    #w = w.astype(np.float)
    max_index = heapq.nlargest(len(w), range(len(w)), w.take)
    
    #Test
    Z_Matrix_test= faces_test - Mean_matrix
    
    for k in range(K,K+1):
        x = np.vstack((v[l] for l in range(len(max_index)) if l<k))
        Ei_Face =np.dot(x,Z_Matrix.T).T
        #print(Ei_Face.shape)#(1, 280)
        Ei_Face_test =np.dot(x,Z_Matrix_test.T).T
        #print(Ei_Face_test.shape)#(1, 120)
        count = 0
        for j in range(len(faces_test)):
            DistanceList = []
            for i in range(len(faces_train)):
                dist = np.linalg.norm(Ei_Face_test[j] - Ei_Face[i])
                DistanceList.append(dist)
            predict = DistanceList.index(min(DistanceList))
            if faces_train_labels[predict]==faces_test_labels[j]:
                count = count+1
        Accuracy=count/len(faces_test)
    end = time.time()
    print('Programm spend time:',end-start,'seconds')
    return Accuracy

def main(argv):
   trainFile,trainFileLabels,K,testFile,testFileLabels = argv
   Accuracy = PCA(trainFile,trainFileLabels,testFile,testFileLabels,int(K))
   print('accuracy is',Accuracy)
   return Accuracy

if __name__ == "__main__":
   main(sys.argv[1:])

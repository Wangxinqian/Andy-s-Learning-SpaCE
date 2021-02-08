#!/usr/bin/env python
# coding: utf-8

# In[6]:


class BinaryHeap():
    def __init__(self):
        self.heapList = [0]
        self.currentSize = 0
    def percUp(self, i):
        while i // 2 > 0: 
            # 如果父节点大于子节点,两者互换
            if self.heapList[i] < self.heapList[i // 2]:
                tmp = self.heapList[i // 2]
                self.heapList[i // 2] = self.heapList[i]
                self.heapList[i] = tmp
            i = i//2
    def insert(self, k):
        self.heapList.append(k)
        self.currentSize = self.currentSize + 1 
        self.percUp(self.currentSize)
    def percDown(self, i): 
        while (i * 2) <= self.currentSize:
            mc = self.minChild(i) 
            if self.heapList[i] > self.heapList[mc]:
                tmp = self.heapList[i] 
                self.heapList[i] = self.heapList[mc]
                self.heapList[mc] = tmp 
            i = mc
    #返回子节点中的最小值， 所代表的index
    def minChild(self, i):
        if i * 2 + 1 > self.currentSize:
            return i * 2
        else:
            if self.heapList[i*2] < self.heapList[i*2+1]:
                return i * 2
            else: 
                return i * 2 + 1 
    def buildHeap(self, alist):
        i = len(alist) // 2
        self.currentSize = len(alist) 
        self.heapList = [0] + alist[:]
        while (i > 0):
            self.percDown(i) 
            i = i - 1


# In[17]:


class BinarySearchTree:
    def __init__(self):
        self.root = None
        self.size = 0
    def length(self):
        return self.size
    def __len__(self):
        return self.size
    def __iter__(self):
        return self.root.__iter__()
    
    def __setitem__(self, k, v):
        self.put(k, v) 
    def put(self, key, val): 
        if self.root:
            self._put(key, val, self.root)
        else:
            self.root = TreeNode(key, val) 
        self.size = self.size + 1 
    def _put(self, key, val, currentNode):
        if key < currentNode.key:
            if currentNode.hasLeftChild():
                self._put(key, val, currentNode.leftChild)
            else: 
                currentNode.leftChild = TreeNode(key, val, parent=currentNode)
        else:
            if currentNode.hasRightChild():
                self._put(key, val, currentNode.rightChild) 
            else: 
                currentNode.rightChild = TreeNode(key, val,parent=currentNode)
                
    def __getitem__(self, key):
        return self.get(key) 
    def get(self, key):
        if self.root:
            res = self._get(key, self.root)
            if res: 
                return res.payload
            else:
                return None
        else:
            return None
    def __contains__(self, key):
        if self._get(key, self.root):
            return True
        else:
            return False
    def _get(self, key, currentNode):
        if not currentNode: 
            return None 
        elif currentNode.key == key:
            return currentNode
        elif key < currentNode.key:
            return self._get(key, currentNode.leftChild) 
        else:
            return self._get(key, currentNode.rightChild)
    def delete(self, key):
        if self.size > 1:
            nodeToRemove = self._get(key, self.root)
            if nodeToRemove:
                self.remove(nodeToRemove)
                self.size = self.size - 1 
            else:
                raise KeyError('Error, key not in tree')
        elif self.size == 1 and self.root.key == key:
            self.root = None
            self.size = self.size - 1
        else:
            raise KeyError('Error, key not in tree')
    def __delitem__(self, key):
        self.delete(key) 
    def remove(self, currentNode): 
        pass


# In[14]:


class TreeNode:
    def __init__(self, key, val, left=None, right=None,parent=None):
        self.key = key 
        self.payload = val
        self.leftChild = left 
        self.rightChild = right
        self.parent = parent
    def hasLeftChild(self):
        return self.leftChild
    def hasRightChild(self):
        return self.rightChild
    def isLeftChild(self):
        return self.parent and self.parent.leftChild == self
    def isRightChild(self):
        return self.parent and self.parent.rightChild == self
    def isRoot(self):
        return not self.parent
    def isLeaf(self):
        return not (self.rightChild or self.leftChild)
    def hasAnyChildren(self): 
        return self.rightChild or self.leftChild
    def hasBothChildren(self): 
        return self.rightChild and self.leftChild
    def replaceNodeData(self, key, value, lc, rc):
        self.key = key 
        self.payload = value
        self.leftChild = lc
        self.rightChild = rc
        if self.hasLeftChild():
            self.leftChild.parent = self
        if self.hasRightChild(): 
            self.rightChild.parent = self
    def findSuccessor(self):
        succ = None 
        if self.hasRightChild():
            succ = self.rightChild.findMin()
        else:
            if self.parent:
                if self.isLeftChild():
                    succ = self.parent
                else: 
                    self.parent.rightChild = None
                    succ = self.parent.findSuccessor()
                    self.parent.rightChild = self
        return succ
    def findMin(self):
        current = self
        while current.hasLeftChild():
            current = current.leftChild
        return current 
    def spliceOut(self):
        if self.isLeaf():
            if self.isLeftChild(): 
                self.parent.leftChild = None
            else: 
                self.parent.rightChild = None 
        elif self.hasAnyChildren():
            if self.hasLeftChild():
                if self.hasLeftChild():
                    if self.isLeftChild(): 
                        self.parent.leftChild = self.leftChild 
                    else: 
                        self.parent.rightChild = self.leftChild
                    self.leftChild.parent = self.parent 
                else:
                    if self.isLeftChild(): 
                        self.parent.leftChild = self.rightChild
                    else: 
                        self.parent.rightChild = self.rightChild
                    self.rightChild.parent = self.parent
    


# In[ ]:





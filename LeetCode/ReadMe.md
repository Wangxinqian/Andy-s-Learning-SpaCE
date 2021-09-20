# AndyWang-s-Learning
[Coding Interviews 2nd edition](https://leetcode-cn.com/problem-list/xb9nqhhg/)
### No.64
```python3
class Solution:
    def __init__(self):
        self.res = 0
    def sumNums(self, n: int) -> int:
        n > 1 and self.sumNums(n - 1)
        self.res += n
        return self.res
```
if A and B: if A==Flase, then B would not do further process.

if A or B: if A==True, then B would not be processed.
*****
### No.03
Using HashSet 
```python3
class Solution:
    def findRepeatNumber(self, nums: List[int]) -> int:
        HashSet = set()
        for n in nums:
            if n in HashSet:
                return n
            else:
                HashSet.add(n)
```
Switch the code, put value i on the i's position
```python3
class Solution:
    def findRepeatNumber(self, nums: List[int]) -> int:
        i = 0
        while i < len(nums):
            if nums[i] == i:
                i+=1
                continue
            if nums[nums[i]] == nums[i]:
                return nums[i]
            nums[nums[i]], nums[i] = nums[i], nums[nums[i]]
        return -1
```
*****
### No.09
Using two stack to represent a Queue.

+ Stack-> first in last out
+ Queue-> first in first out
```python3
class CQueue:

    def __init__(self):
        self.A, self.B = [], []

    def appendTail(self, value: int) -> None:
        self.A.append(value)

    def deleteHead(self) -> int:
        if len(self.B) != 0:
            return self.B.pop()
        elif len(self.A)== 0:
            return -1
        else:
            for i in range(len(self.A)):
                self.B.append(self.A.pop())
            return self.B.pop()
```
*****
### No.10
Recrusive Method-> duplicates and with a complexity of O(N)
Internation Calculation
```python3
class Solution:
    def fib(self, n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a % 1000000007
```
*****
### No.58
```python3
class Solution:
    def reverseLeftWords(self, s: str, n: int) -> str:
        return s[n:] + s[:n]
```
*****
### No.04
Change the question into a search problem.
```python3
class Solution:
    def findNumberIn2DArray(self, matrix: List[List[int]], target: int) -> bool:
        i, j = len(matrix) - 1, 0
        while i >= 0 and j < len(matrix[0]):
            if matrix[i][j] > target: i -= 1
            elif matrix[i][j] < target: j += 1
            else: return True
        return False
```
*****
### No.10
f[i=1] = 1
f[i=0] = 1, since f[i=2] = f[i=1] + f[i=0] = 1 + 1
f[i=n] = f[i=n-1] + f[i=n-2]
```python3
class Solution:
    def findNumberIn2DArray(self, matrix: List[List[int]], target: int) -> bool:
        i, j = len(matrix) - 1, 0
        while i >= 0 and j < len(matrix[0]):
            if matrix[i][j] > target: i -= 1
            elif matrix[i][j] < target: j += 1
            else: return True
        return False
```
*****

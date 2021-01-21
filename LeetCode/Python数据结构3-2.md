# 3.3.4 匹配括号

接下来，我们使用栈解决实际的计算机科学问题。我们都写过如下所示的算术表达式。\
(5 + 6) * (7 + 8) / (4 + 3)\
其中的括号用来改变计算顺序。像 Lisp 这样的编程语言有如下语法结构。\
(defun square(n)(* n n))\
它定义了一个名为 square 的函数，该函数会返回参数 n 的平方值。Lisp 所用括号之多，令
人咋舌。\
在以上两个例子中，括号都前后匹配。匹配括号是指每一个左括号都有与之对应的一个右括
号，并且括号对有正确的嵌套关系。下面是正确匹配的括号串。\
(()()()())\
(((())))\
(()((())()))\
下面的这些括号则是不匹配的。\
((((((())\
()))\
(()()(()\
能够分辨括号匹配得正确与否，对于识别编程语言的结构来说非常重要。\
我们的挑战就是编写一个算法，它从左到右读取一个括号串，然后判断其中的括号是否匹配。\
为了解决这个问题，需要注意到一个重要现象。当从左到右处理括号时，最右边的无匹配左括号
必须与接下来遇到的第一个右括号相匹配，如图 3-4 所示。并且，在第一个位置的左括号可能要
等到处理至最后一个位置的右括号时才能完成匹配。\相匹配的右括号与左括号出现的顺序相反。
这一规律暗示着能够运用栈来解决括号匹配问题。

``` python
1 from pythonds.basic import Stack
2
3 def parChecker(symbolString):
4 s = Stack()
5 balanced = True
6 index = 0
7 while index < len(symbolString) and balanced:
8 symbol = symbolString[index]
9 if symbol == "(":
10 s.push(symbol)
11 else:
12 if s.isEmpty():
13 balanced = False
14 else:
15 s.pop()
16
17 index = index + 1
18
19 if balanced and s.isEmpty():
20 return True
21 else:
22 return False 

```

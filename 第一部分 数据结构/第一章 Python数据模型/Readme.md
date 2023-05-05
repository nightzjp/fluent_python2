## Python数据模型

---

Python的质量保障得益于一致性。使用Python一段时间之后，便可以根据自己掌握的知识，正确的猜出新功能的作用。

然而，如果你在接触Python之前有其他面向对象语言的经验，就会觉得奇怪：为什么获取容器大小不使用collection.len()，而是使用len(collection)？这一点表面上看确实奇怪，而且只是众多行为的冰山一角，不过知道背后的原因之后，你会发现这才是真正的符合 "Python风格" 。一切的一切都埋藏在Python数据模型中。我们平常自己创建
对象就要使用这个API，确保使用最地道的语言功能。

可以把Python视为一个框架，而数据模型就是对框架的描述，规范语言自身各个组成部分的接口，确立序列、函数、迭代器、协程、类、上下文管理器部分的行为。

使用框架要花大量的时间编写方法，交给框架调用。利用Python数据模型构建新类也是如此。Python解释器调用特殊方法来执行基本对象操作，通常由特殊句法触发。特殊方法的名称前后两端都有双下划线。例如在obj[key]句背后提供支持的特殊方法__getitem__。为了求解my_collection[key]，Python解释器要调用my_collection.__getitem__(key)。

如果想让对象支持以下基本的语言结构并与其交互，就需要实现特殊方法：

+ 容器
+ 属性存取
+ 迭代(包括使用async for的异步迭代)
+ 运算符重载
+ 函数和方法调用
+ 已复查表示形式和格式化
+ 使用await的异步编程
+ 对象创建和析构
+ 使用with或async with 语句管理上下文

#### 魔术方法和双下划线

特殊方法用行话来说叫做 *魔术方法* ，特殊方法也叫 "双下划线方法"。

---

> 字符串格式化方式推荐使用Python3.6引入的f字符串格式方法。如果内容占据多行，可以采用str.format()方法

##### 1.2 一摞Python风格的纸牌

示例1-1虽然简单，却展示了实现__getitem__和__len__两个特殊方法之后得到的强大功能。

> 示例1-1 一摞有序的纸牌

```python
import collections


Card = collections.namedtuple("Card", ["rank", "suit"])


class FrenchDesk:
    ranks = [str(n) for n in range(2, 11)] + list("JQKA")
    suits = "spades diamonds clubs hearts".split()
    
    def __init__(self):
        self._card = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        
    def __len__(self):
        return len(self._card)
    
    def __getitem__(self, item):
        return self._card[item]
```

首先用collections.namedtuple构建了一个简单的类，表示单张纸牌。使用namedtuple构建只有属性而没有自定义方法的类对象，例如数据库中的一条记录。这个示例中使用这个类表示一摞纸牌中的各张纸牌，如下所示

```python
beer_card = Card("7", "diamonds")
print(beer_card)  # Card(rank='7', suit='diamonds')
```

但是，这个示例的重点是简短精炼的FrenchDeck类。首先，与标准的Python容器一样，一摞牌响应len()函数，返回一摞牌中有多少张。

```python
deck = FrenchDesk()
print(len(deck))  # 52
```

得益于__getitem__方法，我们可以轻松地从这摞牌中抽取某一张，比如第一张或者是最后一张。

```python
print(deck[0])  # Card(rank='2', suit='spades')
print(deck[-1])  # Card(rank='A', suit='hearts')
```

如果想随机选一张牌，需要定义一个新方法吗？不需要，因为Python已经提供了从序列中随机获取一项的函数。即random.choice。我们可以再一摞牌上使用这个函数。

```python
from random import choice
print(choice(deck))  # Card(rank='J', suit='hearts')
print(choice(deck))  # Card(rank='4', suit='clubs')
print(choice(deck))  # Card(rank='Q', suit='clubs')
```

可以看到，通过特殊方法和利用Python数据模型，这样做有两个优点。

+ 类的用户不需要记住标准操作的方法名称
+ 可以充分利用Python标准库，无须重新造轮子。

由于__getitem__方法把操作委托给self_card的[]运算法，一摞牌自动支持切片(slice)。下面展示了如何从一摞牌中抽取最上面的三张，再从索引12位开始，跳过13张牌，只取4张A

```python
print(deck[:3])  # [Card(rank='2', suit='spades'), Card(rank='3', suit='spades'), Card(rank='4', suit='spades')]
print(deck[12::13])  # [Card(rank='A', suit='spades'), Card(rank='A', suit='diamonds'), Card(rank='A', suit='clubs'), Card(rank='A', suit='hearts')]
```

实现特殊方法__getitem__z会后，这摞纸牌还可以迭代。

```python
# 正向迭代
for card in deck:
    print(card)
# 反向迭代
for card in reversed(deck):
    print(card)
```

迭代往往是隐式的。如果一个容器没有实现__contains__方法，那么in运算符就会做一次顺序扫描。本示例就是这样，FrenchDeck类支持in运算法，因为该类克迭代。

```python
print(Card("7", "hearts") in deck)  # True 
print(Card("11", "hearts") in deck)  # False 
```

那么排序呢?按照常规，牌面大小应该按照点数(A最大)，以及黑桃(最大)、红心、方块、梅花(最小)的顺序排列。下面我们按照这个规则定义排序函数，梅花2返回0，黑桃A返回51。

```python
suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)


def spades_high(card):
    rank_value = FrenchDesk.ranks.index(card.rank)
    return rank_value * len(suit_values) + suit_values[card.suit]


for card in sorted(deck, key=spades_high):
    print(card)
```

虽然FrenchDeck类隐式集成object类，但是欠着的多数功能不是继承来的，而是源自数据模型和组合模式。通过前面使用random.choice、reversed和sorted的示例可以看出，实现__len__和__getitem__两个特殊方法之后，FrenchDeck的行为就像标准的Python序列一样，受益于语言核心特性和标准库。__len__和__getitem__得实现
利用组合模式，把所有工作委托给一个list对象，即self_cards。

> 按照目前的设计，FrenchDesk对象是不支持洗牌操作的，因为他是不可变的


##### 1.3 特殊方法是如何使用的

首先要明确一点，特殊方法供Python解释器调用，而不是程序员自己调用。也就是说。没有*my_object.__len__()*这种写法，正确的写法应该是*len(my_object)*。如果my_object是用户定义的类的实例，Python将调用你实现的*__len__*方法。

然而，处理内置类型是，例如list、str、bytearray、或Numpy数据等扩展，Python解释器会抄个近路。Python中可变长度容器的底层C语言实现中有一个结构体，名为*PyVarObject*。在这个结构体中，ob_size字段保存着容器中的项数。如果my_object是某个内置类型的实例，则len(my_object)直接读取ob_size字段的值，这要比调用方法快得多。

很多时候，特殊方法是隐式调用的。例如，for i in x: 语句其实在背后调用iter(x)，接着又用x__iter__()或x__getitem__()。在frenchDeck示例中，调用的是后者。

我们在编写代码时一般不直接调用这些特殊方法，除非设计大量元编程。即便如此，大部分时间也是实现特殊方法，很少显示调用。唯一例外的是*__init__*方法，为自定义类实现__init__方法时经常直接调用它调取超类的初始化方法

如果需要调用特殊方法，则最好调用相应的内置函数，例如len、iter、str等。这些内置函数不仅调用对应的特殊方法，通常还会提供额外服务，而且对于内置类型来说，速度比调用方法更快。


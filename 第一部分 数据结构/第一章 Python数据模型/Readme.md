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


> 暂时不加任何图示

二维向量加法表示: Vector(2, 4) + Vector(2, 1) = Vector(4, 5)

为了给这个类设计API，先写出模拟的控制台会话，作为doctest。以下代码测试向量加法

```python
from math import hypot

class Vector:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Vector(%r,%r)" % (self.x,self.y)

    def __abs__(self):
        return hypot(self.x,self.y)

    def __bool__(self):
        return bool(abs(self))

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Vector(x,y)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)


v1 = Vector(2, 4)
v2 = Vector(2, 1)
print(v1 + v2)  # Vector(4,5)
```

! 注意：+运算符的结果是一个新的Vector对象，在控制台中以友好的格式显示

使用内置函数abs返回整数和浮点数的绝对值，以及复数的模。为了保持一致性，我们的API也使用abs函数计算向量的模

```python
v = Vector(3, 4)
print(abs(v))  # 5.0
```

还可以实现*运算符，计算向量的标量积(一个向量乘以一个数，得到一个方向相同、模为一定倍数的新向量)

```python
print(v * 3)  # Vector(9,12)

print(abs(v * 3))  # 15.0
```

> 示例1-2 一个简单的二维向量类

使用__repr__、__abs__、__add__和__mul__等特殊方法为Vector类实现这几种运算

##### 加法::

```python
v1 = Vector(3, 4)
v2 = Vector(2, 1)
print(v1 + v2)  # Vector(5,5)
```

##### 绝对值:: 

```python
v = Vector(3, 4)
print(abs(v))  # 5.0
```

##### 标量积::

```python
print(v * 3)  # Vector(9,12)
print(abs(v * 3))  # 15.0
```

以上Vector类除了我们熟悉的__init__方法，还实现了另外5个特殊方法。

这些方法在类内部，或者在前面中的doctest中都没有直接调用。(特殊方法不需要手动调用，解释器自动调用)

以上示例实现了+和*两个运算符，展示了__add__ 和 __mul__ 方法的基本用法。这两个方法创建并返回了一个新的Vector实例，没有修改运算对象，只是读取self或other。这是中辍运算符的预期行为，即创建新对象，不修改运算对象。


特殊方法__repr__供内置函数repr调用，获取对象的字符串表示形式。如未定义__repr__方法，Vector实例将在Python控制台中不友好展示：<__main__.Vector object at 0x1082b7280>。

交互式控制台和调试器在表达式求值结果上调用repr函数，处理方式与使用%运算符处理经典格式化方式中的%r占位符，以及使用str.format方法处理新字符串格式化句法中的!r转换字段一样。

!注意：Vector类__repr__方法中的f字符串使用!r以标准的表示形式显示属性。这样做比较好，因为Vector(1, 2)和Vector("1", "2")之间是有区别的，后者在这个示例中不可用，因为构造函数接收数值而非字符串。

__repr__方法返回的字符串应当没有歧义，如果可能，最好与源码保持一致，方便重新创建所表示的对象。鉴于此，我们才以类似构造函数的形式返回对象字符串的表示形式。

与此形成对照的事，__str__方法由内置函数str()调用，在背后供print函数使用，返回对终端用户友好的字符串。

有时，__repr__方法返回的字符串足够友好，无需再定义__str__方法，因为继承自object类的视线最终会调用__repr__方法。


Python中有一个bool类型，在需要布尔值的地方处理对象，例如if或while语句的条件表达式，或者and、or和not的运算对象。为了确定x表示的值为真或为假，Python调用bool(x)，返回True或False

默认情况下，用户定义类的实例都是真值，除非实现了__bool__或__len__方法。简单来说，bool(x)调用x__bool__()，以后者返回的结果为准。如果没有实现__bool__方法，则Python会尝试调用x__len__()；如果该方法返回零值，则bool函数返回False，否则返回True

我们实现的__bool__方法没有用到什么高深的理论，如果向量的模为零，则返回False，否则返回True，我们使用bool(abs(self))把向量的模转换成布尔值，因为__bool__方法必须返回一个布尔值。在__bool__方法外部，很少需要显示的调用bool()，因为任何对象都可以在布尔值上下文中使用。

```python
Vector.__bool__也可以采用如下方式定义
def __bool__(self):
    return bool(self.x or self.y)

# 这样定义虽然不易读懂，但是不用经过abs和__abs__的处理，也无须计算平方根平方根。使用bool显示转换是有必要的，因为__bool__方法必须返回一个布尔值。
```

抽象基类Collection(Python3.6新增)统一了这三个基本接口，每一个容器类型均应实现如下事项

+ Iterable要支持for、拆包和其它迭代方法
+ Sized要支持内置函数len
+ Container要支持in运算符

Python不强制要求具体类继承这些抽象基类中的任何一个。只要实现了__len__方法就说明哪个类满足Size节课。

Collection有3个十分重要的专用接口

+ Sequence规范list和str等内置类型的接口
+ Mapping被dict、collections.defaultdict等实现
+ Set是set和frozenset两个内置类型的接口

只有Sequence实现了Reversible，因为序列要支持以任意顺序排列内容，而Mapping和Set不需要

> 自Python3.7开始，dict类型变得有顺序了，不过只是保留键的插入顺序。你不能随意重新排列dict中的键

Set抽象基类中的所有特殊方法实现的都是中辍运算符。例如，a & b计算集合a和b的交集，该运算符由__and__特殊方法实现。

《Python语言参考手册》中的第三张列出了80多个特殊方法名称，其中一半以上用于实现算术运算符、按位运算符和比较运算法

> 涉及太多自行查询双下划线函数


##### len为什么不是方法？

《Python之禅》中有一句话：实用胜过纯粹。当x是内置类型的实例时，len(x)运行速度非常的快！计算CPython内置对象的长度时不调用任何方法，而是直接读取C语言结构体中的字段。获取容器中的项数是一项常见操作，str、list、memoryview等各种基本的容器类型必须高效的完成这些工作。

换句话说，len之所以不作为方法调用，是因为它经过了特殊处理，被当做Python数据模型的一部分，就像abs函数一样。但是借助特殊方法__len__，也可让len适用于自定义对象。这是一种相对公平的折中方案，既满足了内置对象对速度的要求，又保证了语言的一致性。这也体现了《Python之禅》中的另一句话："特殊情况不是打破规则的理由"

> 忘掉面向对象语言中的方法调用，把abs和len看做一元运算符，说不定你更能接受它们表面上看似对函数的调用。Python源自ABC语言，很多特性都继承自ABC...


##### 小结

1. 借助特殊方法，自定义对象的行为可以像内置类型一样，让我们写出更具表现力的代码，符合社区所认可的Python风格。

2. Python对象基本上都需要提供一个有用的字符串表示形式，在调试、登记日志和向终端用户表示时使用。鉴于此，数据模型中才有了__repr__和__str__两个特殊方法

3. 模拟用户的行为(例如FrenchDeck示例)是特殊方法最常见的用途之一。比如说数据库代码返回的查询结果往往就是一个类似序列的容器。

4. 得益于运算符重载，Python提供了丰富的数值类型，除内置的数值类型之外，还有decimal.Decimal和fractions.Fraction，全都支持中缀算术运算符。数据科学库NumPy还提供了矩阵和张量中的中缀运算符。
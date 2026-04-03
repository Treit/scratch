#:property PublishAot=false

using D = System.Func<object, object>;

D Cast(object x) => (D)x;

var sw = System.Diagnostics.Stopwatch.StartNew();

Console.WriteLine("CURSED LAMBDA CALCULUS: A FizzBuzz nobody asked for");
Console.WriteLine(new string('=', 55));
Console.WriteLine();

D c0 = f => (D)(x => x);
D c1 = f => (D)(x => Cast(f)(x));

D SUCC = n => (D)(f => (D)(x => Cast(f)(Cast(Cast(n)(f))(x))));

D ADD = m => (D)(n => (D)(f => (D)(x => Cast(Cast(m)(f))(Cast(Cast(n)(f))(x)))));

D MUL = m => (D)(n => (D)(f => Cast(m)(Cast(n)(f))));

D POW = b => (D)(e => Cast(e)(b));

D PRED = n => (D)(f => (D)(x =>
    Cast(Cast(Cast(n)
        ((D)(g => (D)(h => Cast(h)(Cast(g)(f))))))
        ((D)(u => x)))
        ((D)(u => u))));

D SUB = m => (D)(n => Cast(Cast(n)(PRED))(m));

D TRUE  = a => (D)(b => a);
D FALSE = a => (D)(b => b);

D AND = p => (D)(q => Cast(Cast(p)(q))(p));
D OR  = p => (D)(q => Cast(Cast(p)(p))(q));
D NOT = p => Cast(Cast(p)(FALSE))(TRUE);

D ISZERO = n => Cast(Cast(n)((D)(x => FALSE)))(TRUE);

D LEQ = m => (D)(n => Cast(ISZERO)(Cast(Cast(SUB)(m))(n)));
D EQ  = m => (D)(n => Cast(Cast(AND)(Cast(Cast(LEQ)(m))(n)))(Cast(Cast(LEQ)(n))(m)));

D PAIR = x => (D)(y => (D)(f => Cast(Cast(f)(x))(y)));
D FST  = p => Cast(p)(TRUE);
D SND  = p => Cast(p)(FALSE);

D modStep(object n) => (D)(acc =>
    Cast(Cast(Cast(ISZERO)(Cast(Cast(SUB)(n))(Cast(SUCC)(acc))))(c0))(Cast(SUCC)(acc)));

D MOD = m => (D)(n => Cast(Cast(m)(modStep(n)))(c0));

var c2  = Cast(SUCC)(c1);
var c3  = Cast(SUCC)(c2);
var c4  = Cast(SUCC)(c3);
var c5  = Cast(SUCC)(c4);
var c6  = Cast(Cast(MUL)(c2))(c3);
var c8  = Cast(Cast(MUL)(c2))(c4);
var c10 = Cast(Cast(MUL)(c2))(c5);
var c15 = Cast(Cast(MUL)(c3))(c5);

int toInt(object n) => (int)Cast(Cast(n)((D)(x => (object)((int)x + 1))))(0);
bool toBool(object b) => (bool)Cast(Cast(b)((object)true))((object)false);

Console.WriteLine("-- Numbers built purely from lambda calculus --");
Console.WriteLine($"   2  = SUCC(1)     = {toInt(c2)}");
Console.WriteLine($"   3  = SUCC(2)     = {toInt(c3)}");
Console.WriteLine($"   5  = SUCC(4)     = {toInt(c5)}");
Console.WriteLine($"   6  = MUL(2)(3)   = {toInt(c6)}");
Console.WriteLine($"   10 = MUL(2)(5)   = {toInt(c10)}");
Console.WriteLine($"   15 = MUL(3)(5)   = {toInt(c15)}");

Console.WriteLine();
Console.WriteLine("-- Arithmetic --");
Console.WriteLine($"   ADD(3)(5)   = {toInt(Cast(Cast(ADD)(c3))(c5))}");
Console.WriteLine($"   MUL(3)(5)   = {toInt(Cast(Cast(MUL)(c3))(c5))}");
Console.WriteLine($"   POW(2)(5)   = {toInt(Cast(Cast(POW)(c2))(c5))}");
Console.WriteLine($"   PRED(5)     = {toInt(Cast(PRED)(c5))}");
Console.WriteLine($"   SUB(10)(3)  = {toInt(Cast(Cast(SUB)(c10))(c3))}");
Console.WriteLine($"   MOD(10)(3)  = {toInt(Cast(Cast(MOD)(c10))(c3))}");
Console.WriteLine($"   MOD(15)(5)  = {toInt(Cast(Cast(MOD)(c15))(c5))}");

Console.WriteLine();
Console.WriteLine("-- Boolean logic --");
Console.WriteLine($"   AND(T)(T) = {toBool(Cast(Cast(AND)(TRUE))(TRUE))}");
Console.WriteLine($"   AND(T)(F) = {toBool(Cast(Cast(AND)(TRUE))(FALSE))}");
Console.WriteLine($"   OR(F)(T)  = {toBool(Cast(Cast(OR)(FALSE))(TRUE))}");
Console.WriteLine($"   NOT(T)    = {toBool(Cast(NOT)(TRUE))}");
Console.WriteLine($"   ISZERO(0) = {toBool(Cast(ISZERO)(c0))},  ISZERO(3) = {toBool(Cast(ISZERO)(c3))}");
Console.WriteLine($"   LEQ(3)(5) = {toBool(Cast(Cast(LEQ)(c3))(c5))},  LEQ(5)(3) = {toBool(Cast(Cast(LEQ)(c5))(c3))}");
Console.WriteLine($"   EQ(3)(3)  = {toBool(Cast(Cast(EQ)(c3))(c3))},  EQ(3)(5)  = {toBool(Cast(Cast(EQ)(c3))(c5))}");

Console.WriteLine();
Console.WriteLine("-- Pairs --");
var myPair = Cast(Cast(PAIR)(c3))(c5);
Console.WriteLine($"   PAIR(3)(5) = ({toInt(Cast(FST)(myPair))}, {toInt(Cast(SND)(myPair))})");

Console.WriteLine();
Console.WriteLine(new string('=', 55));
Console.WriteLine("FIZZBUZZ (1..15) via pure lambda calculus");
Console.WriteLine(new string('=', 55));
Console.WriteLine();

var nums = new List<object> { c0 };
object cur = c0;
for (int i = 1; i <= 15; i++)
{
    cur = Cast(SUCC)(cur);
    nums.Add(cur);
}

for (int i = 1; i <= 15; i++)
{
    var n = nums[i];
    var divBy3 = Cast(Cast(MOD)(n))(c3);
    var divBy5 = Cast(Cast(MOD)(n))(c5);
    var d3 = Cast(ISZERO)(divBy3);
    var d5 = Cast(ISZERO)(divBy5);
    var isFizzBuzz = toBool(Cast(Cast(AND)(d3))(d5));
    var isFizz = toBool(d3);
    var isBuzz = toBool(d5);

    string result;
    if (isFizzBuzz) result = "FizzBuzz";
    else if (isFizz) result = "Fizz";
    else if (isBuzz) result = "Buzz";
    else result = toInt(n).ToString();

    Console.Write($" {result,-10}");
    if (i % 5 == 0) Console.WriteLine();
}

Console.WriteLine();
Console.WriteLine();
Console.WriteLine(new string('=', 55));
Console.WriteLine("FIBONACCI via Church-encoded Z combinator");
Console.WriteLine(new string('=', 55));
Console.WriteLine();

D Z = f =>
    ((D)(x => Cast(f)((D)(v => Cast(Cast(x)(x))(v)))))
    ((D)(x => Cast(f)((D)(v => Cast(Cast(x)(x))(v)))));

var fibCache = new Dictionary<int, object>();
var fib = Cast(Z)((D)(self => (D)(n =>
{
    int ni = toInt(n);
    if (fibCache.TryGetValue(ni, out var cached)) return cached;
    object r;
    if (toBool(Cast(ISZERO)(n))) r = c0;
    else if (toBool(Cast(ISZERO)(Cast(PRED)(n)))) r = c1;
    else r = Cast(Cast(ADD)(Cast(self)(Cast(PRED)(n))))(Cast(self)(Cast(Cast(PRED)(Cast(PRED)(n)))));
    fibCache[ni] = r;
    return r;
})));

var fibResults = new List<string>();
for (int i = 0; i <= 12; i++)
    fibResults.Add(toInt(Cast(fib)(nums[Math.Min(i, nums.Count - 1)])).ToString());
Console.WriteLine("   fib(0..12) = " + string.Join(", ", fibResults));

Console.WriteLine();
Console.WriteLine(new string('=', 55));
Console.WriteLine("INSERTION SORT on a Church-encoded linked list");
Console.WriteLine(new string('=', 55));
Console.WriteLine();

var NIL = Cast(Cast(PAIR)(FALSE))(FALSE);
D CONS = h => (D)(t => Cast(Cast(PAIR)(TRUE))(Cast(Cast(PAIR)(h))(t)));
D HEAD = l => Cast(FST)(Cast(SND)(l));
D TAIL = l => Cast(SND)(Cast(SND)(l));
D ISNIL = l => Cast(NOT)(Cast(FST)(l));

var INSERT = Cast(Z)((D)(self => (D)(n => (D)(list =>
{
    if (toBool(Cast(ISNIL)(list))) return Cast(Cast(CONS)(n))(NIL);
    if (toBool(Cast(Cast(LEQ)(n))(Cast(HEAD)(list)))) return Cast(Cast(CONS)(n))(list);
    return Cast(Cast(CONS)(Cast(HEAD)(list)))(Cast(Cast(Cast(self))(n))(Cast(TAIL)(list)));
}))));

var SORT = Cast(Z)((D)(self => (D)(list =>
{
    if (toBool(Cast(ISNIL)(list))) return NIL;
    return Cast(Cast(INSERT)(Cast(HEAD)(list)))(Cast(Cast(self))(Cast(TAIL)(list)));
})));

string listToString(object list)
{
    var items = new List<string>();
    var c = list;
    while (!toBool(Cast(ISNIL)(c)))
    {
        items.Add(toInt(Cast(HEAD)(c)).ToString());
        c = Cast(TAIL)(c);
    }
    return "[" + string.Join(", ", items) + "]";
}

var unsorted = Cast(Cast(CONS)(c5))(Cast(Cast(CONS)(c2))(Cast(Cast(CONS)(c8))(Cast(Cast(CONS)(c1))(Cast(Cast(CONS)(c6))(Cast(Cast(CONS)(c3))(NIL))))));
Console.WriteLine($"   Input:  {listToString(unsorted)}");
var sorted = Cast(SORT)(unsorted);
Console.WriteLine($"   Sorted: {listToString(sorted)}");

var MAP = Cast(Z)((D)(self => (D)(fn => (D)(list =>
{
    if (toBool(Cast(ISNIL)(list))) return NIL;
    return Cast(Cast(CONS)(Cast(fn)(Cast(HEAD)(list))))(Cast(Cast(Cast(self))(fn))(Cast(TAIL)(list)));
}))));

var FILTER = Cast(Z)((D)(self => (D)(pred => (D)(list =>
{
    if (toBool(Cast(ISNIL)(list))) return NIL;
    var hd = Cast(HEAD)(list);
    var rest = Cast(Cast(Cast(self))(pred))(Cast(TAIL)(list));
    if (toBool(Cast(pred)(hd))) return Cast(Cast(CONS)(hd))(rest);
    return rest;
}))));

var FOLD = Cast(Z)((D)(self => (D)(fn => (D)(acc => (D)(list =>
{
    if (toBool(Cast(ISNIL)(list))) return acc;
    return Cast(Cast(Cast(Cast(self))(fn))(Cast(Cast(fn)(acc))(Cast(HEAD)(list))))(Cast(TAIL)(list));
})))));

Console.WriteLine();
Console.WriteLine("-- MAP (double each element) --");
var doubled = Cast(Cast(MAP)((D)(n => Cast(Cast(MUL)(c2))(n))))(sorted);
Console.WriteLine($"   {listToString(sorted)} -> {listToString(doubled)}");

Console.WriteLine();
Console.WriteLine("-- FILTER (keep only > 3) --");
var big = Cast(Cast(FILTER)((D)(n => Cast(NOT)(Cast(Cast(LEQ)(n))(c3)))))(sorted);
Console.WriteLine($"   {listToString(sorted)} -> {listToString(big)}");

Console.WriteLine();
Console.WriteLine("-- FOLD (sum the list) --");
var sum = Cast(Cast(Cast(FOLD)(ADD))(c0))(sorted);
Console.WriteLine($"   sum({listToString(sorted)}) = {toInt(sum)}");

sw.Stop();
Console.WriteLine();
Console.WriteLine($"All computed using nothing but \\x.x and function application.");
Console.WriteLine($"Not a single integer, boolean, or data structure was harmed.");
Console.WriteLine($"Elapsed: {sw.Elapsed.TotalSeconds:F2}s");

namespace Stuff;

public interface IStuff
{
    string GetDescription();
}

public abstract class BasicStuff : IStuff
{
    public abstract string GetDescription();
}

public class FunnyStuff : BasicStuff
{
    public override string GetDescription() => "This is funny stuff that makes people laugh!";
}

public class WeirdStuff : BasicStuff
{
    public override string GetDescription() => "This is weird stuff that confuses everyone.";
}

public abstract class Base // no interface
{
    protected abstract IStuff GetStuff();

    public virtual void ImportantMethod()
    {
        var stuff = GetStuff();

        Console.WriteLine($"Doing important work with: {stuff.GetDescription()}");
    }
}

public abstract class SpecializedBase<TSpecializedStuff> : Base
    where TSpecializedStuff : BasicStuff, new()
{
    public TSpecializedStuff Stuff { get; } = new();

    protected override TSpecializedStuff GetStuff() => Stuff;
}

// Concrete implementation that specializes in funny stuff
public class FunnyProcessor : SpecializedBase<FunnyStuff>
{
    public override void ImportantMethod()
    {
        Console.WriteLine("FunnyProcessor is starting...");
        base.ImportantMethod();
        Console.WriteLine("Making everyone laugh! 😂");
    }
}

// Concrete implementation that specializes in weird stuff
public class WeirdProcessor : SpecializedBase<WeirdStuff>
{
    public override void ImportantMethod()
    {
        Console.WriteLine("WeirdProcessor is starting...");
        base.ImportantMethod();
        Console.WriteLine("Creating confusion everywhere! 🤔");
    }
}

internal static class Program
{
    private static void Main(string[] args)
    {
        Console.WriteLine("Demonstrating SpecializedBase<T> implementations:");
        Console.WriteLine("==============================================\n");

        var funnyProcessor = new FunnyProcessor();
        var weirdProcessor = new WeirdProcessor();

        Console.WriteLine("1. Using FunnyProcessor:");
        funnyProcessor.ImportantMethod();
        Console.WriteLine($"   Direct access to stuff: {funnyProcessor.Stuff.GetDescription()}\n");

        Console.WriteLine("2. Using WeirdProcessor:");
        weirdProcessor.ImportantMethod();
        Console.WriteLine($"   Direct access to stuff: {weirdProcessor.Stuff.GetDescription()}\n");

        Console.WriteLine("3. Polymorphic usage:");
        Base[] processors = { funnyProcessor, weirdProcessor };

        foreach (var processor in processors)
        {
            Console.WriteLine($"   Processing with {processor.GetType().Name}:");
            processor.ImportantMethod();
        }
    }
}
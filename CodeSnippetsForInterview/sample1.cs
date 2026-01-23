internal class SomeClass
{
    internal static bool CheckForMatch(string value)
    {
        return new HashSet<string>(StringComparer.OrdinalIgnoreCase) { "first", "second" }.Contains(value);
    }
}


public class StressTestDocument
{
    public string Id { get; set; } = string.Empty;
    public int Count { get; set; }
    public DateTime Timestamp { get; set; }
    public List<ChildItem> Children { get; set; } = new();
    public Dictionary<string, string> Metadata { get; set; } = new();

    public class ChildItem
    {
        public string Name { get; set; } = string.Empty;
        public int Value { get; set; }
        public double Score { get; set; }
    }
}

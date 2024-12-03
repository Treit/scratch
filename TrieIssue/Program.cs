using KTrie;

var words = File.ReadAllLines("words.txt");

var trie = new Trie();
foreach (var word in words)
{
    trie.Add(word);
}

var tasks = new List<Task>();

for (int i = 0; i < 1000; i++)
{
    tasks.Add(Task.Run(() =>
    {
        long count = 0;
        while (true)
        {
            var matches = trie.StartsWith("a").Take(1000);
            foreach (var match in matches)
            {
                count++;
                if (count % 10_000_000 == 0)
                {
                    Console.Write(".");
                }
            }
        }
    }));
}

Console.ReadLine();
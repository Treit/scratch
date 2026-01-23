static string RandomString(Random random, int maxLength)
{
    var len = random.Next(maxLength);
    const string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    return new string(Enumerable.Repeat(chars, len)
        .Select(s => s[random.Next(s.Length)]).ToArray());
}
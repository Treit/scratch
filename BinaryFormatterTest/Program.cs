using System.Runtime.Serialization.Formatters.Binary;

#pragma warning disable SYSLIB0011 // Type or member is obsolete
var bf = new BinaryFormatter();
#pragma warning restore SYSLIB0011 // Type or member is obsolete
var stream = new MemoryStream();
bf.Serialize(stream, new TestRecord("Hello", 123));
stream.Position = 0;
var record = (TestRecord)bf.Deserialize(stream);
Console.WriteLine(record);

[Serializable]
record TestRecord(string Name, int Value);
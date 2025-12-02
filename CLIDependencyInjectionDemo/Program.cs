using Microsoft.Extensions.DependencyInjection;

var services = new ServiceCollection();
services.AddScoped<RequestHandler>();
services.AddScoped<App>();

var serviceProvider = services.BuildServiceProvider();

// Simulate 3 requests. Each gets its own scope
for (int i = 1; i <= 3; i++)
{
    using var scope = serviceProvider.CreateScope();
    var app = scope.ServiceProvider.GetRequiredService<App>();
    app.Run($"Request-{i}");
}

// App with constructor-injected dependency
class App(RequestHandler handler)
{
    public void Run(string requestName)
    {
        Console.WriteLine($"\n=== {requestName} ===");
        handler.ProcessRequest(requestName);
    }
}

// Scoped service - new instance per scope
class RequestHandler
{
    private readonly Guid _instanceId = Guid.NewGuid();

    public void ProcessRequest(string requestName)
    {
        Console.WriteLine($"Handler instance: {_instanceId:N}");
        Console.WriteLine($"Processing: {requestName}");
    }
}

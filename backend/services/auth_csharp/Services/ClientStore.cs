using AuthService.Models;
using Microsoft.Azure.Cosmos;

namespace AuthService.Services;

public class ClientStore
{
    private readonly Container _container;
    private readonly ILogger<ClientStore> _logger;

    public ClientStore(CosmosDbService cosmosDbService, ILogger<ClientStore> logger)
    {
        _container = cosmosDbService.GetContainer("clients");
        _logger = logger;
    }

    public async Task InitializeAsync()
    {
        _logger.LogInformation("ClientStore initialized with Cosmos DB container: clients");
        // Sample data removed - only real user-created clients will appear
    }

    public async Task<List<Client>> GetAllAsync()
    {
        var clients = new List<Client>();
        var query = _container.GetItemQueryIterator<Client>("SELECT * FROM c");
        
        while (query.HasMoreResults)
        {
            var response = await query.ReadNextAsync();
            clients.AddRange(response.ToList());
        }
        
        return clients.OrderByDescending(c => c.CreatedAt).ToList();
    }

    public async Task<Client?> GetByIdAsync(string id)
    {
        try
        {
            var response = await _container.ReadItemAsync<Client>(id, new PartitionKey(id));
            return response.Resource;
        }
        catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return null;
        }
    }

    public async Task<Client> CreateAsync(Client client)
    {
        client.Id = Guid.NewGuid().ToString();
        client.CreatedAt = DateTime.UtcNow;
        client.Status = ClientStatus.trial;
        
        // Initialize fleet based on fleetSize
        client.Fleet = new ClientFleet
        {
            TotalRobots = client.FleetSize,
            ActiveRobots = 0,
            IdleRobots = client.FleetSize,
            MaintenanceRobots = 0
        };
        
        // Calculate MRR based on plan
        var planMrr = new Dictionary<ClientPlan, int>
        {
            [ClientPlan.hobby] = 99,
            [ClientPlan.pro] = 499,
            [ClientPlan.business] = 2000,
            [ClientPlan.enterprise] = 0
        };
        
        client.Subscription = new ClientSubscription
        {
            StartDate = DateTime.UtcNow.ToString("yyyy-MM-dd"),
            EndDate = "",
            Mrr = planMrr.GetValueOrDefault(client.Plan, 0)
        };
        
        var response = await _container.CreateItemAsync(client, new PartitionKey(client.Id));
        _logger.LogInformation("Created client: {ClientId}", client.Id);
        
        return response.Resource;
    }

    public async Task<Client?> UpdateAsync(string id, UpdateClientRequest request)
    {
        var existing = await GetByIdAsync(id);
        if (existing == null) return null;
        
        if (request.Name != null) existing.Name = request.Name;
        if (request.Email != null) existing.Email = request.Email;
        if (request.Plan.HasValue) existing.Plan = request.Plan.Value;
        if (request.Status.HasValue) existing.Status = request.Status.Value;
        if (request.Locations != null) existing.Locations = request.Locations;
        if (request.FleetSize.HasValue)
        {
            existing.FleetSize = request.FleetSize.Value;
            existing.Fleet.TotalRobots = request.FleetSize.Value;
            existing.Fleet.IdleRobots = request.FleetSize.Value;
        }
        if (request.MagicTokens != null) existing.MagicTokens = request.MagicTokens;
        
        existing.UpdatedAt = DateTime.UtcNow;
        
        var response = await _container.ReplaceItemAsync(existing, id, new PartitionKey(id));
        _logger.LogInformation("Updated client: {ClientId}", id);
        
        return response.Resource;
    }

    public async Task<bool> DeleteAsync(string id)
    {
        try
        {
            await _container.DeleteItemAsync<Client>(id, new PartitionKey(id));
            _logger.LogInformation("Deleted client: {ClientId}", id);
            return true;
        }
        catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return false;
        }
    }

    public async Task<DashboardStatsResponse> GetDashboardStatsAsync()
    {
        var clients = await GetAllAsync();
        
        var totalRobots = clients.Sum(c => c.FleetSize);
        var activeDeployments = clients.Count(c => c.Status == ClientStatus.active && c.FleetSize > 0);
        var mrr = clients.Sum(c => c.Subscription.Mrr);
        var trialClients = clients.Count(c => c.Status == ClientStatus.trial);
        var activeClients = clients.Count(c => c.Status == ClientStatus.active);
        var suspendedClients = clients.Count(c => c.Status == ClientStatus.suspended);
        
        var planDistribution = clients
            .GroupBy(c => c.Plan.ToString().ToLower())
            .Select(g => new PlanDistribution { Plan = g.Key, Count = g.Count() })
            .ToList();
        
        // Generate last 6 months of MRR trend data
        var mrrTrend = new List<MonthlyMrr>();
        for (int i = 5; i >= 0; i--)
        {
            var month = DateTime.UtcNow.AddMonths(-i);
            mrrTrend.Add(new MonthlyMrr
            {
                Month = month.ToString("MMM"),
                Mrr = mrr // Simplified - in real app would calculate per month
            });
        }
        
        return new DashboardStatsResponse
        {
            TotalClients = clients.Count,
            TotalRobots = totalRobots,
            ActiveDeployments = activeDeployments,
            MonthlyRecurringRevenue = mrr,
            TrialClients = trialClients,
            ActiveClients = activeClients,
            SuspendedClients = suspendedClients,
            PlanDistribution = planDistribution,
            MrrTrend = mrrTrend
        };
    }
}

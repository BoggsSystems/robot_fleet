using Microsoft.Azure.Cosmos;
using AuthService.Models;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace AuthService.Services;

public class CosmosDbService
{
    private readonly CosmosClient _client;
    private readonly string _databaseName;
    private readonly Container _adminContainer;

    public CosmosDbService(string connectionString, string databaseName, string containerName)
    {
        var options = new CosmosClientOptions
        {
            Serializer = new CosmosTextJsonSerializer()
        };
        _client = new CosmosClient(connectionString, options);
        _databaseName = databaseName;
        _adminContainer = _client.GetContainer(databaseName, containerName);
    }

    // Custom serializer that uses System.Text.Json
    private class CosmosTextJsonSerializer : CosmosSerializer
    {
        private readonly JsonSerializerOptions _options = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };

        public override T FromStream<T>(Stream stream)
        {
            using (stream)
            {
                return JsonSerializer.Deserialize<T>(stream, _options)!;
            }
        }

        public override Stream ToStream<T>(T input)
        {
            var stream = new MemoryStream();
            JsonSerializer.Serialize(stream, input, _options);
            stream.Position = 0;
            return stream;
        }
    }

    // Get any container by name
    public Container GetContainer(string containerName)
    {
        return _client.GetContainer(_databaseName, containerName);
    }

    // Legacy methods for backward compatibility (using admin-users container)
    public async Task<AdminUser?> GetByUsernameAsync(string username)
    {
        try
        {
            var response = await _adminContainer.ReadItemAsync<AdminUser>(username, new PartitionKey(username));
            return response.Resource;
        }
        catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.NotFound)
        {
            return null;
        }
    }

    public async Task<AdminUser?> GetByIdAsync(int id)
    {
        // Query by id since it's not the partition key anymore
        var query = new QueryDefinition("SELECT * FROM c WHERE c.id = @id")
            .WithParameter("@id", id.ToString());
        
        var iterator = _adminContainer.GetItemQueryIterator<AdminUser>(query);
        var response = await iterator.ReadNextAsync();
        return response.FirstOrDefault();
    }

    public async Task<List<AdminUser>> GetAllAsync()
    {
        var query = new QueryDefinition("SELECT * FROM c");
        var iterator = _adminContainer.GetItemQueryIterator<AdminUser>(query);
        var users = new List<AdminUser>();

        while (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            users.AddRange(response);
        }

        return users;
    }

    public async Task<AdminUser> CreateAsync(AdminUser user)
    {
        user.Id = await GetNextIdAsync();
        user.CreatedAt = DateTime.UtcNow;
        
        // Use username as the document id and partition key
        var response = await _adminContainer.CreateItemAsync(user, new PartitionKey(user.Username));
        return response.Resource;
    }

    public async Task UpdateLastLoginAsync(int id)
    {
        var user = await GetByIdAsync(id);
        if (user != null)
        {
            user.LastLogin = DateTime.UtcNow;
            await _adminContainer.UpsertItemAsync(user, new PartitionKey(user.Username));
        }
    }

    public async Task<bool> UsernameExistsAsync(string username)
    {
        var user = await GetByUsernameAsync(username);
        return user != null;
    }

    private async Task<int> GetNextIdAsync()
    {
        var users = await GetAllAsync();
        if (users.Count == 0) return 1;
        return users.Max(u => u.Id) + 1;
    }
}

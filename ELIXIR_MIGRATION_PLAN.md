# GeneAgent to Elixir Migration and Optimization Plan

## Executive Summary

This document outlines a comprehensive plan for migrating GeneAgent, a Python-based language agent for gene set analysis, to Elixir. The migration leverages Elixir's concurrency model, fault tolerance, and Phoenix framework to create a more scalable, maintainable, and performant system.

## Current System Analysis

### Architecture Overview
- **Main Components**: 
  - `main_cascade.py`: Core orchestration logic with GPT-4 integration
  - `worker.py`: Agent class with function calling capabilities
  - `topic.py`: Topic verification module
  - 8 API modules for external biological databases
- **External Dependencies**: OpenAI GPT-4, NCBI databases, Enrichr, PubMed
- **Data Flow**: Sequential verification cascade with iterative refinement

### Key Features
1. **Self-verification mechanism** using domain-specific databases
2. **Multi-step claim generation and verification**
3. **Integration with 8+ biological databases**
4. **GPT-4 function calling** for structured API interactions
5. **Iterative refinement** of biological process names

## Migration Strategy

### Phase 1: Foundation Setup (Weeks 1-2)

#### 1.1 Phoenix Application Bootstrap
```bash
mix phx.new gene_agent --umbrella --database postgres
cd gene_agent
```

#### 1.2 Core Dependencies
Add to `mix.exs`:
- `:req` for HTTP requests (replacing Python `requests`)
- `:jason` for JSON handling
- `:oban` for background job processing
- `:openai_ex` or custom HTTP client for OpenAI integration
- `:floki` for XML parsing (PubMed data)
- `:csv` for dataset processing

#### 1.3 Application Structure
```
apps/
├── gene_agent_core/          # Business logic
├── gene_agent_web/           # Phoenix web interface
├── gene_agent_apis/          # External API integrations
└── gene_agent_workers/       # Background processing
```

### Phase 2: Core Domain Migration (Weeks 3-5)

#### 2.1 Gene Set Domain Models
```elixir
defmodule GeneAgentCore.GeneSet do
  use Ecto.Schema
  import Ecto.Changeset

  embedded_schema do
    field :genes, {:array, :string}
    field :process_name, :string
    field :summary, :string
    field :verification_status, :string, default: "pending"
    field :claims, {:array, :map}
    field :verification_results, {:array, :map}
    
    timestamps()
  end
end
```

#### 2.2 Analysis Pipeline
```elixir
defmodule GeneAgentCore.AnalysisPipeline do
  @moduledoc "Main analysis orchestration"
  
  def analyze_gene_set(gene_set_string) do
    with {:ok, gene_set} <- parse_gene_set(gene_set_string),
         {:ok, initial_analysis} <- generate_initial_analysis(gene_set),
         {:ok, verified_analysis} <- verify_analysis(initial_analysis) do
      {:ok, verified_analysis}
    end
  end
  
  defp verify_analysis(analysis) do
    analysis
    |> generate_claims()
    |> verify_claims_concurrently()
    |> refine_analysis()
  end
end
```

#### 2.3 Claim Verification Engine
```elixir
defmodule GeneAgentCore.VerificationEngine do
  @moduledoc "Concurrent claim verification"
  
  def verify_claims(claims) when is_list(claims) do
    claims
    |> Task.async_stream(&verify_single_claim/1, 
                         timeout: 30_000, 
                         max_concurrency: 8)
    |> Enum.map(&elem(&1, 1))
  end
  
  defp verify_single_claim(claim) do
    GeneAgentAPIs.agent_inference(claim)
  end
end
```

### Phase 3: API Integration Layer (Weeks 4-6)

#### 3.1 HTTP Client Abstraction
```elixir
defmodule GeneAgentAPIs.HTTPClient do
  @moduledoc "Unified HTTP client for all external APIs"
  
  def get(url, params \\ %{}, options \\ []) do
    Req.get(url, params: params, connect_options: options)
  end
  
  def post(url, body, headers \\ [], options \\ []) do
    Req.post(url, json: body, headers: headers, connect_options: options)
  end
end
```

#### 3.2 API Modules Migration
Transform each Python API module to Elixir:

```elixir
defmodule GeneAgentAPIs.ComplexAPI do
  alias GeneAgentAPIs.HTTPClient
  
  @base_url "https://www.ncbi.nlm.nih.gov/research/pubtator3-api/agentapi/complex/"
  
  def get_complex_for_gene_set(gene_set) when is_binary(gene_set) do
    gene_set = String.replace(gene_set, " ", "")
    
    params = %{
      "name" => gene_set,
      "retmode" => "json",
      "limit" => 10
    }
    
    case HTTPClient.get(@base_url, params) do
      {:ok, %{status: 200, body: body}} ->
        {:ok, Map.get(body, "results", %{})}
      {:ok, %{status: status}} ->
        {:error, "HTTP #{status}: Unable to fetch complex data"}
      {:error, reason} ->
        {:error, reason}
    end
  end
end
```

#### 3.3 Function Calling Integration
```elixir
defmodule GeneAgentCore.FunctionCalling do
  @moduledoc "OpenAI function calling integration"
  
  @function_definitions [
    %{
      "name" => "get_complex_for_gene_set",
      "description" => "Get complex information for gene sets",
      "parameters" => %{
        "type" => "object",
        "properties" => %{
          "gene_set" => %{
            "type" => "string",
            "description" => "Comma-separated gene set"
          }
        },
        "required" => ["gene_set"]
      }
    }
    # ... other function definitions
  ]
  
  def available_functions, do: @function_definitions
  
  def execute_function(function_name, arguments) do
    case function_name do
      "get_complex_for_gene_set" ->
        GeneAgentAPIs.ComplexAPI.get_complex_for_gene_set(arguments["gene_set"])
      # ... other function mappings
    end
  end
end
```

### Phase 4: OpenAI Integration (Weeks 5-7)

#### 4.1 OpenAI Client
```elixir
defmodule GeneAgentCore.OpenAIClient do
  alias GeneAgentCore.FunctionCalling
  
  def chat_completion(messages, opts \\ []) do
    body = %{
      model: "gpt-4",
      messages: messages,
      temperature: 0,
      functions: FunctionCalling.available_functions()
    }
    |> Map.merge(Enum.into(opts, %{}))
    
    case HTTPClient.post(openai_url(), body, openai_headers()) do
      {:ok, %{status: 200, body: response}} ->
        handle_response(response)
      {:ok, %{status: status}} ->
        {:error, "OpenAI API error: #{status}"}
      {:error, reason} ->
        {:error, reason}
    end
  end
  
  defp handle_response(%{"choices" => [%{"message" => message} | _]}) do
    case message do
      %{"function_call" => function_call} ->
        execute_function_call(function_call)
      %{"content" => content} ->
        {:ok, content}
    end
  end
end
```

#### 4.2 Agent PhD Implementation
```elixir
defmodule GeneAgentCore.AgentPhD do
  @moduledoc "Main agent for claim verification"
  
  def inference(claim) do
    system_message = """
    You are a helpful fact-checker. Your task is to verify the claim using the provided tools.
    If there are evidences in your contents, please start a message with "Report:" and return your findings along with evidences.
    """
    
    messages = [
      %{"role" => "system", "content" => system_message},
      %{"role" => "user", "content" => build_verification_prompt(claim)}
    ]
    
    verify_with_tools(messages, 0)
  end
  
  defp verify_with_tools(messages, loop_count) when loop_count < 20 do
    case OpenAIClient.chat_completion(messages) do
      {:ok, {:function_call, function_name, arguments}} ->
        result = FunctionCalling.execute_function(function_name, arguments)
        
        new_message = %{
          "role" => "function",
          "name" => function_name,
          "content" => format_function_response(result)
        }
        
        verify_with_tools(messages ++ [new_message], loop_count + 1)
        
      {:ok, content} ->
        extract_report(content)
        
      {:error, reason} ->
        {:error, reason}
    end
  end
  
  defp verify_with_tools(_messages, _loop_count), do: {:error, "Max iterations reached"}
end
```

### Phase 5: Concurrency Optimizations (Weeks 6-8)

#### 5.1 Concurrent Claim Processing
```elixir
defmodule GeneAgentCore.ConcurrentProcessor do
  @moduledoc "Optimized concurrent processing"
  
  def process_claims_concurrently(claims) do
    claims
    |> Task.async_stream(
      &process_single_claim/1,
      max_concurrency: System.schedulers_online() * 2,
      timeout: 60_000,
      on_timeout: :kill_task
    )
    |> Stream.map(fn
      {:ok, result} -> result
      {:exit, reason} -> {:error, "Task failed: #{inspect(reason)}"}
    end)
    |> Enum.to_list()
  end
  
  defp process_single_claim(claim) do
    # Individual claim processing with timeout handling
    Task.async(fn -> 
      GeneAgentCore.AgentPhD.inference(claim) 
    end)
    |> Task.await(30_000)
  rescue
    e -> {:error, "Claim processing failed: #{inspect(e)}"}
  end
end
```

#### 5.2 Background Job Processing
```elixir
defmodule GeneAgentWorkers.AnalysisJob do
  use Oban.Worker, queue: :analysis, max_attempts: 3
  
  @impl Oban.Worker
  def perform(%Oban.Job{args: %{"gene_set_id" => gene_set_id}}) do
    case GeneAgentCore.AnalysisPipeline.analyze_gene_set(gene_set_id) do
      {:ok, _result} -> :ok
      {:error, reason} -> {:error, reason}
    end
  end
end
```

### Phase 6: Phoenix Web Interface (Weeks 7-9)

#### 6.1 LiveView for Real-time Analysis
```elixir
defmodule GeneAgentWeb.AnalysisLive do
  use GeneAgentWeb, :live_view
  
  def mount(_params, _session, socket) do
    {:ok, assign(socket, :analysis_status, :idle)}
  end
  
  def handle_event("analyze", %{"genes" => genes}, socket) do
    # Start background analysis job
    %{gene_set: genes}
    |> GeneAgentWorkers.AnalysisJob.new()
    |> Oban.insert()
    
    {:noreply, assign(socket, :analysis_status, :processing)}
  end
  
  # Real-time updates via PubSub
  def handle_info({:analysis_complete, result}, socket) do
    {:noreply, assign(socket, analysis_result: result, analysis_status: :complete)}
  end
end
```

#### 6.2 API Endpoints
```elixir
defmodule GeneAgentWeb.AnalysisController do
  use GeneAgentWeb, :controller
  
  def analyze(conn, %{"genes" => genes}) do
    case GeneAgentCore.AnalysisPipeline.analyze_gene_set(genes) do
      {:ok, result} ->
        conn
        |> put_status(:ok)
        |> json(%{data: result})
        
      {:error, reason} ->
        conn
        |> put_status(:unprocessable_entity)
        |> json(%{error: reason})
    end
  end
end
```

### Phase 7: Performance Optimizations (Weeks 8-10)

#### 7.1 Caching Layer
```elixir
defmodule GeneAgentCore.Cache do
  @moduledoc "Redis-backed caching for API responses"
  
  def get_or_fetch(key, fetch_fn, ttl \\ 3600) do
    case Redix.command(:redix, ["GET", key]) do
      {:ok, nil} ->
        result = fetch_fn.()
        Redix.command(:redix, ["SETEX", key, ttl, Jason.encode!(result)])
        result
        
      {:ok, cached_data} ->
        Jason.decode!(cached_data)
    end
  end
end
```

#### 7.2 Connection Pooling
```elixir
# In config/config.exs
config :gene_agent_apis, :http_pool,
  size: 50,
  max_overflow: 100

# In application.ex
{Finch, name: GeneAgentAPIs.Finch, pools: http_pool_config()}
```

#### 7.3 Rate Limiting
```elixir
defmodule GeneAgentAPIs.RateLimiter do
  use GenServer
  
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end
  
  def acquire_token(api_name) do
    GenServer.call(__MODULE__, {:acquire, api_name})
  end
  
  # Implement token bucket algorithm for each API
end
```

## Optimization Opportunities

### 1. Concurrency Improvements
- **Current**: Sequential claim verification
- **Optimized**: Concurrent processing with configurable concurrency limits
- **Impact**: 5-10x faster claim verification

### 2. Caching Strategy
- **API Response Caching**: Cache external API responses (TTL: 1 hour)
- **OpenAI Response Caching**: Cache GPT responses for identical inputs
- **Gene Set Analysis Caching**: Cache complete analysis results

### 3. Resource Management
- **Connection Pooling**: Reuse HTTP connections
- **Circuit Breakers**: Prevent cascade failures
- **Backpressure**: Handle high-load scenarios gracefully

### 4. Monitoring and Observability
```elixir
defmodule GeneAgentCore.Telemetry do
  def setup do
    :telemetry.attach_many(
      "gene-agent-telemetry",
      [
        [:gene_agent, :analysis, :start],
        [:gene_agent, :analysis, :stop],
        [:gene_agent, :api, :request, :start],
        [:gene_agent, :api, :request, :stop]
      ],
      &handle_event/4,
      nil
    )
  end
end
```

## Testing Strategy

### 1. Unit Tests
```elixir
defmodule GeneAgentCore.AnalysisPipelineTest do
  use ExUnit.Case
  
  describe "analyze_gene_set/1" do
    test "processes valid gene set" do
      gene_set = "PEX1,PEX2,PEX3"
      
      assert {:ok, analysis} = AnalysisPipeline.analyze_gene_set(gene_set)
      assert analysis.process_name
      assert analysis.summary
    end
  end
end
```

### 2. Integration Tests
```elixir
defmodule GeneAgentAPIs.ComplexAPITest do
  use ExUnit.Case
  
  @tag :integration
  test "fetches complex data from API" do
    gene_set = "PEX1,PEX2,PEX3"
    
    assert {:ok, data} = ComplexAPI.get_complex_for_gene_set(gene_set)
    assert is_map(data)
  end
end
```

### 3. Load Tests
```elixir
defmodule GeneAgentCore.LoadTest do
  use ExUnit.Case
  
  @tag :load
  test "handles concurrent analysis requests" do
    tasks = for i <- 1..100 do
      Task.async(fn ->
        AnalysisPipeline.analyze_gene_set("GENE#{i}")
      end)
    end
    
    results = Task.await_many(tasks, 60_000)
    
    assert length(results) == 100
    assert Enum.all?(results, &match?({:ok, _}, &1))
  end
end
```

## Migration Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1 | Weeks 1-2 | Phoenix setup, dependencies |
| 2 | Weeks 3-5 | Core domain models, pipeline |
| 3 | Weeks 4-6 | API integrations |
| 4 | Weeks 5-7 | OpenAI integration |
| 5 | Weeks 6-8 | Concurrency optimizations |
| 6 | Weeks 7-9 | Web interface |
| 7 | Weeks 8-10 | Performance tuning |
| 8 | Weeks 9-11 | Testing, deployment |

## Deployment Strategy

### 1. Infrastructure
```yaml
# docker-compose.yml
version: '3.8'
services:
  gene_agent:
    build: .
    ports:
      - "4000:4000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/gene_agent
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: gene_agent
      POSTGRES_PASSWORD: postgres
      
  redis:
    image: redis:7-alpine
```

### 2. Monitoring Setup
```elixir
# config/prod.exs
config :gene_agent, GeneAgentWeb.Telemetry,
  metrics: [
    # Phoenix Metrics
    summary("phoenix.endpoint.stop.duration",
      unit: {:native, :millisecond}),
    
    # Custom metrics
    counter("gene_agent.analysis.count"),
    distribution("gene_agent.analysis.duration"),
    counter("gene_agent.api.requests.count"),
    distribution("gene_agent.api.requests.duration")
  ]
```

## Risk Mitigation

### 1. Technical Risks
- **API Rate Limits**: Implement rate limiting and circuit breakers
- **OpenAI Service Reliability**: Implement retry logic with exponential backoff
- **Memory Usage**: Use streaming for large datasets, implement proper cleanup

### 2. Migration Risks
- **Feature Parity**: Comprehensive test suite to ensure identical behavior
- **Performance Regression**: Load testing and benchmarking
- **Data Loss**: Migration scripts with rollback capabilities

## Success Metrics

### 1. Performance
- **Response Time**: <2s for typical gene set analysis (vs 10-30s current)
- **Throughput**: Handle 100+ concurrent analyses
- **Resource Usage**: <500MB memory per worker process

### 2. Reliability
- **Uptime**: 99.9% availability
- **Error Rate**: <1% failed analyses
- **Recovery Time**: <5 minutes for system recovery

### 3. Maintainability
- **Test Coverage**: >90% line coverage
- **Documentation**: Complete API and deployment docs
- **Code Quality**: Consistent with Elixir community standards

## Conclusion

This migration plan leverages Elixir's strengths in concurrency, fault tolerance, and maintainability to create a more scalable and reliable version of GeneAgent. The phased approach minimizes risk while delivering incremental value. The expected improvements include:

- **5-10x performance improvement** through concurrency
- **Better fault tolerance** with supervisor trees
- **Improved maintainability** with functional programming patterns
- **Enhanced scalability** for handling larger workloads
- **Real-time capabilities** with Phoenix LiveView

The migration timeline of 11 weeks provides adequate time for thorough testing and quality assurance while maintaining the system's critical functionality.
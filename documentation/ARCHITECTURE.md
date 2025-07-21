# 🏗️ Arquitetura do Projeto

## 📁 Estrutura do Projeto

```bash
acompanhamento/
├── app/                          # Código fonte principal
│   ├── api/                      # Camada de API (FastAPI)
│   │   ├── dependencies.py       # Dependências e validações
│   │   └── v1/                   # Versão da API
│   │       └── acompanhamento.py # Endpoints do microserviço
│   ├── core/                     # Configurações centrais
│   │   ├── config.py             # Configurações da aplicação
│   │   ├── exceptions.py         # Exceções customizadas
│   │   └── kafka.py              # Configurações do Kafka
│   ├── db/                       # Camada de banco de dados
│   │   ├── base.py               # Configurações base do DB
│   │   └── session.py            # Gerenciamento de sessões
│   ├── domain/                   # Regras de negócio
│   │   ├── acompanhamento_service.py # Serviços de negócio
│   │   └── order_state.py        # Gerenciamento de estados
│   ├── models/                   # Modelos de dados (Pydantic)
│   │   ├── acompanhamento.py     # Modelos principais
│   │   └── events.py             # Modelos de eventos
│   ├── repository/               # Camada de acesso a dados
│   │   └── acompanhamento_repository.py # Repository pattern
│   ├── schemas/                  # Schemas da API (Request/Response)
│   │   └── acompanhamento_schemas.py # Schemas FastAPI
│   └── main.py                   # Ponto de entrada da aplicação
├── tests/                        # Suite de testes
│   ├── unit/                     # Testes unitários
│   │   ├── api/                  # Testes da API
│   │   ├── models/               # Testes dos models
│   │   ├── repository/           # Testes do repository
│   │   ├── schemas/              # Testes dos schemas
│   │   └── service/              # Testes dos serviços
│   ├── integration/              # Testes de integração
│   ├── performance/              # Testes de performance
│   └── e2e/                      # Testes end-to-end
├── documentation/               # Documentação técnica do projeto
├── .github/workflows/            # Pipelines CI/CD
├── alembic/                      # Migrações do banco
├── docker-compose.yml            # Orquestração local
├── Dockerfile                    # Container da aplicação
├── pyproject.toml               # Dependências e configurações
└── run_tests.py                 # Test runner customizado
```

## 🎯 Camadas da Arquitetura

### 1. **API Layer** (`app/api/`)

-   **Responsabilidade**: Interface externa, validação de entrada, serialização
-   **Tecnologia**: FastAPI
-   **Componentes**: Endpoints, Dependencies, Middlewares

### 2. **Domain Layer** (`app/domain/`)

-   **Responsabilidade**: Regras de negócio, lógica de aplicação
-   **Tecnologia**: Python puro
-   **Componentes**: Services, Business Rules, State Management

### 3. **Repository Layer** (`app/repository/`)

-   **Responsabilidade**: Acesso a dados, persistência
-   **Tecnologia**: SQLAlchemy (preparado)
-   **Componentes**: Repository Pattern, Data Access Objects

### 4. **Models Layer** (`app/models/`)

-   **Responsabilidade**: Definição de entidades e estruturas de dados
-   **Tecnologia**: Pydantic
-   **Componentes**: Domain Models, Value Objects, Events

### 5. **Core Layer** (`app/core/`)

-   **Responsabilidade**: Configurações, utilitários centrais, exceções customizadas
-   **Tecnologia**: Pydantic Settings
-   **Componentes**: Config, Kafka Setup, Database Config, Custom Exceptions

## 🔄 Fluxo de Dados

```mermaid
graph TB
    A[API Request] --> B[FastAPI Endpoint]
    B --> C[Dependencies & Validation]
    C --> D[Domain Service]
    D --> E[Repository]
    E --> F[Database]
    F --> E
    E --> D
    D --> G[Response Schema]
    G --> H[FastAPI Response]
    H --> I[API Response]
```

## 📋 Modelos de Dados

### Principais Entidades:

1. **ItemPedido**

    - `id_produto: int`
    - `quantidade: int`
    - Validações de negócio integradas

2. **EventoPedido**

    - `id_pedido: int`
    - `cpf_cliente: str`
    - `status_pedido: StatusPedido`
    - `itens: List[ItemPedido]`
    - `total_pedido: float`
    - `data_pedido: datetime`
    - `tempo_estimado: Optional[str]`

3. **EventoPagamento**

    - `id_pedido: int`
    - `status_pagamento: StatusPagamento`
    - `valor_pago: float`
    - `data_pagamento: datetime`

4. **Acompanhamento**
    - União de dados de pedido e pagamento
    - Estado consolidado do pedido
    - Informações de tracking

### Enums de Status:

-   **StatusPedido**: `Recebido`, `Em Preparação`, `Pronto`, `Finalizado`
-   **StatusPagamento**: `Pendente`, `Pago`, `Falhou`

## � Endpoints da API

### Endpoints Implementados:

1. **Health Check**

    - `GET /` - Status básico da aplicação
    - `GET /health` - Health check detalhado com timestamp

2. **Acompanhamento de Pedidos**
    - `GET /acompanhamento/{id_pedido}` - Buscar pedido por ID
    - `PUT /acompanhamento/{id_pedido}/status` - Atualizar status do pedido
    - `GET /acompanhamento/fila/pedidos` - Listar fila de pedidos
    - `GET /acompanhamento/cliente/{cpf}` - Histórico do cliente

### Padrões de Response:

-   **Sucesso**: Status 200 com dados estruturados
-   **Erro**: Status 4xx/5xx com detalhes do erro
-   **Validação**: Automática via Pydantic
-   **Documentação**: Swagger automático em `/docs`

## 🧪 Estratégia de Testes

### **Cobertura Total: 402 testes | 91% coverage**

### 1. **Testes Unitários** (`tests/unit/`)

-   **295 testes** distribuídos por camada
-   **API Layer**: 152 testes (endpoints, schemas, dependencies)
-   **Models Layer**: 66 testes (validação, serialização)
-   **Service Layer**: 77 testes (business logic, calculations, error handling)

### 2. **Testes de Integração** (`tests/integration/`)

-   **26 testes** de integração entre componentes
-   **API Integration**: Workflows completos end-to-end
-   **Model Consistency**: Validação entre diferentes models

### 3. **Testes de Performance** (`tests/performance/`)

-   **46 testes** de performance e throughput
-   **Memory Monitoring**: Usando psutil para controle de memória
-   **Concurrent Testing**: Simulação de carga e stress
-   **Response Time**: Benchmarks de latência

### 4. **Testes E2E** (`tests/e2e/`)

-   **3 testes** de workflow completo
-   **Order Lifecycle**: Fluxo completo do pedido
-   **Error Recovery**: Cenários de falha e recuperação

### Ferramentas de Teste:

-   **Test Runner**: `python run_tests.py` (customizado)
-   **Coverage**: pytest-cov com relatórios HTML
-   **Performance**: psutil para monitoring de memória
-   **Mocking**: AsyncMock para testes assíncronos

## �🔧 Configurações

### Ambientes Suportados:

-   **Development**: Configurações para desenvolvimento local
-   **Test**: Configurações para execução de testes
-   **Production**: Configurações para ambiente produtivo

### Variáveis de Ambiente:

-   `DATABASE_URL`: URL de conexão com banco
-   `KAFKA_BOOTSTRAP_SERVERS`: Servidores Kafka
-   `LOG_LEVEL`: Nível de logging
-   `ENVIRONMENT`: Ambiente atual (dev/test/prod)

## 🚨 Tratamento de Exceções

### Exceções Customizadas (`app/core/exceptions.py`):

-   **AcompanhamentoException**: Base para exceções de negócio
-   **AcompanhamentoNotFound**: Pedido não encontrado
-   **InvalidStatusTransition**: Transição de status inválida
-   **ValidationError**: Erros de validação de dados

### Context Manager:

-   **handle_service_exceptions()**: Conversão automática para HTTP errors
-   **Logging**: Rastreamento automático de exceções
-   **User-Friendly**: Mensagens de erro padronizadas

## 🚀 Tecnologias Utilizadas

### **Core Framework:**

-   **FastAPI**: Framework web assíncrono com documentação automática
-   **Pydantic**: Validação de dados e serialização
-   **SQLAlchemy**: ORM para banco de dados (preparado para MySQL)
-   **Alembic**: Migrações de banco

### **Mensageria e Configuração:**

-   **Kafka**: Mensageria assíncrona (preparado)
-   **Poetry**: Gerenciamento de dependências
-   **Docker**: Containerização

### **Testes e Qualidade:**

-   **Pytest**: Framework de testes (402 testes implementados)
-   **pytest-cov**: Cobertura de código (91% atual)
-   **psutil**: Monitoring de performance e memória
-   **AsyncMock**: Testes assíncronos

### **DevOps e CI/CD:**

-   **GitHub Actions**: CI/CD pipeline
-   **Pre-commit**: Hooks de qualidade
-   **Custom Test Runner**: `run_tests.py` para execução organizada

### **Desenvolvimento:**

-   **VS Code**: Editor recomendado com configurações específicas
-   **Black**: Formatação de código
-   **isort**: Organização de imports

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
│   ├── e2e/                      # Testes end-to-end
│   └── bdd/                      # Testes BDD (Behavior Driven Development) ✅ NOVO
│       ├── features/             # Cenários Gherkin (.feature files)
│       └── test_acompanhamento_steps.py # Step definitions pytest-bdd
├── documentation/               # Documentação técnica do projeto
│   ├── ARCHITECTURE.md          # Arquitetura detalhada do projeto
│   ├── BRANCH_PROTECTION.md     # Regras de proteção de branch
│   ├── CI_CD_PIPELINE.md        # Pipeline de CI/CD
│   ├── PROJECT_REPORT.md        # Relatório histórico do projeto
│   ├── TESTING_GUIDE.md         # Guia de estratégia de testes
│   └── SONARCLOUD_SETUP.md      # Guia de configuração SonarCloud ✅ NOVO
├── .github/workflows/            # Pipelines CI/CD
├── alembic/                      # Migrações do banco
├── docker-compose.yml            # Orquestração local
├── Dockerfile                    # Container da aplicação
├── pyproject.toml               # Dependências e configurações
├── sonar-project.properties     # Configuração SonarCloud ✅ NOVO
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

### 3. **Repository Layer** (`app/repository/`) ✅ IMPLEMENTADO

-   **Responsabilidade**: Acesso a dados, persistência
-   **Tecnologia**: SQLAlchemy 2.0 com async/await ✅ NOVO
-   **Componentes**: Repository Pattern, Data Access Objects
-   **Implementação**:
    -   CRUD completo (Create, Read, Update, Delete)
    -   Eager loading com selectinload para evitar lazy loading
    -   Async sessions para performance
    -   Conversão automática entre modelos de banco e domínio
    -   Tratamento de constraints e integridade referencial

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

    %% Fluxo de Eventos Kafka ✅ NOVO
    J[Kafka Event - Pedido] --> K[POST /evento-pedido]
    K --> D
    L[Kafka Event - Pagamento] --> M[POST /evento-pagamento]
    M --> D

    %% Integração entre Microserviços ✅ NOVO
    N[Microserviço Pedidos] --> J
    O[Microserviço Pagamentos] --> L
```

### Processamento de Eventos ✅ NOVO

1. **Eventos de Pedido**: Microserviço de pedidos publica eventos que são processados via `/acompanhamento/evento-pedido`
2. **Eventos de Pagamento**: Microserviço de pagamentos publica eventos que são processados via `/acompanhamento/evento-pagamento`
3. **Consolidação**: Estados de pedido e pagamento são consolidados no acompanhamento
4. **Notificações**: Sistema pode notificar clientes sobre mudanças de status

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

3. **Processamento de Eventos (Kafka Integration)** ✅ NOVO
    - `POST /acompanhamento/evento-pedido` - Processar eventos de criação/atualização de pedidos via Kafka
    - `POST /acompanhamento/evento-pagamento` - Processar eventos de pagamento via Kafka

### Padrões de Response:

-   **Sucesso**: Status 200 com dados estruturados
-   **Erro**: Status 4xx/5xx com detalhes do erro
-   **Validação**: Automática via Pydantic
-   **Documentação**: Swagger automático em `/docs`

## 🧪 Estratégia de Testes

### **Cobertura Total: 428 testes | 91% coverage** ✅ ATUALIZADO

### 1. **Testes Unitários** (`tests/unit/`)

-   **336 testes** distribuídos por camada ✅ ATUALIZADO
-   **API Layer**: 152 testes (endpoints, schemas, dependencies)
-   **Models Layer**: 66 testes (validação, serialização)
-   **Repository Layer**: 41 testes (CRUD operations, mocking) ✅ NOVO
-   **Service Layer**: 77 testes (business logic, calculations, error handling)

### 2. **Testes de Integração** (`tests/integration/`)

-   **46 testes** de integração entre componentes ✅ ATUALIZADO
-   **Database Integration**: 8 testes de integração com SQLAlchemy ✅ NOVO
-   **API Integration**: 14 testes funcionais de endpoints ✅ NOVO
-   **Model Consistency**: Validação entre diferentes models

### 3. **Testes de Performance** (`tests/performance/`)

-   **39 testes** de performance e throughput ✅ ATUALIZADO
-   **Memory Monitoring**: Usando psutil para controle de memória
-   **Concurrent Testing**: Simulação de carga e stress
-   **Response Time**: Benchmarks de latência

### 4. **Testes E2E** (`tests/e2e/`)

-   **3 testes** de workflow completo
-   **Order Lifecycle**: Fluxo completo do pedido
-   **Error Recovery**: Cenários de falha e recuperação

### 5. **Testes BDD** (`tests/bdd/`) ✅ NOVO

-   **4 cenários BDD** em linguagem natural (Gherkin)
-   **44 step definitions** implementadas com pytest-bdd
-   **Cobertura de negócio**: Cenários de usuário em linguagem natural
-   **Cenários implementados**:
    1. **Cliente acompanha pedido do início ao fim** - Fluxo completo de status
    2. **Consulta de fila de pedidos pela cozinha** - Ordenação e informações
    3. **Cálculo de tempo estimado** - Baseado em categorias de itens
    4. **Validação de transição de status** - Regras de negócio e transições inválidas

### Ferramentas de Teste:

-   **Test Runner**: `python run_tests.py` (customizado) ✅ ATUALIZADO
    -   `run_tests.py unit` - Testes unitários rápidos
    -   `run_tests.py integration` - Testes de integração
    -   `run_tests.py performance` - Benchmarks de performance
    -   `run_tests.py e2e` - Testes end-to-end
    -   `run_tests.py bdd` - Cenários BDD (Behavior Driven Development) ✅ NOVO
    -   `run_tests.py coverage` - Relatório completo de cobertura
    -   `run_tests.py all` - Execução de todos os testes
-   **Coverage**: pytest-cov com relatórios HTML (91% atual) ✅ ATUALIZADO
-   **Performance**: psutil para monitoring de memória
-   **Mocking**: AsyncMock para testes assíncronos
-   **Database Testing**: SQLite in-memory para testes de integração ✅ NOVO
-   **Functional Testing**: Abordagem funcional para endpoints API ✅ NOVO
-   **BDD Framework**: pytest-bdd para cenários Gherkin ✅ NOVO

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

## 🎯 BDD (Behavior Driven Development) ✅ NOVO

### **Framework BDD Implementado:**

-   **pytest-bdd**: Framework para execução de cenários Gherkin
-   **Feature Files**: Cenários escritos em linguagem natural
-   **Step Definitions**: Implementação dos passos em Python

### **Cenários de Negócio Implementados:**

#### 1. **Cliente acompanha pedido do início ao fim**

```gherkin
Scenario: Cliente acompanha pedido do início ao fim
    Given que um cliente fez um pedido com id "12345"
    And o pedido contém "2" lanches e "1" bebida
    And o pagamento foi aprovado
    When o pedido é enviado para a cozinha
    Then o status deve ser "Recebido"
    And o tempo estimado deve ser calculado
    When a cozinha inicia o preparo
    Then o status deve ser atualizado para "Em preparação"
    When a cozinha finaliza o preparo
    Then o status deve ser atualizado para "Pronto"
```

#### 2. **Consulta de fila de pedidos pela cozinha**

-   **Objetivo**: Validar ordenação e informações da fila
-   **Cobertura**: Lista de pedidos ordenados por tempo de criação

#### 3. **Cálculo de tempo estimado baseado nos itens**

-   **Objetivo**: Verificar regras de cálculo de tempo
-   **Cobertura**: Diferentes categorias de produtos (lanche, acompanhamento, bebida)

#### 4. **Validação de transição de status**

-   **Objetivo**: Testar regras de transição de status
-   **Cobertura**: Transições válidas e inválidas

### **Execução dos Testes BDD:**

```bash
# Executar todos os cenários BDD
poetry run python run_tests.py bdd

# Executar diretamente com pytest
poetry run python -m pytest tests/bdd/ -v
```

### **Benefícios do BDD:**

-   **Linguagem Natural**: Cenários legíveis por stakeholders
-   **Documentação Viva**: Testes que documentam o comportamento
-   **Colaboração**: Ponte entre negócio e desenvolvimento
-   **Regressão**: Garantia de que comportamentos não sejam quebrados

## 📊 SonarCloud Integration ✅ NOVO

### **Análise Automática de Qualidade:**

-   **Code Quality**: Bugs, vulnerabilidades, code smells
-   **Security Analysis**: OWASP Top 10, security hotspots
-   **Coverage Integration**: Relatórios de cobertura automáticos
-   **Technical Debt**: Métricas de dívida técnica

### **Configuração Implementada:**

#### **sonar-project.properties:**

```properties
sonar.projectKey=ju-c-lopes_microservico-acompanhamento
sonar.organization=ju-c-lopes
sonar.sources=app
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.qualitygate.wait=true
```

#### **GitHub Actions Integration:**

-   **Job sonarcloud**: Executa após testes passarem
-   **Análise automática**: Em pushes e pull requests
-   **Quality Gate**: Critérios de qualidade automáticos

### **Métricas Analisadas:**

-   **Maintainability Rating**: A (atual)
-   **Reliability Rating**: A (atual)
-   **Security Rating**: A (atual)
-   **Coverage**: 91% (atual)
-   **Duplicated Lines**: < 3%
-   **Code Smells**: Identificação automática

### **Benefícios:**

-   **Tech Challenge Compliance**: Atende requisito SonarQube
-   **Qualidade Contínua**: Análise automática em cada mudança
-   **Dashboards Profissionais**: Métricas visuais detalhadas
-   **Detecção Precoce**: Issues identificados antes do merge

## 🚀 Tecnologias Utilizadas

### **Core Framework:**

-   **FastAPI**: Framework web assíncrono com documentação automática
-   **Pydantic**: Validação de dados e serialização
-   **SQLAlchemy**: ORM async implementado para MySQL/SQLite ✅ IMPLEMENTADO
-   **Alembic**: Migrações de banco

### **Mensageria e Configuração:**

-   **Kafka**: Mensageria assíncrona (preparado)
-   **Poetry**: Gerenciamento de dependências
-   **Docker**: Containerização

### **Testes e Qualidade:**

-   **Pytest**: Framework de testes (428 testes implementados) ✅ ATUALIZADO
-   **pytest-cov**: Cobertura de código (91% atual) ✅ ATUALIZADO
-   **pytest-bdd**: Framework BDD para cenários Gherkin ✅ NOVO
-   **psutil**: Monitoring de performance e memória
-   **AsyncMock**: Testes assíncronos
-   **SQLite**: Database in-memory para testes de integração ✅ NOVO
-   **SonarCloud**: Análise automática de qualidade de código ✅ NOVO

### **DevOps e CI/CD:**

-   **GitHub Actions**: CI/CD pipeline ✅ ATUALIZADO
    -   **Job test**: Execução de todos os tipos de teste
    -   **Job security-scan**: Análise de segurança
    -   **Job sonarcloud**: Análise de qualidade com SonarCloud ✅ NOVO
    -   **Job build**: Build e teste de containers Docker
    -   **Job quality-gate**: Validação final de qualidade
-   **SonarCloud**: Análise contínua de qualidade, segurança e cobertura ✅ NOVO
-   **Pre-commit**: Hooks de qualidade
-   **Custom Test Runner**: `run_tests.py` para execução organizada

### **Desenvolvimento:**

-   **VS Code**: Editor recomendado com configurações específicas
-   **Black**: Formatação de código
-   **isort**: Organização de imports

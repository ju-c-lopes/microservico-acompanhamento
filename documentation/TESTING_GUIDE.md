# 🧪 Guia de Testes

## Categorias de Testes

Nossa suite de testes está organizada em categorias que executam automaticamente:

```bash
# Unit Tests (rápidos, isolados)
tests/unit/models/          # Testes de validação de models
tests/unit/schemas/         # Testes de validação de schemas
tests/unit/api/             # Testes da camada API
tests/unit/repository/      # Testes do repository
tests/unit/service/         # Testes da camada de serviço

# Integration Tests (interação entre componentes)
tests/integration/          # Database integration, API endpoints, Model consistency ✅ ATUALIZADO

# Performance Tests (carga e velocidade)
tests/performance/          # Benchmarks de performance dos models

# End-to-End Tests (fluxo completo)
tests/e2e/                  # Cenários completos de negócio

# BDD Tests (comportamento em linguagem natural) ✅ NOVO
tests/bdd/                  # Cenários BDD com Gherkin (pytest-bdd)
tests/bdd/features/         # Arquivos .feature com cenários em linguagem natural
tests/bdd/test_acompanhamento_steps.py # Step definitions para pytest-bdd
```

## 🔧 Executando Testes Localmente

### Usando o Test Runner Customizado

```bash
# Testes por categoria
python run_tests.py unit           # Apenas unit tests
python run_tests.py integration    # Apenas integration tests
python run_tests.py performance    # Apenas performance tests
python run_tests.py e2e            # Apenas end-to-end tests
python run_tests.py bdd            # Apenas BDD tests (Behavior Driven Development) ✅ NOVO

# Testes por camada
python run_tests.py models         # Testes de models
python run_tests.py repository     # Testes de repository
python run_tests.py service        # Testes de serviço
python run_tests.py api            # Testes da API
python run_tests.py schemas        # Testes de schemas

# Testes específicos por model
python run_tests.py item           # ItemPedido tests
python run_tests.py evento-pedido  # EventoPedido tests
python run_tests.py evento-pagamento # EventoPagamento tests
python run_tests.py acompanhamento # Acompanhamento tests

# Testes combinados
python run_tests.py fast           # Unit + Integration (rápidos)
python run_tests.py ci             # Todos exceto performance (ideal para CI)
python run_tests.py all            # Todos os testes
python run_tests.py coverage       # Todos os testes com cobertura
```

### Usando Pytest Diretamente

```bash
# Instalar dependências
poetry install

# Executar testes específicos
poetry run pytest tests/unit/                    # Unit tests
poetry run pytest tests/integration/             # Integration tests
poetry run pytest tests/performance/             # Performance tests
poetry run pytest tests/e2e/                     # End-to-end tests
poetry run pytest tests/bdd/                     # BDD tests ✅ NOVO

# Com cobertura
poetry run pytest tests/ --cov=app/models        # Cobertura de models
poetry run pytest tests/ --cov=app --cov-report=html  # Relatório HTML

# Testes específicos
poetry run pytest -m performance                 # Apenas performance tests
poetry run pytest tests/unit/models/test_item_pedido.py  # Arquivo específico
poetry run pytest -k "test_create_valid"         # Testes que contenham o nome
```

## 📊 Relatórios de Cobertura

```bash
# Gerar relatório de cobertura
python run_tests.py coverage

# Visualizar relatório HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🎯 Estrutura dos Testes

### Unit Tests

-   **Objetivo**: Testar componentes individuais isoladamente
-   **Características**: Rápidos, sem dependências externas
-   **Cobertura**: Models, Schemas, Business Logic, API Endpoints, Repository
-   **Total**: 336 testes distribuídos por: ✅ ATUALIZADO
    -   **API Layer**: 152 testes (endpoints, dependencies, schemas, configurations)
    -   **Models Layer**: 66 testes (validation, serialization)
    -   **Repository Layer**: 41 testes (CRUD operations, mocking) ✅ NOVO
    -   **Service Layer**: 77 testes (business logic, calculations, error handling)

### Integration Tests

-   **Objetivo**: Testar interação entre componentes
-   **Características**: Moderados, com dependências controladas
-   **Cobertura**: Database integration, API endpoints, Model consistency
-   **Total**: 46 testes incluindo: ✅ ATUALIZADO
    -   **Database Integration**: 8 testes com SQLAlchemy async ✅ NOVO
    -   **API Integration**: 14 testes funcionais de endpoints ✅ NOVO
    -   **Model Consistency**: Validação entre diferentes models

### Performance Tests

-   **Objetivo**: Validar performance e benchmarks
-   **Características**: Foco em tempo de execução e memória
-   **Cobertura**: Large datasets, Concurrent operations, Memory stability
-   **Total**: 39 testes com monitoring via psutil ✅ ATUALIZADO
-   **Features**: Memory monitoring, concurrent testing, throughput analysis

### End-to-End Tests

-   **Objetivo**: Testar fluxos completos de negócio
-   **Características**: Cenários reais, múltiplos componentes
-   **Cobertura**: Complete order lifecycle, Business workflows
-   **Total**: 3 testes covering full order workflows

### BDD Tests ✅ NOVO

-   **Objetivo**: Documentar comportamento em linguagem natural (Gherkin)
-   **Características**: Cenários legíveis por stakeholders, colaboração
-   **Cobertura**: Comportamentos de negócio em linguagem natural
-   **Total**: 4 cenários BDD com 44 step definitions
-   **Cenários implementados**:
    1. **Cliente acompanha pedido do início ao fim** - Fluxo completo de status
    2. **Consulta de fila de pedidos pela cozinha** - Ordenação e informações
    3. **Cálculo de tempo estimado** - Baseado em categorias de itens
    4. **Validação de transição de status** - Regras de negócio e transições inválidas
-   **Framework**: pytest-bdd para execução de cenários Gherkin
-   **Benefícios**: Documentação viva, colaboração negócio-desenvolvimento

## 🚀 Métricas de Qualidade

-   **Total de Testes**: 428 testes ✅ ATUALIZADO
-   **Cobertura**: 91% atual (90%+ mantida) ✅ ATUALIZADO
-   **Performance**: ~1.4s para suite completa
-   **Categorias**: 5 tipos organizados (unit, integration, performance, e2e, bdd) ✅ ATUALIZADO
-   **Distribuição**:
    -   **336 Unit Tests**: API (152), Models (66), Repository (41), Service (77) ✅ ATUALIZADO
    -   **46 Integration Tests**: Database (8), API endpoints (14), Model consistency ✅ ATUALIZADO
    -   **39 Performance Tests**: Memory monitoring, Throughput, Concurrency ✅ ATUALIZADO
    -   **3 E2E Tests**: Complete business workflows
    -   **4 BDD Tests**: Cenários em linguagem natural (Gherkin) ✅ NOVO

## 📋 Comandos Úteis

```bash
# Ver ajuda do test runner
python run_tests.py

# Executar testes com verbose
poetry run pytest tests/ -v

# Executar testes em paralelo
poetry run pytest tests/ -n auto

# Falhar no primeiro erro
poetry run pytest tests/ -x

# Executar apenas testes que falharam
poetry run pytest tests/ --lf
```

## 🛠️ Ferramentas e Tecnologias de Teste

### **Principais Ferramentas:**

-   **pytest**: Framework de testes principal (428 testes) ✅ ATUALIZADO
-   **pytest-cov**: Cobertura de código (91% atual) ✅ ATUALIZADO
-   **pytest-bdd**: Framework BDD para cenários Gherkin ✅ NOVO
-   **psutil**: Monitoring de memória em performance tests
-   **AsyncMock**: Testes assíncronos para services e repositories
-   **SQLite**: Database in-memory para testes de integração ✅ NOVO
-   **Custom Test Runner**: `run_tests.py` para execução organizada

### **Padrões de Teste Implementados:**

-   **Direct Function Testing**: Evita problemas com TestClient
-   **AsyncMock Patterns**: Para repository e service mocking
-   **Database Testing**: SQLite in-memory para integração ✅ NOVO
-   **Functional API Testing**: Abordagem funcional para endpoints ✅ NOVO
-   **Memory Monitoring**: Testes de estabilidade de memória
-   **Concurrent Testing**: Simulação de carga e stress
-   **Context Managers**: Para setup/teardown consistente

### **Arquivos de Configuração:**

-   `conftest.py`: Fixtures compartilhadas por nível
-   `pytest.ini`: Configurações globais do pytest
-   `run_tests.py`: Test runner customizado com 12 comandos ✅ ATUALIZADO

## 📊 Análise de Qualidade com SonarCloud ✅ NOVO

### **Integração Automática:**

-   **SonarCloud**: Análise contínua de qualidade, segurança e cobertura
-   **GitHub Actions**: Integração automática com CI/CD pipeline
-   **Quality Gate**: Critérios de qualidade automáticos

### **Métricas Analisadas:**

-   **Maintainability Rating**: A (atual)
-   **Reliability Rating**: A (atual)
-   **Security Rating**: A (atual)
-   **Coverage**: 91% (integrado aos testes)
-   **Duplicated Lines**: < 3%
-   **Code Smells**: Identificação automática
-   **Security Hotspots**: OWASP Top 10 compliance
-   **Technical Debt**: Métricas de dívida técnica

### **Configuração:**

```bash
# Arquivo de configuração SonarCloud
sonar-project.properties

# Documentação completa de setup
documentation/SONARCLOUD_SETUP.md
```

### **Execução:**

-   **Automática**: Em pushes e pull requests
-   **Manual**: Via GitHub Actions
-   **Local**: Possível configuração via SonarScanner

### **Benefícios:**

-   **Tech Challenge Compliance**: Atende requisito SonarQube/SonarCloud
-   **Qualidade Contínua**: Análise automática em cada mudança
-   **Dashboards Profissionais**: Métricas visuais detalhadas
-   **Detecção Precoce**: Issues identificados antes do merge
-   **Security Analysis**: Vulnerabilidades e hotspots de segurança

## 🎯 BDD (Behavior Driven Development) ✅ NOVO

### **Framework Implementado:**

```bash
# Executar cenários BDD
python run_tests.py bdd

# Executar com pytest diretamente
poetry run pytest tests/bdd/ -v
```

### **Estrutura de Arquivos:**

```bash
tests/bdd/
├── features/
│   └── acompanhamento_pedido.feature    # Cenários Gherkin
└── test_acompanhamento_steps.py         # Step definitions
```

### **Exemplo de Cenário Gherkin:**

```gherkin
Scenario: Cliente acompanha pedido do início ao fim
    Given que um cliente fez um pedido com id "12345"
    And o pedido contém "2" lanches e "1" bebida
    And o pagamento foi aprovado
    When o pedido é enviado para a cozinha
    Then o status deve ser "Recebido"
    And o tempo estimado deve ser calculado
```

### **Step Definitions:**

-   **44 step definitions** implementadas com decorators pytest-bdd
-   **@given, @when, @then**: Padrões BDD bem definidos
-   **Integração**: Com services e models do domínio
-   **Validação**: Comportamentos de negócio testados

### **Benefícios BDD:**

-   **Linguagem Natural**: Cenários legíveis por stakeholders
-   **Documentação Viva**: Testes que documentam o comportamento
-   **Colaboração**: Ponte entre negócio e desenvolvimento
-   **Regressão**: Garantia de que comportamentos não sejam quebrados
-   **Especificação**: Living specification do sistema

# 🍔 Microserviço de Acompanhamento - Tech Challenge Fase 4

[![CI/CD Pipeline](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/ci.yml/badge.svg)](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/ci.yml)
[![Tests](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/test.yml/badge.svg)](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/test.yml)
[![Coverage](coverage.svg)](htmlcov/index.html)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ju-c-lopes_microservico-acompanhamento&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ju-c-lopes_microservico-acompanhamento)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ju-c-lopes_microservico-acompanhamento&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ju-c-lopes_microservico-acompanhamento)

Microserviço responsável pelo acompanhamento de pedidos em uma lanchonete, desenvolvido com FastAPI e arquitetura limpa.

## � Tech Challenge Compliance

**✅ TODOS OS REQUISITOS ATENDIDOS:**

-   🧪 **BDD (Behavior Driven Development)**: 4 cenários em linguagem natural com Gherkin
-   📊 **SonarQube/SonarCloud**: Análise contínua de qualidade e segurança (Rating A)
-   🏗️ **Clean Architecture**: Separação em camadas bem definidas
-   🚀 **FastAPI + Kafka**: API REST completa com integração de eventos
-   🧪 **428 Testes**: Coverage 91% com múltiplas categorias de teste

## �🎯 Sobre o Projeto

Este microserviço gerencia o ciclo de vida dos pedidos, desde o recebimento até a finalização, integrando informações de pedidos e pagamentos para fornecer uma experiência completa de acompanhamento aos clientes.

### ✨ Funcionalidades Principais

-   📦 **Acompanhamento de Pedidos**: Tracking completo do status dos pedidos
-   💰 **Integração de Pagamentos**: Consolidação de informações de pagamento
-   ⏰ **Cálculo de Tempo Estimado**: Estimativas inteligentes baseadas nos itens
-   🔄 **Gerenciamento de Estados**: Transições validadas entre status
-   📊 **Fila de Pedidos**: Organização e priorização de pedidos
-   🚀 **Event Streaming**: Processamento de eventos via Kafka
-   🧪 **BDD Tests**: Cenários comportamentais em linguagem natural (Gherkin)
-   📈 **Quality Assurance**: Análise contínua via SonarCloud

### 🏗️ Arquitetura

```
📁 Estrutura em Camadas
├── 🌐 API Layer (FastAPI)      # Interface externa
├── 🧠 Domain Layer             # Regras de negócio
├── 💾 Repository Layer         # Acesso a dados
├── 📋 Models Layer (Pydantic)  # Estruturas de dados
└── ⚙️  Core Layer              # Configurações
```

**Principais Componentes:**

-   **Models**: `ItemPedido`, `EventoPedido`, `EventoPagamento`, `Acompanhamento`
-   **Status**: Recebido → Em Preparação → Pronto → Finalizado
-   **Pagamentos**: Pendente → Pago → Falhou

## 🏆 Qualidade & Testing (Tech Challenge)

### 🧪 Testing Strategy (428 testes | 91% coverage)

-   **BDD Tests**: 4 cenários Gherkin para validação comportamental
-   **Unit/Integration/E2E**: Cobertura completa de casos de uso
-   **Performance Tests**: Benchmarks com métricas de tempo
-   **Automated CI/CD**: Execução em todos os PRs

### 📊 Continuous Quality

-   **SonarCloud Integration**: A-ratings em todas as métricas
-   **Code Coverage**: 91% de cobertura de código
-   **Clean Architecture**: Separação rigorosa de responsabilidades
-   **FastAPI + Kafka**: Stack moderna para microserviços

## 🚀 Como Usar

### 📋 Pré-requisitos

-   Python 3.11+
-   Poetry
-   Docker (opcional)

### ⚡ Instalação

```bash
# 1. Instalação do poetry
# Linux, MacOS, Windows (WSL)
curl -sSL https://install.python-poetry.org | python3 -

# Adicionar ao PATH (escolha seu shell):
# Para Bash:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
# Para Zsh (macOS padrão):
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# Verificar instalação:
poetry --version

# 2. Clonar o repositório
git clone https://github.com/ju-c-lopes/microservico-acompanhamento.git
cd microservico-acompanhamento

# 3. Instalar dependências
poetry install

# 4. Executar testes
python run_tests.py all

# 5. Executar a aplicação (quando disponível)
poetry run uvicorn app.main:app --reload
```

### 🧪 Executando Testes

```bash
# Executar todos os testes (428 testes | 91% coverage)
python run_tests.py all

# Testes por categoria
python run_tests.py unit           # Testes unitários (rápidos)
python run_tests.py integration    # Testes de integração
python run_tests.py performance    # Testes de performance
python run_tests.py e2e            # Testes end-to-end + BDD

# Testes por camada
python run_tests.py models         # Testes de models
python run_tests.py api            # Testes da API
python run_tests.py schemas        # Testes de schemas

# BDD - Behavior Driven Development (Gherkin scenarios)
pytest tests/bdd/                  # 4 cenários comportamentais

# Coverage report
python run_tests.py coverage       # Relatório de cobertura detalhado
```

## ⚙️ Executando com Docker


### 🐳 Docker

```bash
# Build da imagem
docker build -t acompanhamento .

# Executar com docker-compose
docker-compose up -d
````

## 📊 Estado Atual do Projeto

### ✅ Implementado

-   **✅ Modelos de Dados Completos** (Pydantic)

    -   ItemPedido, EventoPedido, EventoPagamento, Acompanhamento
    -   Validações de negócio integradas
    -   Enums de status com valores em português

-   **✅ API REST + Kafka** (FastAPI)

    -   9 endpoints implementados e funcionais
    -   Event processing para integração entre microserviços
    -   Validação automática via Pydantic
    -   Error handling e dependency injection

-   **✅ Suite de Testes Robusta** (428 testes | 91% coverage)

    -   **BDD Tests**: 4 cenários Gherkin para validação comportamental
    -   Unit tests (isolados e rápidos)
    -   Integration tests (interação entre componentes)
    -   Performance tests (benchmarks)
    -   End-to-end tests (fluxos completos)
    -   Schema tests (validação FastAPI)

-   **✅ Test Runner Customizado**

    -   15+ comandos especializados
    -   Execução por categoria ou camada
    -   Relatórios de cobertura
    -   Suporte completo para BDD

-   **✅ Pipeline CI/CD + Quality Assurance**

    -   **SonarCloud Integration**: A-ratings em todas as métricas
    -   Testes automáticos em Python 3.11 e 3.12
    -   Quality gates obrigatórios
    -   Proteção de branch main
    -   Escaneamento de segurança
    -   Code coverage tracking

-   **✅ Repository Layer** (SQLAlchemy)

    -   Interface completa implementada
    -   Operações CRUD com async/await
    -   Testes de integração validados

### 🚧 Em Desenvolvimento

-   **Database Integration** (MySQL via RDS)
-   **Kafka Infrastructure** (Consumer/Producer deployment)
-   **Database Migrations** (Alembic)

## 📚 Documentação

-   📖 [**Arquitetura**](documentation/ARCHITECTURE.md) - Estrutura e design do projeto
-   🧪 [**Guia de Testes**](documentation/TESTING_GUIDE.md) - Como executar e organizar testes
-   🚀 [**Pipeline CI/CD**](documentation/CI_CD_PIPELINE.md) - Workflows e automações
-   🛡️ [**Proteção de Branch**](documentation/BRANCH_PROTECTION.md) - Configurações de segurança
-   📊 [**Relatório do Projeto**](documentation/PROJECT_REPORT.md) - Histórico completo de desenvolvimento

## 👥 Contribuindo

```bash
# 1. Criar feature branch
git checkout develop
git pull origin develop
git checkout -b feature/sua-feature

# 2. Desenvolver e testar
python run_tests.py all

# 3. Commit e push
git add .
git commit -m "feat: sua descrição"
git push origin feature/sua-feature

# 4. Criar Pull Request para main
```

## 📈 Métricas de Qualidade

-   **Testes**: 424 testes executados automaticamente
-   **Cobertura**: 97% atual (superou meta 90%)
-   **Performance**: ~3.1s para suite completa
-   **Segurança**: Escaneamento automático de vulnerabilidades
-   **Qualidade**: Validações de código obrigatórias 

---

**Tech Challenge FIAP - Fase 4** | Desenvolvido com ❤️ e FastAPI 

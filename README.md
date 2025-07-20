# 🍔 Microserviço de Acompanhamento - Tech Challenge Fase 4

[![CI/CD Pipeline](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/ci.yml/badge.svg)](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/ci.yml)
[![Tests](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/test.yml/badge.svg)](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/test.yml)
[![Coverage](coverage.svg)](htmlcov/index.html)

Microserviço responsável pelo acompanhamento de pedidos em uma lanchonete, desenvolvido com FastAPI e arquitetura limpa.

## 🎯 Sobre o Projeto

Este microserviço gerencia o ciclo de vida dos pedidos, desde o recebimento até a finalização, integrando informações de pedidos e pagamentos para fornecer uma experiência completa de acompanhamento aos clientes.

### ✨ Funcionalidades Principais

-   📦 **Acompanhamento de Pedidos**: Tracking completo do status dos pedidos
-   💰 **Integração de Pagamentos**: Consolidação de informações de pagamento
-   ⏰ **Cálculo de Tempo Estimado**: Estimativas inteligentes baseadas nos itens
-   🔄 **Gerenciamento de Estados**: Transições validadas entre status
-   📊 **Fila de Pedidos**: Organização e priorização de pedidos

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

## 🚀 Como Usar

### 📋 Pré-requisitos

-   Python 3.11+
-   Poetry
-   Docker (opcional)

### ⚡ Instalação Rápida

```bash
# 1. Clonar o repositório
git clone https://github.com/ju-c-lopes/microservico-acompanhamento.git
cd microservico-acompanhamento

# 2. Instalar dependências
poetry install

# 3. Executar testes
python run_tests.py all

# 4. Executar a aplicação (quando disponível)
poetry run uvicorn app.main:app --reload
```

### 🧪 Executando Testes

```bash
# Executar todos os testes
python run_tests.py all

# Testes por categoria
python run_tests.py unit           # Testes unitários (rápidos)
python run_tests.py integration    # Testes de integração
python run_tests.py performance    # Testes de performance
python run_tests.py e2e            # Testes end-to-end

# Testes por camada
python run_tests.py models         # Testes de models
python run_tests.py api            # Testes da API
python run_tests.py schemas        # Testes de schemas

# Com cobertura
python run_tests.py coverage
```

### 🐳 Docker

```bash
# Build da imagem
docker build -t acompanhamento .

# Executar com docker-compose
docker-compose up -d
```

## 📊 Estado Atual do Projeto

### ✅ Implementado

-   **✅ Modelos de Dados Completos** (Pydantic)

    -   ItemPedido, EventoPedido, EventoPagamento, Acompanhamento
    -   Validações de negócio integradas
    -   Enums de status com valores em português

-   **✅ Suite de Testes Robusta** (368+ testes)

    -   Unit tests (isolados e rápidos)
    -   Integration tests (interação entre componentes)
    -   Performance tests (benchmarks)
    -   End-to-end tests (fluxos completos)
    -   Schema tests (validação FastAPI)

-   **✅ Test Runner Customizado**

    -   15+ comandos especializados
    -   Execução por categoria ou camada
    -   Relatórios de cobertura

-   **✅ Pipeline CI/CD Completo**
    -   Testes automáticos em Python 3.11 e 3.12
    -   Quality gates obrigatórios
    -   Proteção de branch main
    -   Escaneamento de segurança

### 🚧 Em Desenvolvimento

-   **API Endpoints** (FastAPI)
-   **Repository Implementation** (SQLAlchemy)
-   **Kafka Integration** (Event Streaming)
-   **Database Migrations** (Alembic)

## 📚 Documentação

-   📖 [**Arquitetura**](documentation/ARCHITECTURE.md) - Estrutura e design do projeto
-   🧪 [**Guia de Testes**](documentation/TESTING_GUIDE.md) - Como executar e organizar testes
-   🚀 [**Pipeline CI/CD**](documentation/CI_CD_PIPELINE.md) - Workflows e automações
-   🛡️ [**Proteção de Branch**](documentation/BRANCH_PROTECTION.md) - Configurações de segurança

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

-   **Testes**: 368+ testes executados automaticamente
-   **Cobertura**: 90%+ mantida
-   **Performance**: < 2s para suite completa
-   **Segurança**: Escaneamento automático de vulnerabilidades
-   **Qualidade**: Validações de código obrigatórias

---

**Tech Challenge FIAP - Fase 4** | Desenvolvido com ❤️ e FastAPI

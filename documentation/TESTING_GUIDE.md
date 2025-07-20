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
tests/integration/          # Testes de consistência de models

# Performance Tests (carga e velocidade)
tests/performance/          # Benchmarks de performance dos models

# End-to-End Tests (fluxo completo)
tests/e2e/                  # Cenários completos de negócio
```

## 🔧 Executando Testes Localmente

### Usando o Test Runner Customizado

```bash
# Testes por categoria
python run_tests.py unit           # Apenas unit tests
python run_tests.py integration    # Apenas integration tests
python run_tests.py performance    # Apenas performance tests
python run_tests.py e2e            # Apenas end-to-end tests

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
- **Objetivo**: Testar componentes individuais isoladamente
- **Características**: Rápidos, sem dependências externas
- **Cobertura**: Models, Schemas, Business Logic

### Integration Tests
- **Objetivo**: Testar interação entre componentes
- **Características**: Moderados, com dependências controladas
- **Cobertura**: Model consistency, Repository integration

### Performance Tests
- **Objetivo**: Validar performance e benchmarks
- **Características**: Foco em tempo de execução e memória
- **Cobertura**: Large datasets, Concurrent operations

### End-to-End Tests
- **Objetivo**: Testar fluxos completos de negócio
- **Características**: Cenários reais, múltiplos componentes
- **Cobertura**: Complete order lifecycle, Business workflows

## 🚀 Métricas de Qualidade

- **Total de Testes**: 368+ testes
- **Cobertura**: 90%+ mantida
- **Performance**: < 2s para suite completa
- **Categorias**: 4 tipos organizados (unit, integration, performance, e2e)

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

# Documentação da Estrutura de Testes

Este documento descreve a estrutura organizada de testes para o microserviço de acompanhamento.

## Estrutura de Diretórios

```
tests/
├── conftest.py                 # Fixtures compartilhados e configuração
├── unit/                       # Unit tests (isolados, rápidos)
│   ├── models/                 # Unit tests de models
│   │   ├── test_item_pedido.py
│   │   ├── test_evento_pedido.py
│   │   ├── test_evento_pagamento.py
│   │   ├── test_acompanhamento.py
│   │   └── test_evento_acompanhamento.py
│   └── schemas/                # Testes de validação de schemas
│       └── test_validation.py
├── integration/                # Integration tests (múltiplos componentes)
│   └── test_model_consistency.py
├── performance/                # Performance tests
│   └── test_model_performance.py
├── e2e/                       # End-to-end tests (fluxos completos)
│   └── test_full_workflow.py
└── legacy/                    # Arquivos de teste legados (podem ser removidos depois)
    ├── test_acompanhamento.py
    ├── test_models_advanced.py
    └── test_models_validation.py
```

## Categorias de Testes

### Unit Tests (`tests/unit/`)

-   **Propósito**: Testar componentes individuais isoladamente
-   **Velocidade**: Rápido (< 0,1s por teste)
-   **Cobertura**: Validação individual de models, serialização, lógica básica
-   **Exemplos**: Validação de campos, criação de models, serialização

### Integration Tests (`tests/integration/`)

-   **Propósito**: Testar interação entre múltiplos componentes
-   **Velocidade**: Médio (0,1-1s por teste)
-   **Cobertura**: Consistência de models, validação de regras de negócio, fluxo de eventos
-   **Exemplos**: Transições de estado de pedido, consistência pagamento-pedido

### Performance Tests (`tests/performance/`)

-   **Propósito**: Testar características de performance
-   **Velocidade**: Variável (pode ser mais lento)
-   **Cobertura**: Large datasets, uso de memória, velocidade de serialização
-   **Exemplos**: 1000+ itens, bulk operations, eficiência de memória

### End-to-End Tests (`tests/e2e/`)

-   **Propósito**: Testar fluxos de negócio completos
-   **Velocidade**: Mais lento (1-5s por teste)
-   **Cobertura**: Ciclo de vida completo do pedido, cenários do mundo real
-   **Exemplos**: Criação de pedido → pagamento → preparação → entrega

## Executando Testes

### Executar Todos os Testes

```bash
pytest tests/
```

### Executar por Categoria

```bash
# Apenas unit tests
pytest tests/unit/

# Apenas integration tests
pytest tests/integration/

# Apenas performance tests
pytest tests/performance/

# Apenas end-to-end tests
pytest tests/e2e/
```

### Executar por Model

```bash
# Todos os testes de ItemPedido
pytest tests/unit/models/test_item_pedido.py

# Todos os testes de EventoPedido
pytest tests/unit/models/test_evento_pedido.py
```

### Executar com Markers

```bash
# Apenas performance tests
pytest -m performance

# Apenas unit tests
pytest -m unit
```

### Executar com Saída Verbosa

```bash
pytest tests/ -v
```

### Executar com Coverage (se configurado)

```bash
pytest tests/ --cov=app/models/
```

## Convenções de Nomenclatura de Testes

### Nomes de Arquivos

-   `test_{nome_model}.py` para testes específicos de models
-   `test_{funcionalidade}.py` para testes específicos de funcionalidades

### Nomes de Classes

-   `Test{NomeModel}` para classes de teste de models
-   `Test{Funcionalidade}` para classes de teste de funcionalidades

### Nomes de Métodos

-   `test_{o_que_esta_sendo_testado}` com nomes descritivos
-   Exemplos: `test_create_valid_item_pedido`, `test_invalid_cpf_format`

## Fixtures Compartilhados

Localizados em `conftest.py`:

-   `sample_datetime`: Datetime consistente para todos os testes
-   `sample_itens`: Lista padrão de ItemPedido para testes
-   `sample_cpf`: CPF válido para testes
-   `sample_id_pedido`: ID de pedido padrão para testes

## Melhores Práticas

1. **Manter unit tests rápidos**: Sem dependências externas, sem I/O
2. **Usar nomes de teste descritivos**: Devem explicar o que está sendo testado
3. **Usar fixtures para dados comuns**: Evitar repetir setup de dados de teste
4. **Agrupar testes relacionados**: Usar classes de teste para agrupar funcionalidades relacionadas
5. **Testar casos extremos**: Incluir valores limite, casos nulos, dados inválidos
6. **Manter independência de testes**: Cada teste deve poder rodar isoladamente

## Diretrizes de Performance

-   Unit tests: < 0,1s cada
-   Integration tests: < 1s cada
-   Performance tests: < 5s cada (exceto quando testando operações longas especificamente)
-   End-to-end tests: < 10s cada

## Metas de Coverage

-   **Unit tests**: 95%+ coverage da lógica de models
-   **Integration tests**: Cobrir todas as interações de models
-   **Performance tests**: Cobrir preocupações de escalabilidade
-   **End-to-end tests**: Cobrir todos os fluxos de negócio críticos

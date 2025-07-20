# 🚀 Pipeline CI/CD

Este projeto inclui um pipeline CI/CD abrangente usando GitHub Actions com múltiplos workflows.

## 📋 Workflows Disponíveis

### 1. **Pipeline Principal CI/CD** (`.github/workflows/ci.yml`)

- **Gatilhos**: Push para `main`/`develop`, Pull Requests
- **Funcionalidades**:
  - ✅ Testes em múltiplas versões do Python (3.11, 3.12)
  - ✅ Cache de dependências com Poetry
  - ✅ Suite de testes abrangente (unit, integration, performance, e2e)
  - ✅ Relatório de cobertura de código
  - ✅ Escaneamento de segurança
  - ✅ Build da imagem Docker
  - ✅ Validação de quality gate

### 2. **Workflow de Testes** (`.github/workflows/test.yml`)

- **Gatilhos**: Eventos de push e PR
- **Funcionalidades**:
  - ✅ Execução organizada de testes por categoria
  - ✅ Validação do test runner customizado
  - ✅ Verificações de qualidade de código (black, ruff, mypy)
  - ✅ Artefatos de relatórios de cobertura

### 3. **Verificação de Pull Request** (`.github/workflows/pr-check.yml`)

- **Gatilhos**: Apenas Pull Requests
- **Funcionalidades**:
  - ✅ Testes de validação rápidos
  - ✅ Validação de regras de negócio
  - ✅ Teste de importação de models
  - ✅ Relatórios de resumo do PR

### 4. **Deploy** (`.github/workflows/deploy.yml`)

- **Gatilhos**: Push para `main`, dispatch manual
- **Funcionalidades**:
  - ✅ Proteção do ambiente de produção
  - ✅ Suite completa de testes antes do deploy
  - ✅ Build e teste da imagem Docker
  - ✅ Escaneamento de vulnerabilidades de segurança

### 5. **Badge de Cobertura** (`.github/workflows/badge.yml`)

- **Gatilhos**: Eventos de push e PR
- **Funcionalidades**:
  - ✅ Geração automática de badge de cobertura
  - ✅ Atualizações de badge no README

## 📊 Métricas de Qualidade

- **Cobertura de Testes**: 90%+ mantida automaticamente
- **Validação de Regras de Negócio**: ✅ Aplicada
- **Suporte Multi-Python**: 3.11, 3.12
- **Escaneamento de Segurança**: Scanner de vulnerabilidades Trivy
- **Qualidade de Código**: Verificações opcionais de linting e formatação

## 🏷️ Status Badges

![CI/CD Pipeline](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/ci.yml/badge.svg)
![Tests](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/test.yml/badge.svg)
![Coverage](coverage.svg)

## 🛡️ Segurança e Qualidade

- **Escaneamento Automático de Segurança**: Scanner de vulnerabilidades Trivy
- **Segurança de Dependências**: Verificações Safety para vulnerabilidades conhecidas
- **Qualidade de Código**: Linting opcional com ruff e formatação com black
- **Verificação de Tipos**: Type checking opcional com mypy
- **Quality Gates**: Previnem merge se os testes falharem

## 🚀 Processo de Deploy

1. **Desenvolvimento**: Trabalhar na branch `develop`
2. **Pull Request**: Validação automática do PR executada
3. **Code Review**: Processo de revisão manual
4. **Merge para Main**: Aciona o pipeline CI/CD completo
5. **Deploy**: Imagem Docker construída e pronta para produção

O pipeline garante alta qualidade de código e previne regressões através de testes automatizados abrangentes.

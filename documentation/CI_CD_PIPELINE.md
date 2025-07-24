# 🚀 Pipeline CI/CD

Este projeto inclui um pipeline CI/CD abrangente usando GitHub Actions com múltiplos workflows.

## 📋 Workflows Disponíveis

### 1. **Pipeline Principal CI/CD** (`.github/workflows/ci.yml`)

-   **Gatilhos**: Push para `main`/`develop`, Pull Requests
-   **Funcionalidades**:
    -   ✅ Testes em múltiplas versões do Python (3.11, 3.12)
    -   ✅ Cache de dependências com Poetry
    -   ✅ Suite de testes abrangente (unit, integration, performance, e2e, bdd) ✅ ATUALIZADO
    -   ✅ Relatório de cobertura de código
    -   ✅ Escaneamento de segurança
    -   ✅ Análise de qualidade com SonarCloud ✅ NOVO
    -   ✅ Build da imagem Docker
    -   ✅ Validação de quality gate

### 2. **Workflow de Testes** (`.github/workflows/test.yml`)

-   **Gatilhos**: Eventos de push e PR
-   **Funcionalidades**:
    -   ✅ Execução organizada de testes por categoria
    -   ✅ Validação do test runner customizado
    -   ✅ Verificações de qualidade de código (black, ruff, mypy)
    -   ✅ Artefatos de relatórios de cobertura

### 3. **Verificação de Pull Request** (`.github/workflows/pr-check.yml`)

-   **Gatilhos**: Apenas Pull Requests
-   **Funcionalidades**:
    -   ✅ Testes de validação rápidos
    -   ✅ Validação de regras de negócio
    -   ✅ Teste de importação de models
    -   ✅ Relatórios de resumo do PR

### 4. **Deploy** (`.github/workflows/deploy.yml`)

-   **Gatilhos**: Push para `main`, dispatch manual
-   **Funcionalidades**:
    -   ✅ Proteção do ambiente de produção
    -   ✅ Suite completa de testes antes do deploy
    -   ✅ Build e teste da imagem Docker
    -   ✅ Escaneamento de vulnerabilidades de segurança

### 5. **Badge de Cobertura** (`.github/workflows/badge.yml`)

-   **Gatilhos**: Eventos de push e PR
-   **Funcionalidades**:
    -   ✅ Geração automática de badge de cobertura
    -   ✅ Atualizações de badge no README

### 6. **SonarCloud Analysis** (Job no Pipeline Principal) ✅ NOVO

-   **Integração**: Job `sonarcloud` executado após os testes passarem
-   **Gatilhos**: Push para `main`/`develop`, Pull Requests
-   **Funcionalidades**:
    -   ✅ Análise automática de qualidade de código
    -   ✅ Escaneamento de segurança (OWASP Top 10)
    -   ✅ Relatórios de cobertura integrados
    -   ✅ Detecção de code smells e vulnerabilidades
    -   ✅ Quality Gate automático
    -   ✅ Métricas de maintainability, reliability e security
    -   ✅ Dashboards profissionais no SonarCloud.io

## 📊 Métricas de Qualidade

-   **Cobertura de Testes**: 91% atual (90%+ mantida automaticamente) ✅ ATUALIZADO
-   **Total de Testes**: 428 testes (unit, integration, performance, e2e, bdd) ✅ ATUALIZADO
-   **Validação de Regras de Negócio**: ✅ Aplicada
-   **Suporte Multi-Python**: 3.11, 3.12
-   **Escaneamento de Segurança**: Scanner de vulnerabilidades Trivy
-   **Qualidade de Código**: Verificações opcionais de linting e formatação
-   **SonarCloud Metrics** ✅ NOVO:
    -   **Maintainability Rating**: A (atual)
    -   **Reliability Rating**: A (atual)
    -   **Security Rating**: A (atual)
    -   **Duplicated Lines**: < 3%
    -   **Technical Debt**: Monitoramento automático

## 🏷️ Status Badges

![CI/CD Pipeline](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/ci.yml/badge.svg)
![Tests](https://github.com/ju-c-lopes/microservico-acompanhamento/actions/workflows/test.yml/badge.svg)
![Coverage](coverage.svg)
![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ju-c-lopes_microservico-acompanhamento&metric=alert_status) ✅ NOVO
![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ju-c-lopes_microservico-acompanhamento&metric=sqale_rating) ✅ NOVO
![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ju-c-lopes_microservico-acompanhamento&metric=security_rating) ✅ NOVO

## 🛡️ Segurança e Qualidade

-   **Escaneamento Automático de Segurança**: Scanner de vulnerabilidades Trivy
-   **Segurança de Dependências**: Verificações Safety para vulnerabilidades conhecidas
-   **Qualidade de Código**: Linting opcional com ruff e formatação com black
-   **Verificação de Tipos**: Type checking opcional com mypy
-   **Quality Gates**: Previnem merge se os testes falharem
-   **SonarCloud Integration** ✅ NOVO:
    -   **Análise Contínua**: Qualidade, segurança e cobertura automáticas
    -   **Security Hotspots**: Detecção de vulnerabilidades OWASP Top 10
    -   **Code Smells**: Identificação automática de problemas de manutenibilidade
    -   **Technical Debt**: Métricas de dívida técnica e estimativas de correção
    -   **Pull Request Decoration**: Comentários automáticos em PRs com issues
    -   **Quality Gate**: Critérios rigorosos de qualidade que bloqueiam merges problemáticos

## 🚀 Processo de Deploy

1. **Desenvolvimento**: Trabalhar na branch `develop`
2. **Pull Request**: Validação automática do PR executada
3. **Análise SonarCloud**: Quality gate e análise de segurança ✅ NOVO
4. **Code Review**: Processo de revisão manual
5. **Merge para Main**: Aciona o pipeline CI/CD completo
6. **Deploy**: Imagem Docker construída e pronta para produção

## ⚙️ Configuração SonarCloud ✅ NOVO

### **Arquivos de Configuração:**

-   **`sonar-project.properties`**: Configuração do projeto SonarCloud
-   **`documentation/SONARCLOUD_SETUP.md`**: Guia completo de configuração

### **Integração GitHub Actions:**

```yaml
# Job no .github/workflows/ci.yml
sonarcloud:
    name: SonarCloud Analysis
    runs-on: ubuntu-latest
    needs: test
    steps:
        - uses: actions/checkout@v4
        - name: SonarCloud Scan
          uses: SonarSource/sonarcloud-github-action@master
```

### **Métricas Monitoradas:**

-   **Quality Gate**: Pass/Fail automático
-   **Coverage**: Integração com pytest-cov (91% atual)
-   **Security**: Vulnerabilidades e hotspots
-   **Maintainability**: Code smells e technical debt
-   **Reliability**: Bugs e issues de confiabilidade

### **Tech Challenge Compliance:**

✅ **Requisito SonarQube atendido** via SonarCloud (versão cloud enterprise do SonarQube)

O pipeline garante alta qualidade de código e previne regressões através de testes automatizados abrangentes e análise contínua de qualidade com SonarCloud.

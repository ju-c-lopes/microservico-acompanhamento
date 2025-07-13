## Fase 4 Tech Challenge
---

Primeiro esboço de estrutura

```bash
acompanhamento/
├── app
│   ├── api
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── acompanhamento.py
│   │       └── __init__.py
│   ├── core
│   │   ├── config.py
│   │   ├── __init__.py
│   │   └── kafka.py
│   ├── db
│   │   ├── base.py
│   │   └── __init__.py
│   ├── domain
│   │   ├── acompanhamento_service.py
│   │   ├── __init__.py
│   │   └── order_state.py
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   ├── acompanhamento.py
│   │   ├── events.py
│   │   └── __init__.py
│   └── repository
│       ├── acompanhamento_repository.py
│       └── __init__.py
├── Dockerfile
├── README.md
└── tests
    ├── __init__.py
    └── test_acompanhamento.py

10 directories, 23 files
```

# Integração com AWS SQS – Microserviço de Acompanhamento

## Visão Geral

Este documento explica como o microserviço de acompanhamento integra-se com o AWS SQS para consumir e produzir eventos, seguindo o padrão Clean Architecture adotado no projeto.

---

## 1. Arquitetura da Integração SQS

-   O microserviço **não depende de HTTP** para integração entre sistemas.
-   Toda comunicação de eventos é feita via **filas SQS**.
-   O serviço **consome** eventos das filas:
    -   `pedido-events`
    -   `pagamento-events`
    -   `produto-events`
-   O serviço **envia** eventos para a fila:
    -   `acompanhamento-events`

---

## 2. Componentes Envolvidos

-   **worker/sqs_consumer.py**: Worker assíncrono que escuta as filas SQS e processa eventos.
-   **core/sqs_client.py**: Cliente SQS centralizado para enviar/receber/deletar mensagens.
-   **adapters/event_adapter.py**: Funções para adaptar o formato dos eventos recebidos para o padrão do domínio.
-   **domain/acompanhamento_service.py**: Serviço de domínio que processa os eventos já validados.
-   **models/**: Modelos Pydantic para validação dos eventos.

---

## 3. Fluxo de Consumo de Eventos

1. O worker conecta nas filas SQS configuradas.
2. Recebe mensagens (eventos) de cada fila.
3. Usa um adaptador para transformar o evento no formato esperado pelo domínio.
4. Valida o evento com Pydantic.
5. Chama o service (`AcompanhamentoService`) para processar o evento.
6. Se o processamento for bem-sucedido, deleta a mensagem da fila.

---

## 4. Fluxo de Produção de Eventos

-   Quando necessário, o microserviço pode enviar eventos para a fila `acompanhamento-events` usando o cliente SQS centralizado.
-   O evento deve ser serializado no formato esperado pelos consumidores.

---

## 5. Exemplo de Uso (Consumo)

```python
async def consumir_fila(queue_url, adaptador):
    sqs = get_sqs_client()
    service = AcompanhamentoService()
    while True:
        messages = await sqs.receive_messages(queue_url)
        for msg in messages:
            evento = adaptador(msg["Body"])
            await service.processar_evento(evento)
            await sqs.delete_message(queue_url, msg["ReceiptHandle"])
        await asyncio.sleep(1)
```

---

## 6. Observações Importantes

-   O worker pode rodar em paralelo ao FastAPI (API HTTP), mas não depende dele para funcionar.
-   O processamento é assíncrono e desacoplado: o evento chega, é processado, e só depois aparece no banco.
-   Se o banco estiver fora, o worker pode tentar de novo (mensagem volta para a fila).
-   Adaptadores são fundamentais para garantir que o domínio receba os dados no formato correto.

---

## 7. Como Rodar o Worker SQS

O worker é responsável por escutar as filas SQS configuradas e processar os eventos recebidos, chamando o domínio do microserviço.

### Passos para rodar o worker:

1. **Configure as variáveis de ambiente** necessárias (exemplo: `PEDIDO_QUEUE_URL`, `PAGAMENTO_QUEUE_URL`, `PRODUTO_QUEUE_URL`, além das credenciais AWS).
2. **Execute o worker** com o comando:
    ```bash
    poetry run python app/worker/sqs_consumer.py
    ```
3. O worker ficará rodando em background, escutando as filas e processando eventos automaticamente.

> **Dica:** Você pode rodar o worker em paralelo à API FastAPI, em outro terminal ou container.

---

## 8. Como Enviar Eventos para o SQS

-   Use o cliente SQS centralizado (`core/sqs_client.py`) para enviar eventos para a fila `acompanhamento-events`.
-   Exemplo:
    ```python
    await sqs.send_message(queue_url, evento_serializado)
    ```

---

## 9. Dúvidas Frequentes

-   **Preciso adaptar o evento?**
    Sim, sempre adapte o evento recebido para o formato do domínio antes de processar.
-   **E se o evento vier com campos diferentes?**
    Use/adapte as funções em `adapters/event_adapter.py` para garantir compatibilidade.
-   **O que acontece se der erro no processamento?**
    A mensagem volta para a fila após o tempo de visibilidade e será reprocessada.

---

## 10. Referências

-   [Documentação AWS SQS](https://docs.aws.amazon.com/pt_br/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
-   [aioboto3 (async SQS client)](https://aioboto3.readthedocs.io/en/latest/)

---

**Dúvidas? Consulte este arquivo ou procure a equipe de arquitetura!**

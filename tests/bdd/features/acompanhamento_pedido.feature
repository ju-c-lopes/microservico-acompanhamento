Feature: Acompanhamento de Pedidos
  Como um cliente da lanchonete
  Eu quero acompanhar meu pedido em tempo real
  Para saber quando estará pronto para retirada

  Background:
    Given que o sistema de acompanhamento está funcionando
    And existem produtos disponíveis no cardápio

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
    And o cliente deve ser notificado
    When o cliente retira o pedido
    Then o status deve ser atualizado para "Finalizado"

  Scenario: Consulta de fila de pedidos pela cozinha
    Given que existem "3" pedidos na fila
    And os pedidos estão com status "Recebido" e "Em preparação"
    When a cozinha consulta a fila de pedidos
    Then deve receber a lista ordenada por tempo de criação
    And cada pedido deve conter as informações necessárias para preparo

  Scenario: Cálculo de tempo estimado baseado nos itens
    Given que um pedido contém "2" lanches
    And o pedido contém "1" acompanhamento
    And o pedido contém "1" bebida
    When o sistema calcula o tempo estimado
    Then deve considerar o tempo de preparo de cada categoria
    And retornar o tempo total em formato "XX min"

  Scenario: Atualização de status com validação de transição
    Given que um pedido está com status "Recebido"
    When tento atualizar diretamente para "Finalizado"
    Then deve retornar erro de transição inválida
    And o status deve permanecer "Recebido"
    When atualizo para "Em preparação"
    Then a atualização deve ser bem-sucedida

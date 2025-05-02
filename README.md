# Projeto de Processamento de Assets

## Visão Geral
Este projeto é responsável pelo processamento e gerenciamento de assets (ativos) através de uma arquitetura serverless na AWS. O sistema processa eventos de metadados de tabelas de bancos de dados e determina se devem ser tratados como operações de upsert ou drop.

## Arquitetura do Sistema

### Componentes Principais

1. **Asset Input Data Stream**
   - Recebe dados de agentes externos
   - Formato: Stream de dados de entrada para processamento inicial

2. **Event Decisor (Lambda)**
   - Processa eventos recebidos
   - Determina o tipo de operação (upsert ou drop)
   - Gerencia o estado dos assets no DynamoDB

3. **Event Content Bucket (S3)**
   - Armazena conteúdo relacionado aos eventos
   - Mantém histórico de mudanças

4. **Filas SQS**
   - `upsert-queue`: Fila para operações de inserção/atualização
   - `upsert-queue-dlq`: Fila de dead letter para retry de operações de upsert
   - `drop-queue`: Fila para operações de remoção
   - `drop-queue-dlq`: Fila de dead letter para retry de operações de drop

5. **Asset Control Table (DynamoDB)**
   - Armazena metadados dos assets
   - Controla estado e histórico de processamento

6. **Lambdas de Processamento**
   - `upsert-asset-event-producer`: Processa eventos de upsert
   - `drop-asset-event-producer`: Processa eventos de drop

### Fluxo de Dados

1. Dados entram através do Asset Input Data Stream
2. Event Decisor Lambda processa e categoriza os eventos
3. Eventos são direcionados para filas específicas (upsert ou drop)
4. Producers processam os eventos e atualizam o estado no DynamoDB
5. Resultados são armazenados no Event Content Bucket

## Estrutura do Código

```
.
├── src/
│   ├── modules/                           # Módulos do projeto
│   │   ├── lambda_event_decisor/         # Lambda de decisão de eventos
│   │   ├── lambda_upsert_asset_event_producer/  # Lambda producer de eventos upsert
│   │   ├── lambda_drop_asset_event_producer/    # Lambda producer de eventos drop
│   │   ├── lambda_redrive/               # Lambda para reprocessamento
│   │   ├── shared/                       # Código compartilhado entre módulos
│   │   └── lambdas/                      # Definições base das lambdas
│   └── handler.py                        # Handler principal
│
├── tests/                                # Testes automatizados
├── requirements.txt                      # Dependências do projeto
├── pytest.ini                           # Configuração de testes
└── conftest.py                          # Configurações de teste compartilhadas
```

## Responsabilidades dos Módulos

### Lambda Event Decisor
- Processa eventos de entrada
- Determina se um evento deve gerar upsert ou drop
- Gerencia o estado dos assets no DynamoDB

### Lambda Upsert Asset Event Producer
- Gera eventos de upsert para assets
- Processa atualizações e inserções
- Envia eventos para filas específicas

### Lambda Drop Asset Event Producer
- Gera eventos de drop para assets
- Processa remoções de assets
- Gerencia o ciclo de vida dos assets

### Lambda Redrive
- Reprocessa eventos que falharam
- Gerencia tentativas de reprocessamento
- Trata eventos das DLQs

### Shared
- Código compartilhado entre módulos
- Utilitários comuns
- Interfaces e tipos compartilhados

### Lambdas Base
- Definições base para as lambdas
- Configurações compartilhadas
- Estruturas comuns

## Configuração e Variáveis de Ambiente

### Variáveis Obrigatórias
- `DYNAMODB_TABLE_NAME`: Nome da tabela do DynamoDB
- `UPSERT_QUEUE_URL`: URL da fila SQS para eventos de upsert
- `DROP_QUEUE_URL`: URL da fila SQS para eventos de drop

## Processamento de Eventos

### Eventos de Status "Running"
1. Verifica existência do asset no DynamoDB
2. Compara hashes para detectar mudanças
3. Gera eventos de upsert quando necessário
4. Atualiza timestamps de processamento

### Eventos de Status "Completed"
1. Identifica assets candidatos para drop
2. Gera eventos de drop quando apropriado
3. Atualiza estado no DynamoDB

## Instalação e Desenvolvimento

### Requisitos
- Python 3.11
- AWS CLI configurado
- Acesso aos serviços AWS necessários

### Setup do Ambiente
```bash
pip install -r requirements.txt
```

### Testes
```bash
pytest tests/
```

## Monitoramento e Logs

- CloudWatch Logs para todas as Lambdas
- Métricas de SQS para filas
- Alarmes CloudWatch para erros e latência
- DLQs para tratamento de falhas 

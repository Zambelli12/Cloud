# Cloud
Sistema de Análise de Dados - Monitoramento de Estoque

Descrição Geral

Este projeto consiste em um sistema de Monitoramento Inteligente de Estoque. O problema analisado é a dificuldade de prever rupturas de estoque em cenários de vendas variáveis. O objetivo do sistema é utilizar algoritmos de Inteligência Artificial (SARIMAX) para analisar o histórico de vendas de produtos e calcular automaticamente um ponto de reposição (limite mínimo) dinâmico, alertando gestores via dashboard web.

Dataset

Fonte dos dados: Dados sintéticos gerados via script proprietário (seed_data.py) para simulação de cenário de varejo.

Volume de dados esperado: Histórico diário de vendas para 20 produtos, totalizando aproximadamente 14.000 registros iniciais (simulação de 2 anos).

Licenciamento do dataset: Open Source (Gerado para fins acadêmicos).

Arquitetura da Solução

A solução segue o padrão de microsserviços:

graph TD;
    User[Usuário] -->|HTTP/Port 5000| WebApp[Container: Dashboard Web (Flask)];
    
    subgraph "Docker / Azure Cloud Environment"
        WebApp -->|Leitura SQL| DB[(Azure Database for MySQL)];
        Worker[Container: Processamento IA (Python)] -->|Leitura e Escrita| DB;
    end

    style DB fill:#0078d4,stroke:#333,stroke-width:2px,color:white;
    style Worker fill:#d9534f,stroke:#333,stroke-width:2px,color:white;
    style WebApp fill:#5cb85c,stroke:#333,stroke-width:2px,color:white;


Demonstração

Capturas de tela do dashboard

<img width="1550" height="791" alt="image" src="https://github.com/user-attachments/assets/02c4ab37-a511-4bb8-bcf1-c1bfb9193559" />

Link para vídeo de demo

-VIDEO-

Referências

Docker Docs: https://docs.docker.com/

Azure Database for MySQL: https://learn.microsoft.com/en-us/azure/mysql/

Statsmodels (SARIMAX): https://www.statsmodels.org/dev/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html

Flask Framework: https://flask.palletsprojects.com/

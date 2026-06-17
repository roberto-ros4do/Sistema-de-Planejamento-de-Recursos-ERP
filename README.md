# ERP de Controle de Estoque e Movimentações

Este ERP de Controle de Estoque e Movimentações é um sistema desenvolvido em Python com o objetivo de auxiliar no gerenciamento de produtos, estoque, saldo financeiro e movimentações empresariais.

O projeto foi criado como trabalho acadêmico e vem sendo expandido continuamente para simular funcionalidades encontradas em sistemas ERP reais. Atualmente, o sistema opera via terminal e utiliza banco de dados SQLite para persistência de dados.

## Tecnologias utilizadas
Python 3
SQLite3
Pandas
CSV
Datetime

## Funcionalidades
### Gestão de Produtos
Cadastro de produtos
Registro de:
Nome
Quantidade em estoque
Preço de venda
Especificações
Controle de investimento inicial
Exclusão de produtos
#### Controle de Estoque
Atualização automática de estoque através das movimentações
Consulta de produtos cadastrados
Filtros por:
Nome
Quantidade
Valor
### Controle Financeiro
Registro de saldo disponível
Aplicação de recursos
Retirada de recursos
Desconto automático de investimentos realizados no cadastro de produtos
### Movimentações

Registro de:

Compras
Vendas
Devoluções
Perdas
Transferências

Cada movimentação possui:

Produto relacionado
Quantidade
Data
Horário

### Histórico
Histórico de cadastro de produt
Histórico de movimentações
Filtragem por período:
Última semana
Último mês
Intervalo personalizado de datas

###Relatórios
Exportação de relatórios em formato CSV
Relatório de produtos
Relatório de movimentações filtradas por período

## Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

Python 3.10 ou superior
Pip
Bibliotecas necessárias

Instale as dependências utilizando:

```bash
pip install pandas
```
As demais bibliotecas utilizadas (sqlite3, datetime e csv) fazem parte da biblioteca padrão do Python.

## Instalação
Clone o repositório:
```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
```
Acesse a pasta do projeto:
```bash
cd nome-do-repositorio
```

## Como Utilizar

Ao iniciar o sistema, será exibido um menu principal:
```bash
[1] CADASTRAR PRODUTOS
[2] LISTAGEM DE PRODUTOS
[3] HISTÓRICO DE CADASTRO
[4] REGISTRAR MOVIMENTAÇÃO
[5] HISTÓRICO DE MOVIMENTAÇÕES
[6] EXPORTAR RELATÓRIO CSV
[7] DELETAR PRODUTO
[8] EDITAR SALDO
[9] SAIR DO SISTEMA
Cadastro de Produtos
```

**Permite registrar novos produtos informando:**

Nome
Quantidade inicial
Valor de venda
Especificações
Valor investido
Registro de Movimentações

**Permite controlar entradas e saídas do estoque:**

Entradas
Compra
Devolução
Saídas
Venda
Perda
Transferência

**Histórico de Cadastros:**
Consulta todos os produtos cadastrados com data e horário de registro.

**Histórico de Movimentações:**
Permite consultar movimentações registradas e filtrá-las por período.

**Exportação CSV:**
Gera relatórios que podem ser abertos em:

Microsoft Excel
LibreOffice Calc
Google Sheets

## Próximas Implementações
Sistema de Login
Interface gráfica
Relatório gerencial
Alertas inteligentes de estoque
API REST
Dashboard de indicadores
Testes automatizados

Desenvolvido por [Seu Nome] como projeto de estudo e trabalho acadêmico, com foco na evolução contínua das habilidades em desenvolvimento de software, banco de dados e arquitetura de sistemas.

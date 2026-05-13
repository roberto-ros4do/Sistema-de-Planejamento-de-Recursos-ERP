<<<<<<< HEAD
# ERP CRUD Console em Python

Sistema simples de Planejamento de Recursos Empresariais (ERP) CRUD desenvolvido em Python no terminal, com foco em:
=======
# ERP Console em Python

Sistema simples de Planejamento de Recursos Empresariais (ERP) desenvolvido em Python no terminal, com foco em:
>>>>>>> 40566f7f0dc65e279679e1d0afe22ec733036f5f

* controle de estoque
* movimentações de produtos
* controle financeiro
* persistência de dados
* aprendizado de SQL e SQLite

---

# Objetivo do Projeto

Este projeto foi criado com fins de estudo e evolução prática em:

* Python
* Modularização
* Banco de dados SQLite
* Operações SQL

O sistema começou utilizando armazenamento em JSON e posteriormente foi migrado para SQLite para melhorar persistência, organização e escalabilidade dos dados.

---

# Funcionalidades

## Cadastro de Produtos

* nome
* quantidade em estoque
* preço
* especificações

---

## Movimentações

### Entradas

* compra
* devolução

### Saídas

* venda
* perda
* transferência

---

## Controle Financeiro

* saldo da empresa
* aplicações
* retiradas
* atualização automática após movimentações

---

## Relatórios

* listagem de produtos
* histórico de movimentações

# Tecnologias Utilizadas

* Python 3
* SQLite3

---

# Conceitos Aplicados

## Python

* funções
* modularização
* loops
* tratamento de exceções
* listas e dicionários
* persistência de dados

---

## SQLite

* CREATE TABLE
* INSERT
* SELECT
* UPDATE
* fetchone()
* fetchall()
* commit()
* banco relacional

---

# Evolução do Projeto

## Versão 1 — JSON

A primeira versão utilizava:

```python
json.load()
json.dump()
```

Os dados eram armazenados em arquivos `.json`.

Essa etapa foi importante para entender persistência de dados e estruturação do sistema.

---

## Versão 2 — SQLite

O projeto foi refatorado para utilizar SQLite.

Melhorias obtidas:

* persistência relacional
* manipulação mais segura dos dados
* melhor escalabilidade
* uso real de banco de dados
* aprendizado de SQL aplicado na prática

---

# Como Executar

## Clone o repositório

```bash
git clone <url-do-repositorio>
```

---

## Execute o projeto

```bash
python main.py
```

---

# Melhorias Futuras

* autenticação de usuários
* relatórios gerenciais
* interface gráfica
<<<<<<< HEAD
* Integração web com Flask
=======
* integração web

---
>>>>>>> 40566f7f0dc65e279679e1d0afe22ec733036f5f

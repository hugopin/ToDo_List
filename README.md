# ToDo List

Projeto de lista de tarefas desenvolvido na especialização da UFG.

## Instalação

As instruções abaixo usam Windows com PowerShell. O projeto foi desenvolvido
e testado com Python 3.14.7. É necessário ter Python e Git instalados.

1. Clone o repositório e entre na pasta:

   ```powershell
   git clone https://github.com/hugopin/ToDo_List.git
   cd ToDo_List
   ```

2. Crie e ative o ambiente virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instale as dependências com o ambiente virtual ativo:

   ```powershell
   python -m pip install -r requirements.txt
   ```

O SQLite é acessado pelo módulo `sqlite3`, incluído no Python; não é necessário
instalar um servidor de banco de dados.

## Execução

Na raiz do projeto, com o ambiente virtual ativo, inicie o servidor:

```powershell
python -m uvicorn app.main:app --reload
```

Após a mensagem `Application startup complete`, acesse a
[documentação interativa](http://127.0.0.1:8000/docs) no navegador para experimentar
as operações. O servidor atende localmente em `http://127.0.0.1:8000`.

O arquivo `tasks.db` e sua tabela são criados automaticamente na primeira
inicialização. As tarefas permanecem salvas após reiniciar o servidor, desde que
esse arquivo seja mantido.

Para encerrar o servidor, pressione `Ctrl+C` no terminal. Em uma nova sessão,
ative novamente a `.venv` antes de executar o comando do servidor.

## Endpoints e exemplos de uso

Com o servidor iniciado, abra `/docs`, expanda uma operação, clique em
**Try it out**, preencha os dados e clique em **Execute**.

| Método | Endereço | Operação | Código de sucesso |
|---|---|---|---|
| POST | `/tasks` | Criar uma tarefa pendente | 201 |
| GET | `/tasks` | Listar todas as tarefas | 200 |
| GET | `/tasks?completed=false` | Listar tarefas pendentes | 200 |
| GET | `/tasks?completed=true` | Listar tarefas concluídas | 200 |
| GET | `/tasks/{id}` | Consultar uma tarefa | 200 |
| PATCH | `/tasks/{id}` | Editar título, descrição ou conclusão | 200 |
| DELETE | `/tasks/{id}` | Excluir uma tarefa | 204 |

### Criar uma tarefa

Em `POST /tasks`, envie:

```json
{
  "title": "Estudar FastAPI",
  "description": "Acompanhar o miniprojeto da UFG"
}
```

Resposta de exemplo, com código 201:

```json
{
  "id": 1,
  "title": "Estudar FastAPI",
  "description": "Acompanhar o miniprojeto da UFG",
  "completed": false
}
```

O identificador é gerado automaticamente e pode variar. A descrição pode ser
omitida; nesse caso, será `null`. Títulos vazios ou contendo apenas espaços
são rejeitados com código 422.

### Listar e consultar

Em `GET /tasks`, deixe `completed` sem preencher para listar todas as tarefas,
ou selecione `false` para pendentes e `true` para concluídas. A resposta é uma
lista; quando não há resultados, retorna `[]` com código 200.

Em `GET /tasks/{id}`, informe o identificador recebido na criação. A resposta
contém uma única tarefa.

### Editar e alterar a conclusão

Em `PATCH /tasks/{id}`, informe o identificador e envie apenas os campos que
deseja alterar. Por exemplo, para editar o título:

```json
{
  "title": "Revisar FastAPI"
}
```

Para marcar como concluída:

```json
{
  "completed": true
}
```

Use `false` para voltar a pendente. Os campos omitidos mantêm seus valores.
Para remover a descrição, envie `{"description": null}`. Uma edição válida
retorna a tarefa atualizada com código 200; título vazio ou valor nulo para
`title` ou `completed` retorna 422.

### Excluir e consultar erros

Em `DELETE /tasks/{id}`, informe o identificador da tarefa que deseja remover.
Uma exclusão realizada retorna 204, sem corpo na resposta.

Consultar, editar ou excluir um identificador inexistente retorna 404:

```json
{
  "detail": "Tarefa não encontrada."
}
```

## Testes

Na raiz do projeto, com a `.venv` ativa e as dependências instaladas, execute:

```powershell
python -m pytest tests/test_tasks.py -v
```

O resultado esperado é `8 passed`. A opção `-v` mostra o nome e o resultado de
cada caso. Não é necessário iniciar o Uvicorn: os testes usam o `TestClient`
do FastAPI para enviar requisições diretamente à aplicação.

Os oito casos verificam:

- Criação com identificador gerado e situação inicial pendente.
- Rejeição de título vazio.
- Rejeição de título contendo apenas espaços.
- Consulta de tarefa inexistente com retorno 404.
- Edição parcial preservando os campos omitidos.
- Exclusão com retorno 204 e erros 404 nas tentativas posteriores.
- Listagem com filtros de pendentes e concluídas.
- Persistência entre encerramento e nova inicialização do ciclo de vida da aplicação.

Cada caso utiliza um banco SQLite em uma pasta temporária, separado do
`tasks.db` local. No teste de persistência, as duas inicializações usam o mesmo
banco temporário. Os testes ficam em `tests/test_tasks.py`.

## Arquitetura

A aplicação é uma API local em Python, com FastAPI e SQLite. As operações
podem ser experimentadas pela documentação interativa em `/docs`.

```mermaid
flowchart TD
    A["Documentação interativa — /docs"] -->|Requisição HTTP| B["FastAPI"]
    B --> C["Validação dos dados — schemas.py"]
    C --> D["Endpoints — main.py"]
    D --> E["Acesso aos dados — database.py"]
    E --> F[("SQLite — tasks.db")]
    F --> E
    E --> D
    D --> G["Modelo de resposta — schemas.py"]
    G -->|Resposta JSON| A
```

- `app/main.py`: inicializa o banco ao iniciar a aplicação e define os endpoints.
- `app/schemas.py`: define os modelos de entrada e saída e valida os dados recebidos.
- `app/database.py`: abre conexões e executa as operações SQL.
- `tasks.db`: guarda as tarefas entre execuções e fica fora do controle de versão.

O diagrama representa o fluxo de uma requisição válida. Dados inválidos recebem
uma resposta de erro antes de executar a operação no banco.

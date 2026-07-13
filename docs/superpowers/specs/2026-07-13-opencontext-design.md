# OpenContext Design

## Objetivo

Criar um projeto open source de portfólio chamado **OpenContext**, focado em recuperação de contexto para aplicações de IA explicáveis. O projeto será independente do GAV Insights e não conterá integrações, credenciais, dados ou regras de negócio específicas da GAV Resorts.

## Escopo aprovado

- Biblioteca Python para ingestão, chunking, embeddings, indexação e recuperação de documentos Markdown.
- API FastAPI para indexar documentos, pesquisar contexto e responder perguntas fundamentadas.
- UI React/Vite mínima para demonstrar busca, contexto recuperado, scores e citações.
- Corpus de exemplo neutro sobre product analytics, incluído no repositório.
- Integração opcional com um LLM via variável de ambiente; o modo retrieval-only funciona sem chave de API.
- Testes unitários do núcleo RAG e testes HTTP da API.
- Documentação de arquitetura, setup, fluxo de dados e decisões técnicas.
- Licença MIT e arquivos de configuração seguros para publicação.

## Fora de escopo

- Power BI, Fabric, PostgreSQL e MCPs filhos.
- Autenticação corporativa, Cosmos DB, sessões persistentes e feedback de usuários.
- Dados reais, nomes de relatórios, métricas ou documentos internos da GAV.
- Histórico Git do repositório original.
- Deploy obrigatório em nuvem.

## Arquitetura

```text
Markdown corpus
    -> Loader
    -> Chunker
    -> Embedding provider
    -> Local vector index
    -> Retriever
    -> FastAPI /search or /ask
    -> React/Vite demo
```

### Pacote `opencontext/`

- `config.py`: configurações por ambiente, com defaults locais seguros.
- `contracts.py`: modelos Pydantic para documentos, chunks, resultados e respostas.
- `loader.py`: leitura de Markdown e metadados opcionais.
- `chunker.py`: divisão por headings e tamanho máximo, preservando origem.
- `embeddings.py`: provider local determinístico para desenvolvimento e interface extensível para providers reais.
- `index.py`: persistência do índice local sem banco externo obrigatório.
- `retriever.py`: recuperação em dois estágios, retornando scores e trechos de origem.
- `service.py`: fachada para indexação e consulta, mantendo a API independente dos detalhes internos.

### API

- `GET /health`: estado da aplicação e do índice.
- `POST /documents/index`: indexa um diretório permitido de Markdown.
- `POST /search`: retorna chunks relevantes com origem, heading e score.
- `POST /ask`: monta uma resposta baseada apenas no contexto recuperado; usa LLM opcional quando configurado.

Erros de configuração, corpus vazio e ausência de contexto serão explícitos. A resposta de `/ask` sempre carregará as fontes recuperadas; quando não houver evidência suficiente, retornará uma mensagem de insuficiência em vez de inventar conteúdo.

### UI

A UI terá uma única experiência principal: pergunta, botão de busca/resposta, estado de carregamento, resposta, lista de fontes e trechos recuperados. O estado será local e a API base será configurável por `VITE_API_BASE_URL`.

## Tecnologia

- Python 3.11+
- FastAPI, Pydantic e Uvicorn
- Biblioteca de embeddings local opcional, com fallback leve para execução da demo
- React 18 e Vite
- Pytest
- Licença MIT

As dependências serão mantidas pequenas e documentadas. O projeto deverá iniciar e demonstrar busca sem exigir serviços externos.

## Higiene open source

- Criar `.env.example`, nunca copiar `.env`.
- Excluir arquivos de sessão, feedback, caches, bancos locais, artefatos de build e credenciais.
- Substituir documentos internos por exemplos sintéticos.
- Revisar referências textuais a GAV, Power BI, Fabric, clientes e ambientes corporativos.
- Incluir `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` e `SECURITY.md` curtos e adequados a um projeto público.
- Incluir README em português/inglês ou, no mínimo, README em inglês com uma seção de contexto em português.

## Critérios de aceitação

1. O novo diretório é um repositório Git independente chamado `OpenContext`.
2. A instalação local está documentada e reproduzível.
3. O corpus de exemplo pode ser indexado por comando ou endpoint.
4. Uma consulta retorna trechos com origem e score.
5. A API inicia sem credenciais externas e responde ao health check.
6. A UI inicia e consegue executar uma busca contra a API.
7. Os testes do núcleo e da API passam.
8. Busca por credenciais, dados reais e referências proprietárias não encontra material indevido.

## Decisões de portfólio

O projeto prioriza clareza arquitetural, demonstrabilidade e segurança de publicação. O nome `OpenContext` será usado em código, documentação, título da UI e metadados do pacote. A primeira versão não tentará reproduzir todo o produto original; ela apresentará o núcleo técnico que pode ser entendido e reutilizado por outras pessoas.

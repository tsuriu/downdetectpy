# 📡 Downdetector API

Um **web scraper baseado em FastAPI** que extrai dados de status e interrupções de serviços dos sites Downdetector, com uma interface de dashboard moderna.

---

## 🌟 Funcionalidades

- **Sistema de cache inteligente** - Limita requisições a uma vez a cada 10 minutos
- **Resiliência de Scraping** - Lida com desafios do Cloudflare e detecção de navegador
- **Fallback de Domínio** - Alterna automaticamente para `.com` se o domínio primário for bloqueado
- **Fallback de Cache** - Retorna cache antigo/expirado se o scraping falhar, garantindo disponibilidade
- **Scraping em tempo real** das páginas de status do Downdetector
- **Dados de séries temporais** para interrupções de serviços e tendências de performance
- **Estatísticas de problemas** e relatórios detalhados de interrupções
- **Suporte a múltiplos domínios** (`.com.br`, `.com`, `.co.uk`, etc.)
- **Métricas de performance** incluídas nas respostas da API
- **Diretório de empresas** com logos e visualizações sparkline
- **Dashboard moderno** com modo escuro/claro e atualizações em tempo real
- **Pronto para Docker** com proxy reverso Nginx e cache
- **Atualização automática** (intervalos de 10 minutos) com opção manual
- **Funcionalidade de busca** para filtrar empresas por nome
- **Ordenação por status** (fora do ar → problemas → operacional)

---

## 🚀 Começo Rápido

### 🐳 Docker (Recomendado)

1. **Clone e execute:**
   ```bash
   docker-compose up -d
   ```

2. **Acesse o dashboard:**
   - **Dashboard:** http://localhost:8089
   - **Documentação da API:** http://localhost:8089/docs (via documentação automática do FastAPI)

### 💻 Instalação Manual

1. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Execute o servidor FastAPI:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Acesse diretamente:**
   - **Servidor API:** http://localhost:8000
   - **Documentação da API:** http://localhost:8000/docs
   - **Esquema OpenAPI:** http://localhost:8000/openapi.json

---

## 📊 Funcionalidades do Dashboard

O dashboard incluído (`index.html`) fornece:

- **Layout de grid responsivo** (2 a 10 colunas baseado no tamanho da tela)
- **Indicadores de status em tempo real** com codificação por cores:
  - 🟢 **Verde**: Operacional (`success`)
  - 🟡 **Amarelo**: Problemas detectados (`warning`)
  - 🔴 **Vermelho**: Serviço fora do ar (`danger`)
  - ⚫ **Cinza**: Status desconhecido/neutro
- **Cartões interativos** mostrando logos das empresas e contagem média de relatos
- **Barra de busca** para filtragem rápida de empresas
- **Alternador de tema** (modo escuro/claro) com preferência persistente
- **Contagem regressiva para auto-atualização** (10 minutos) com botão de atualização manual
- **Barra de navegação recolhível** para mais espaço na tela
- **Resumo de status** no rodapé mostrando contagens operacional/problemas/fora do ar

---

## 📘 Endpoints da API

### 🔎 Obter Status do Serviço
**GET** `/api/status?company={nome_empresa}&domain={dominio}&timezone={fuso_horario}`

**Parâmetros de Consulta:**
| Nome       | Descrição                                                   | Padrão             | Obrigatório |
|------------|---------------------------------------------------------------|---------------------|----------|
| `company`  | Nome da empresa como aparece na URL do Downdetector         | –                   | Sim      |
| `domain`   | Domínio do Downdetector (ex: `com.br`, `com`, `co.uk`)      | `com.br`            | Não       |
| `timezone` | Fuso horário para timestamps (nome do banco de dados TZ)    | `America/Maceio`    | Não       |

**Exemplo:**
```bash
curl "http://localhost:8089/api/status?company=claro&domain=com.br"
```

---

### 🏢 Obter Lista de Empresas
**GET** `/api/companylist?domain={dominio}`

**Parâmetros de Consulta:**
| Nome     | Descrição                  | Padrão   | Obrigatório |
|----------|------------------------------|-----------|----------|
| `domain` | Domínio do Downdetector para consulta | `com.br`  | Não       |

**Exemplo:**
```bash
curl "http://localhost:8089/api/companylist"
```

---

## 🗄️ Endpoints de Gerenciamento de Cache

A API inclui um sistema de cache inteligente que limita as requisições aos servidores do Downdetector para uma vez a cada 10 minutos. Requisições subsequentes retornam dados cacheados.

### 📊 Informações do Cache
**GET** `/api/cache/info`
Retorna informações detalhadas sobre os dados cacheados incluindo tamanhos de arquivos, tempos de expiração e estatísticas do cache.

### 🗑️ Limpar Todo o Cache
**DELETE** `/api/cache/clear`
Limpa todos os dados cacheados, forçando a próxima requisição a buscar dados novos do Downdetector.

### ⏰ Limpar Cache Expirado
**DELETE** `/api/cache/clear/expired`
Limpa apenas as entradas de cache que expiraram, mantendo dados cacheados válidos.

---

## 📥 Exemplos de Respostas

### ✅ Resposta de Status do Serviço (com metadados de cache)
```json
{
  "time_series": [
    {
      "date": "2023-10-15 14:00:00",
      "reports_value": 42,
      "baseline_value": 12
    }
  ],
  "most_reported_problems": [
    {
      "name": "Conexão com servidor",
      "percentage": "42%"
    }
  ],
  "stats": {
    "max_reports": {
      "value": 120,
      "timestamp": "2023-10-15 15:30:00"
    },
    "average_reports": 45.67,
    "total_reports": 1096,
    "max_deviation": {
      "value": 108,
      "timestamp": "2023-10-15 15:30:00"
    },
    "spikes": ["2023-10-15 15:30:00"],
    "alerts_count": 8
  },
  "duration_seconds": 3.456,
  "company": "Claro",
  "domain": "com.br",
  "timezone": "America/Maceio",
  "cache_timestamp": "2023-12-11T10:30:00",
  "cache_expires_at": "2023-12-11T10:40:00",
  "from_cache": false,
  "cache_hit": false
}
```

---

### 🧾 Resposta da Lista de Empresas (com metadados de cache)
```json
{
  "duration_seconds": 5.123,
  "companies": [
    {
      "full_company_link": "https://downdetector.com.br/status/pix/",
      "company_name": "PIX",
      "logo_url": "https://downdetector.com.br/logo/pix.png",
      "svg_data": {
        "data_values": "[1,2,3...]",
        "data_min": "0.0",
        "data_max": "42.0",
        "data_mean": 12.5,
        "data_stddev": 8.2,
        "last_status": "success",
        "sparkline_color": "rgb(22, 160, 176)",
        "sparkline_color_hex": "#16a0b0"
      }
    }
  ],
  "domain": "com.br",
  "cache_timestamp": "2023-12-11T10:30:00",
  "cache_expires_at": "2023-12-11T10:40:00",
  "from_cache": true,
  "cache_hit": true,
  "is_fallback": true,
  "fallback_reason": "Scraping failed"
}
```

---

## 🏗️ Arquitetura

### Fluxo do Sistema de Cache:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Cliente   │────▶│   FastAPI   │────▶│   Camada    │────▶│  Downdetector│
│   Requisição│     │   Endpoint  │     │   de Cache  │     │   Scraper    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                        │                    │                    │
                        │   Cache Hit?       │   Cache Miss/Expired
                        │◀───────────────────│───────────────────▶│
                        │                    │                    │
                        │   Retorna Dados    │   Busca Dados      │
                        │   Cache (Instant)  │   Novos (10+ seg)  │
                        └───────────────────▶│◀───────────────────┘
```

### Serviços Docker:
- **`downdetector`**: FastAPI + Scraper Playwright com camada de cache
- **`nginx`**: Proxy reverso com cache adicional e serviço de arquivos estáticos
- **Rede Compartilhada**: `app-network` para comunicação entre containers
- **Diretório de Cache**: `./cache` para armazenamento persistente de cache

---

## ⚙️ Configuração

### Configurações de Cache:
- **Duração do Cache:** 10 minutos (600 segundos)
- **Diretório de Cache:** `./cache` (criado automaticamente)
- **Formato do Arquivo de Cache:** JSON com metadados
- **Auto-expiração:** Sim (baseado em timestamp)

### Configurações Nginx (`nginx.conf`):
- **Porta:** 80 (mapeada para porta do host 8089)
- **Cache de arquivos estáticos:** 1 ano para assets
- **Cache de respostas da API:** 10 segundos para respostas 200/302 (camada adicional)
- **Cabeçalhos CORS:** Habilitados para todas as origens
- **Compressão Gzip:** Habilitada para conteúdo baseado em texto

### Personalização do Ambiente:
Modifique `docker-compose.yml` para:
  - Alterar portas expostas
  - Ajustar limites de recursos (CPU/memória)
  - Habilitar configurações de produção
  - Modificar duração do cache definindo variáveis de ambiente

### Personalização do Dashboard:
- Modifique `index.html` para alterações na interface
- Atualize a configuração do Tailwind na seção `<script>` para cores do tema
- Ajuste colunas do grid nas classes CSS de `companiesGrid`
- Altere intervalo de auto-atualização no JavaScript (padrão: 10 minutos)

---

## 🔧 Solução de Problemas

### Problemas Comuns:

1. **Navegador Playwright não instalando:**
   ```bash
   # Dentro do container:
   docker exec -it downdetector playwright install
   ```

2. **Dashboard não carregando empresas:**
   - Verifique console do navegador por erros
   - Verifique se API está acessível: `curl http://localhost:8089/api/companylist`
   - Certifique-se que containers estão rodando: `docker ps`
   - Verifique arquivos de cache: `ls -la ./cache/`

3. **Obtendo dados desatualizados:**
   - Cache expira automaticamente após 10 minutos
   - Limpe manualmente o cache: `curl -X DELETE http://localhost:8089/api/cache/clear`
   - Ou limpe apenas o expirado: `curl -X DELETE http://localhost:8089/api/cache/clear/expired`

4. **Cache não funcionando:**
   - Certifique-se que o diretório `./cache` existe e tem permissão de escrita
   - Verifique permissões: `chmod 755 ./cache`
   - Verifique informações do cache: `curl http://localhost:8089/api/cache/info`

5. **Primeira requisição lenta, requisições subsequentes rápidas:**
   - Comportamento esperado - primeira requisição faz scraping do Downdetector (lento)
   - Requisições subsequentes usam cache (rápido) até o cache expirar

6. **Logos de empresas faltando:**
   - Algumas empresas podem não ter logos no Downdetector
   - Fallback exibe nome da empresa em texto

---

## 📄 Licença e Atribuição

- **Interface do Dashboard**: Construída customizada com Tailwind CSS e Material Icons
- **Fonte de Dados**: Downdetector (https://downdetector.com)
- **Framework da API**: FastAPI (https://fastapi.tiangolo.com)
- **Automação de Navegador**: Playwright (https://playwright.dev)

---

## 🤝 Contribuindo

1. Faça um fork do repositório
2. Crie um branch para sua feature
3. Faça commit das suas alterações
4. Push para o branch
5. Abra um Pull Request

---

## 📞 Suporte

Para problemas, solicitações de funcionalidades ou perguntas:
1. Verifique a seção de solução de problemas acima
2. Revise a documentação da API em `/docs`
3. Abra uma issue no repositório

---

**Nota**: Esta ferramenta é apenas para fins de monitoramento. O sistema de cache embutido ajuda a respeitar os servidores do Downdetector limitando as requisições a uma vez a cada 10 minutos por endpoint. Implemente limitação de taxa adicional em ambientes de produção se necessário.

---

**Bom Monitoramento!** 🚀

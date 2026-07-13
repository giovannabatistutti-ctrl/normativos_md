# REASONING LAYER — Aditamentos iFood Benefícios

**Versão:** 1.0  
**Data:** 2025-07-08  
**Projeto:** 15-aditamentos — iFood Pago Compliance  
**Base documental:** `data/ifb-aditamentos/analise_estrutura_aditamento.md`

---

## 1. Como identificar o tipo de aditamento a partir de um ticket Jira

### 1.1 Fonte de dados primária

O ticket Jira do projeto **JURFIN** com tipo **"Aditivos não padrão"** e empresa **"iFood Benefícios"** é a fonte primária de todas as informações do aditamento.

### 1.2 Campos do ticket a inspecionar

| Campo Jira | Informação | Uso no aditamento |
|---|---|---|
| `summary` | Descrição do pedido | Identificar módulos solicitados |
| `customfield_empresa` | Razão social da empresa | Cabeçalho do aditamento |
| `customfield_cnpj` | CNPJ da empresa | Cabeçalho + validação |
| `customfield_modulos` | Lista de módulos selecionados | Seleção de blocos do template |
| `customfield_proposta_com` | Proposta Comercial ISA | Pré-condição para módulo ISA (11) |
| `attachment` | Arquivos anexados | Contrato-base + Proposta Comercial |
| `assignee` | Advogado responsável | Destinatário de perguntas PENDENTES |

### 1.3 Identificação do tipo de aditamento

**Leia o campo `customfield_modulos`** (ou equivalente) e mapeie para os módulos do template:

| Solicitação no ticket | Módulo correspondente |
|---|---|
| Correção de faturamento / Atualização de valores | Módulo 1 |
| Remover prorrogação automática | Módulo 2 |
| Prorrogar vigência (sem renovação automática) | Módulo 3 |
| Prorrogar vigência (com renovação automática) | Módulo 4 |
| Remover cessão de poderes / Cláusula 16.6 | Módulo 5 |
| Reduzir aviso prévio de rescisão | Módulo 6 |
| Incluir CNPJs do grupo | Módulo 7 |
| Remover CNPJs do grupo | Módulo 8 |
| Declaração iFood Pago IP / ZOOP | Módulo 9 |
| Retirada de Colab+ / Subsídio | Módulo 10 |
| ISA / Incentivo ao Saldo Alimentar | Módulo 11 |
| Saldo Extra | Módulo 12 |
| Saldo Natal | Módulo 13 |

**Se o módulo solicitado não está na lista acima → campo PENDENTE com pergunta ao advogado.**

---

## 2. Como ler um contrato anexo e localizar cláusulas relevantes

### 2.1 Formatos suportados

| Formato | Suporte | Observação |
|---|---|---|
| `.pdf` | ✅ Suportado | Usar `pdfplumber` para extração de texto |
| `.docx` | ✅ Suportado | Usar `python-docx` |
| `.doc` | ⚠️ Limitado | Formato legado OLE2 — solicitar conversão para .docx |
| Google Docs | ✅ Suportado | Usar Google Docs API |

### 2.2 Cláusulas a localizar

| Cláusula | Tema | Dado a extrair |
|---|---|---|
| Item VIII do Formulário | Dados da empresa / produtos | Razão social, CNPJ, endereço, CEP, produtos contratados |
| Cláusula 10.2 | Prorrogação automática | Prazo de vigência original |
| Cláusula 10.3 | Aviso prévio de rescisão | Número de dias de aviso prévio **original** |
| Cláusula 16.6 | Cessão de direitos | Restrições existentes |
| Seção de partes | Identificação da empresa | Confirmar razão social e CNPJ |

### 2.3 Dados críticos a extrair do contrato

1. **Data de assinatura do contrato original** — obrigatória para o cabeçalho
2. **Prazo de aviso prévio original (Cláusula 10.3)** — necessário para validar que o aviso prévio negociado é menor
3. **Produtos contratados** — para módulo de correção de faturamento
4. **CNPJs do grupo** — para módulos 7 e 8
5. **Presença do Programa Colab+** — pré-condição para módulo 10

### 2.4 Procedimento se o contrato não estiver anexado

→ Marcar `DATA_CONTRATO_ORIGINAL` como `{{PENDENTE: Qual a data de assinatura do contrato original?}}`  
→ Postar pergunta no ticket Jira ao advogado responsável  
→ **Nunca estimar ou assumir a data**

---

## 3. Como mapear informações do ticket para variáveis do template

### 3.1 Variáveis globais (todos os aditamentos)

| Variável template | Fonte | Validação |
|---|---|---|
| `{{RAZAO_SOCIAL}}` | `customfield_empresa` no ticket | Obrigatório, não vazio |
| `{{CNPJ_EMPRESA}}` | `customfield_cnpj` no ticket | Formato XX.XXX.XXX/XXXX-XX + dígitos verificadores |
| `{{ENDERECO_EMPRESA}}` | Contrato anexo (Item VIII) | Obrigatório |
| `{{CEP_EMPRESA}}` | Contrato anexo (Item VIII) | Formato XX.XXX-XXX |
| `{{DATA_CONTRATO_ORIGINAL}}` | Contrato anexo | Formato: DD de MMMM de AAAA |
| `{{DATA_ADITIVO}}` | Ticket ou instrução do advogado | Não pode ser anterior ao contrato |
| `{{CIDADE_ASSINATURA}}` | Default: "Osasco" | Confirmar se diferente |

### 3.2 Variáveis por módulo

**Módulo 6 — Aviso Prévio:**
- `{{AVISO_PREVIO_DIAS}}` ← número informado no ticket (campo específico ou comentário do advogado)
- `{{AVISO_PREVIO_EXTENSO}}` ← gerado automaticamente a partir de `AVISO_PREVIO_DIAS`

**Módulo 1 — Correção de Faturamento:**
- Produtos e valores ← Item VIII do formulário atualizado, conforme instrução no ticket

**Módulos 7/8 — CNPJs do Grupo:**
- Lista de empresas ← campo específico no ticket (razão social + CNPJ de cada empresa)

### 3.3 Marcador de campo ausente

Quando uma informação não está disponível no ticket NEM no contrato anexo:

```
{{PENDENTE: [pergunta exata para o advogado]}}
```

**Exemplos:**
- `{{PENDENTE: Qual a data de assinatura do contrato original?}}`
- `{{PENDENTE: Quantos dias de aviso prévio foram negociados?}}`
- `{{PENDENTE: Qual o endereço completo da empresa para constar no aditamento?}}`

Campos PENDENTES são postados como comentário no ticket Jira ao advogado responsável.

---

## 4. Diretriz de Integridade (OBRIGATÓRIA)

> Esta seção é de cumprimento obrigatório em toda operação do pipeline.  
> Violações desta diretriz bloqueiam a geração do documento.

### 4.1 Regras fundamentais

1. **NUNCA inventar cláusulas, valores, datas, nomes ou termos.**  
   Se a informação não está disponível, usar `{{PENDENTE: [pergunta]}}` — sem exceção.

2. **Toda variável preenchida deve ter fonte declarada.**  
   - Fonte aceita 1: campo específico do ticket Jira (ex: `customfield_cnpj`)  
   - Fonte aceita 2: cláusula específica do contrato anexo (ex: "Cláusula 10.3 do contrato em PDF")  
   - Fonte aceita 3: padrão configurado (`default`) — apenas para valores fixos conhecidos (ex: cidade "Osasco")  
   - **Não é fonte aceita:** inferência, estimativa, conhecimento prévio, valor "provável"

3. **Se a informação não está no ticket ou no contrato → `{{PENDENTE: [pergunta exata]}}`**  
   A pergunta deve ser suficientemente específica para que o advogado possa responder objetivamente.

4. **Dúvidas são postadas diretamente ao advogado no ticket Jira.**  
   O pipeline nunca resolve ambiguidades com estimativas ou suposições.

5. **Score ≥ 0.90 só é possível com ZERO campos PENDENTES.**  
   Qualquer campo `{{PENDENTE}}` mantém o score em 0 e bloqueia o envio autônomo.

6. **Campos PENDENTES bloqueiam envio autônomo ao Netlex.**  
   O documento só pode ser enviado autonomamente quando score ≥ 0.90 e sem nenhum PENDENTE.

### 4.2 Terminologia canônica obrigatória

| Termo correto | Variações PROIBIDAS |
|---|---|
| `ISA` | "Saldo Saúde Alimentar", "Saldo Alimentação Saudável", "Incentivo Alimentar" |
| `iFood Refeição` | "Refeição", "Vale Refeição", "VR iFood" |
| `iFood Alimentação` | "Alimentação", "Vale Alimentação", "VA iFood" |
| `Saldo Natal` | "Benefício Natal", "Crédito Natal" |
| `Saldo Extra` | "Benefício Extra", "Crédito Extra" |
| `Programa Colab+` | "Colab Plus", "Programa Colaboração" |
| `iFood Pago IP` | "iFood Pago", "iFood Pagamentos", "ZOOP" (isolado) |

Detecção de termo não-canônico → **score = 0**, bloquear geração.

### 4.3 Campos globais obrigatórios (bloqueiam geração se ausentes)

Razão Social, CNPJ (válido), Endereço, CEP, Data do Contrato Original, Data do Aditivo.

---

## 5. Módulos a criar (não presentes no template atual)

### 5.1 Módulo 11 — ISA (Incentivo ao Saldo Alimentar)

- **Pré-condição documental obrigatória:** Proposta Comercial ISA deve estar anexada ao ticket
- **Se ausente:** `{{PENDENTE: A Proposta Comercial ISA não foi localizada nos anexos. Por favor anexe ao ticket antes do processamento.}}`
- **Terminologia:** Usar exclusivamente "ISA" — nunca "Saldo Saúde Alimentar" ou "Saldo Alimentação Saudável"

### 5.2 Módulo 12 — Saldo Extra

- Módulo a ser especificado com o time jurídico
- Por enquanto: requer instrução explícita do advogado no ticket

### 5.3 Módulo 13 — Saldo Natal

- **Regra específica:** Responsabilidade de distribuição é do **cliente** (empresa contratante), **não do iFood**
- Esta regra deve constar expressamente no texto do módulo
- Duplo aditamento ISA + Saldo Natal (módulos 11 + 13): gerar **um único documento consolidado**

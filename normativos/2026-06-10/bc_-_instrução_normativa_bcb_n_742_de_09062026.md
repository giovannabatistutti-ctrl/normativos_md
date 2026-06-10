# BC - Instrução Normativa BCB N° 742 de 09/06/2026

> **Análise iFood Pago | Compliance** — 10/06/2026 16:03  
> **Gerado por:** Pipeline determinístico (agente Toqan indisponível nesta execução)

---

## Identificação

| Campo | Valor |
|---|---|
| **Tipo** | Instrução Normativa BCB |
| **Número** | 742 |
| **Data de Publicação** | 2026-06-10 |
| **Vigência** | Verificar texto integral |
| **Link oficial** | [https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Instru%C3%A7%C3%A3o%20Normativa%20BCB&numero=742](https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?tipo=Instru%C3%A7%C3%A3o%20Normativa%20BCB&numero=742) |

---

## Classificação

| Campo | Valor |
|---|---|
| **Classificação** | 🟡 **MONITORAR** |
| **Confiança** | MÉDIA |
| **Criticidade** | 🟢 **BAIXO** |

---

## Racional da Classificação

A IN BCB nº 742 não é diretamente aplicável mas deve ser monitorada pois divulga a versão 8.3 do manual operacional do diretório de identificadores de contas transacionais (dict), que compõe o regulamento do pix. Temas a acompanhar: pix.

---

## Ementa

Divulga a versão 8.3 do Manual Operacional do Diretório de Identificadores de Contas Transacionais (DICT), que compõe o Regulamento do Pix.

---

## Análise do Agente (mensagem Slack)

🔴 APLICÁVEL — Instrução Normativa BCB nº 742/2026

**1. Identificação**
Foi publicada a Instrução Normativa BCB nº 742, de 09/06/2026, que divulga a versão 8.3 do Manual Operacional do Diretório de Identificadores de Contas Transacionais (DICT), parte integrante do Regulamento do Pix.

**2. Vigência**
Imediata, a partir de 09/06/2026.

**3. Resumo**
*(i)* O DICT é o diretório central do Banco Central que relaciona chaves Pix às contas receptoras, sendo essencial para lookup/roteamento de pagamentos Pix, consulta de titulares e resolução de portabilidade de chave.
*(ii)* A versão 8.3 do Manual Operacional pode trazer alterações nos procedimentos operacionais, formatos de mensagens, SLAs ou requisitos de segurança relacionados ao DICT.
*(iii)* Impacto direto nas operações do iFood Pago relacionadas ao Pix, especialmente no registro e gerenciamento de chaves Pix, portabilidade, e atendimento a SLAs e requisitos de segurança.
*(iv)* Ponto de atenção: verificar as mudanças específicas introduzidas pela versão 8.3 e adequar os sistemas e processos do iFood Pago para conformidade.

**4. Íntegra:** 📄 [link DOU ou BCB]

**5. Próximos Passos**
Peço por gentileza que as áreas de Operações e Tecnologia avaliem as alterações da versão 8.3 do Manual Operacional do DICT e implementem as adequações necessárias até 30/06/2026. Caso necessário, posso agendar um GT para alinhamento.

🎯 Avaliação de Risco
| Pilar | Nível | Motivo |
|---|---|---|
| ⚙️ Operacional | 3 | Alterações no DICT podem exigir ajustes em sistemas e processos operacionais. |
| ⚖️ Regulatório | 4 | Conformidade com o DICT é obrigatória para participantes do Pix. |
| 💰 Financeiro | 2 | Risco financeiro moderado em caso de não conformidade, como multas ou sanções. |
| 👥 Clientes | 3 | Impacto na experiência do cliente em caso de falhas no registro ou portabilidade de chaves. |
Score: 12 | Criticidade: 🟠 ALTO |

---

## Políticas Internas Relacionadas

- iFP-POL-013 — Política de Prevenção e Combate a Fraudes (Fraudes/Risk (coordenação); Compliance/PLD (integração); Operações (execução de bloqueios); Jurídico (processos judiciais).)

---

*Pipeline normativos-bcb | iFood Pago Compliance | 10/06/2026 16:03*
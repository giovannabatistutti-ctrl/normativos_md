---
modulo: "aviso_previo"
versao: "1.0"
produtos: ["todos"]
variaveis_obrigatorias:
  - "PRAZO_AVISO_PREVIO_DIAS"
variaveis_opcionais:
  - "PRAZO_AVISO_PREVIO_EXTENSO"
regras_negocios:
  - "ATENÇÃO: o campo PRAZO_AVISO_PREVIO_DIAS NUNCA pode ser inventado ou estimado"
  - "O valor DEVE ser extraído explicitamente do contrato original ou do ticket de solicitação"
  - "Se o valor não estiver disponível na documentação, preencher como PENDENTE e NÃO gerar o aditivo"
  - "PRAZO_AVISO_PREVIO_DIAS deve ser inteiro positivo e menor que o prazo original dos TCG"
  - "PRAZO_AVISO_PREVIO_EXTENSO é gerado automaticamente a partir de PRAZO_AVISO_PREVIO_DIAS (ex: 30 → trinta)"
  - "Este módulo altera a Cláusula 10.3 dos Termos e Condições Gerais"
  - "A redução do aviso prévio é uma concessão negociada — exige aprovação comercial documentada"
---

## ALTERAÇÃO DA CLÁUSULA 10.3 — AVISO PRÉVIO PARA RESCISÃO IMOTIVADA

> ⚠️ **AVISO CRÍTICO — CAMPO OBRIGATÓRIO:**
> O prazo de aviso prévio (`{{PRAZO_AVISO_PREVIO_DIAS}}`) **NUNCA** deve ser preenchido com valor estimado ou padrão sem base documental. Este campo deve ser extraído do contrato original ou da solicitação aprovada. Se não localizado: marcar como **PENDENTE** e suspender a geração até obter a informação.

**1.1.** As Partes acordam em alterar a Cláusula 10.3 dos Termos e Condições Gerais, que passará a vigorar com a seguinte redação:

> *"10.3. A Empresa poderá solicitar a exclusão de algum Benefício, mantendo o Contrato vigente para os demais, ou solicitar a resilição do Contrato, imotivadamente, devendo, em ambos os casos, enviar aviso por escrito ao iFood Benefícios com no mínimo {{PRAZO_AVISO_PREVIO_DIAS}} ({{PRAZO_AVISO_PREVIO_EXTENSO}}) dias de antecedência."*

**1.2.** O prazo de aviso prévio estabelecido na cláusula acima aplica-se tanto à resilição total do Contrato quanto à exclusão parcial de benefícios, preservando, neste último caso, as demais condições contratuais vigentes.

**1.3.** O aviso prévio deverá ser enviado por escrito, por meio de comunicação formal entre os representantes autorizados das Partes, não sendo válido aviso verbal ou tácito para os fins desta cláusula.

---
fonte_modelo: "aditamento_ifood_beneficios_v1"

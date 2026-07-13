---
modulo: "cabecalho"
versao: "1.0"
produtos: ["todos"]
variaveis_obrigatorias:
  - "RAZAO_SOCIAL"
  - "CNPJ"
  - "ENDERECO"
  - "REPRESENTANTE_LEGAL"
  - "CPF_REPRESENTANTE"
  - "NUMERO_CONTRATO"
  - "DATA_CONTRATO_ORIGINAL"
variaveis_opcionais: []
regras_negocios:
  - "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX com dígitos verificadores válidos"
  - "CPF_REPRESENTANTE deve estar no formato XXX.XXX.XXX-XX com dígitos verificadores válidos"
  - "DATA_CONTRATO_ORIGINAL deve ser anterior à data de assinatura do aditivo"
  - "NUMERO_CONTRATO deve conter referência ao contrato original celebrado entre as partes"
---

## TERMO ADITIVO AO CONTRATO DE PRESTAÇÃO DE SERVIÇOS

**PARTES:**

**CONTRATADA:** iFood Benefícios e Serviços Ltda., inscrita no CNPJ/MF sob o n.º 33.157.312/0001-62, com sede na Av. dos Autonomistas, 1.496, Bloco B, 3º andar, Vila Yara, Osasco/SP, CEP 06.020-902, doravante denominada simplesmente **iFood Benefícios**;

**CONTRATANTE:** {{RAZAO_SOCIAL}}, pessoa jurídica de direito privado, inscrita no CNPJ/MF sob o n.º {{CNPJ}}, com sede em {{ENDERECO}}, representada neste ato por seu representante legal, {{REPRESENTANTE_LEGAL}}, portador do CPF n.º {{CPF_REPRESENTANTE}}, doravante denominada simplesmente **CONTRATANTE** ou **Empresa**;

**iFood Benefícios** e **CONTRATANTE**, quando mencionadas em conjunto, doravante denominadas simplesmente **"Partes"**.

---

**PREÂMBULO**

**CONSIDERANDO QUE** as Partes celebraram, em {{DATA_CONTRATO_ORIGINAL}}, o Contrato de Prestação de Serviços n.º {{NUMERO_CONTRATO}} (doravante referido como **"Contrato"**), composto pelo Formulário de Contratação, pelos Termos e Condições Gerais de Uso dos Serviços ("TCG") disponíveis em https://marketing-assets-benefits.ifood.com.br/terms/termos-e-condicoes-gerais.pdf, e pelos Termos e Condições Específicas aplicáveis a cada benefício contratado ("TCE");

**CONSIDERANDO QUE** as Partes têm interesse em alterar determinadas condições do Contrato, nos termos e condições estabelecidos no presente instrumento;

**RESOLVEM** celebrar o presente Termo Aditivo ao Contrato de Prestação de Serviços (doravante "Aditivo"), mediante as seguintes cláusulas e condições:

---

**ALTERAÇÕES**

---
fonte_modelo: "aditamento_ifood_beneficios_v1"

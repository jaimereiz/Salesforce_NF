#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce

# Conectar ao Salesforce
sf = Salesforce(username="jaimefilho@bemol.com.br", password="230599va", security_token="C4BInx42NDqNJXCb19giFdM4")

# Configuração do Streamlit
st.title("Consulta de Notas Fiscais")

# Entrada do usuário
NF_input = st.text_input("Digite os números das notas fiscais separados por vírgula:")
Serie = st.text_input("Digite o número da série:")

if st.button("Consultar"):
    if NF_input and Serie:
        NF_list = [nf.strip() for nf in NF_input.split(" ")]  # Corrigido separador de espaço
        NF_condition = f"IN ({', '.join([repr(nf) for nf in NF_list])})"

        # Consulta Invoice__c
        invoice_query = f"""
        SELECT
            Id, Name, BairroEntrega__c,CepEntrega__c, Store__c,Serie__c,MsgNota__c
        FROM
            Invoice__c
        WHERE
            Name {NF_condition} AND Serie__c = '{Serie}'
        """
        invoice_response = sf.query(invoice_query)

        if invoice_response['records']:
            invoice_df = pd.DataFrame(invoice_response['records'])
            invoice_df.drop(columns=["attributes"], errors="ignore", inplace=True)

            # Obtendo os IDs das notas fiscais
            invoice_ids = invoice_df['Id'].tolist()
            
            if invoice_ids:  # Verifica se há IDs antes de prosseguir
                InvoiceId_condition = f"IN ({', '.join([repr(id) for id in invoice_ids])})"

                # Consulta InvoiceItems__c
                InvoiceItems_query = f"""
                SELECT
                    Name, MaterialNumber__c, InvoiceId__c,NetPrice__c
                FROM
                    InvoiceItems__c
                WHERE
                    InvoiceId__c {InvoiceId_condition}
                """
                InvoiceItems_response = sf.query(InvoiceItems_query)

                if InvoiceItems_response['records']:
                    InvoiceItems_df = pd.DataFrame(InvoiceItems_response['records'])
                    InvoiceItems_df.drop(columns=["attributes"], errors="ignore", inplace=True)

                    # Merge dos DataFrames
                    merged_df = pd.merge(
                        invoice_df,
                        InvoiceItems_df,
                        left_on='Id',
                        right_on='InvoiceId__c',
                        how='left'
                    )

                    # Remover colunas desnecessárias
                    merged_df.drop(columns=['InvoiceId__c','Id'], inplace=True, errors="ignore")

                    st.write("### Resultados da Consulta:")
                    st.dataframe(merged_df)
                else:
                    st.warning("Nenhum item encontrado para as notas fiscais informadas.")
                    st.dataframe(invoice_df)
            else:
                st.warning("Nenhuma nota fiscal encontrada para os valores informados.")
        else:
            st.warning("Nenhuma nota fiscal encontrada para os valores informados.")
    else:
        st.error("Por favor, digite as notas fiscais e o número da série.")
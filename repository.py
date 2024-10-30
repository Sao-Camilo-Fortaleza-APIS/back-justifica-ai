import database as db

class applicant:
    def __init__(self):
        pass

    def search_applicant(self,nr_cpf):
        try:
            conn = db.connect_sql_server_bd()
            conn2 = db.connect_oracle_bd()
            with conn.cursor() as cursor:
                query = f"""select Codigo as MATRICULA, Nome, eMail from EPG
                          where CPF = ?
                          and DtRescisao is null"""

                cursor.execute(query,(nr_cpf))

                rows = cursor.fetchone()

            with conn2.cursor() as cursor:
                query = f"""select cd_pessoa_fisica 
                            from tasy.pessoa_fisica
                            where nr_cpf = :n_cpf"""
                
                cursor.execute(query, {"n_cpf": nr_cpf})

                rows2 = cursor.fetchone()

            if rows and rows2:
                response = {"mat":rows[0],"name":rows[1], "email":rows[2], "id_tasy":rows2[0]}
            else:
                response = None
            
        except Exception as e:
            return str(e)
        finally:
            return response

class Orders:
    def __init__(self):
        pass

    def post_justify_order(self,aware_p,requester_p,number_p,mat_p,cd_sector_p,occurrence_p,reason_p,component_p):

        conn = db.connect_oracle_bd()
        try:
            if aware_p:
                aware_p = "Aceito"
            else:
                aware_p = "Não aceito"
            
            with conn.cursor() as cursor:
                cursor.execute(f"select tasy.obter_nome_pf({requester_p}) from dual")
                nm_applicant = cursor.fetchone()[0]

                title_p = f"AJUSTE PONTO: {nm_applicant} - {occurrence_p}"

                description_p = f"""Dados Justificativa:\nTermo de Ciência: {aware_p}\nMat: {mat_p}\nNome: {nm_applicant}\nData Ocorrência: {occurrence_p}\nMotivo: {reason_p}\nObservação: {component_p}"""

                query = """select tasy.man_ordem_servico_seq.nextval from dual"""

                query2 = """INSERT INTO tasy.MAN_ORDEM_SERVICO(NR_SEQUENCIA, DT_ORDEM_SERVICO, CD_PESSOA_SOLICITANTE, NM_USUARIO,
                                                        DS_CONTATO_SOLICITANTE, DS_DANO_BREVE,DS_DANO, IE_PARADO, IE_PRIORIDADE,
                                                        DT_INICIO_DESEJADO, DT_CONCLUSAO_DESEJADA, NR_SEQ_LOCALIZACAO, NR_SEQ_EQUIPAMENTO, 
                                                        NR_GRUPO_PLANEJ, NR_GRUPO_TRABALHO, IE_ATUALIZACAO_MIGRACAO, IE_OBRIGAR_AVALIACAO, 
                                                        IE_ORIGEM_OS, IE_SOLIC_VIP, IE_OS_RELATORIO, IE_GRAU_SATISFACAO, 
                                                        IE_ENVOLVE_TREINAMENTO, IE_ORIENTACAO_SATISFACAO, IE_OBRIGA_NEWS, IE_TIPO_ORDEM,
                                                        IE_STATUS_ORDEM, NR_SEQ_ESTAGIO, NM_USUARIO_NREC, dt_atualizacao )
                    VALUES (:last_seq_p, SYSDATE, :requester, 'Tasy', 
                            :nr_contato, :titulo_p, :descricao_p, 'N', 'M', 
                            TRUNC(SYSDATE), SYSDATE + 1, 
                            :nr_seq_localizacao, 21913, 33, 50, 
                            'P', 'N', 4, 'N', 'N', 'N', 'N', 'N', 'S', 1, 1, 59, 'Tasy', sysdate)"""
                
                cursor.execute(query)
                last_seq = cursor.fetchone()[0]

                cursor.execute(query2,{"last_seq_p":last_seq,
                                       "requester":requester_p,
                                       "nr_contato": number_p,
                                       "titulo_p": title_p,
                                       "descricao_p": description_p,
                                       "nr_seq_localizacao": cd_sector_p})
                response = last_seq
            conn.commit()
            
        except Exception as e:
            response = str(e)

        finally:
            return response
        
    def get_sector(self):
        try:
            conn = db.connect_oracle_bd()
            cursor = conn.cursor()
            cursor.execute(f"select nr_sequencia, ds_localizacao from tasy.man_localizacao where ie_situacao = 'A' and nr_sequencia not in (40,34,37,97,36,218,205,186)  order by 2")

            rows = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
            response = [{"nr_sequencia": row[0], "ds_localizacao": row[1]} for row in rows]
            return response

    def get_orders_pendents(self,nm_user):
        try:
            conn = db.connect_oracle_bd()
            with conn.cursor() as cursor:
                query = f"""SELECT dt_ordem_servico, b.nr_sequencia, tasy.obter_nome_pf(b.cd_pessoa_solicitante)ds_pessoa_solicitante, tasy.obter_desc_man_localizacao(b.nr_seq_localizacao) ds_localizacao, b.ds_dano_breve, b.ds_contato_solicitante, b.nr_grupo_trabalho, b.ds_dano
                                    FROM TASY.MAN_ORDEM_SERVICO_EXEC A RIGHT JOIN TASY.MAN_ORDEM_SERVICO B ON(A.NR_SEQ_ORDEM = B.NR_SEQUENCIA)
                                    WHERE B.ie_status_ordem not in 3 and  UPPER(a.nm_usuario_exec) IS NULL
                                    and b.NR_SEQ_WHEB is null
                                    and b.nr_grupo_trabalho = 50
                                    and b.NR_SEQ_LOCALIZACAO in (SELECT nr_seq_localizacao
                                                                 FROM TASY.MAN_RESP_LOCALIZACAO
                                                                 WHERE cd_pessoa_resp_localizacao = TASY.HCD_OBTER_CODIGO_USUARIO(:nm_usuario))
                                    order by nr_sequencia"""
                cursor.execute(query,{"nm_usuario":nm_user})
                response = cursor.fetchall()
        except Exception as e:
            response = str(e)
        finally:
            return response

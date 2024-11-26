import database as db

class UserRepository:
    def __init__(self):
        pass

    ## METODO QUE BUSCA O USUÁRIO ##
    def find_user(self, user):
        try:
            conn = db.connect_oracle_bd()

            with conn.cursor() as cursor:
                query = f"""
                SELECT UPPER(nm_usuario), ds_senha, ds_tec, cd_pessoa_fisica,
                CASE WHEN (UPPER(DS_LOGIN) = UPPER('{user}')) then UPPER(DS_LOGIN)
                WHEN (UPPER(NM_USUARIO) = UPPER('{user}')) then UPPER(NM_USUARIO) END
                FROM tasy.usuario 
                WHERE (UPPER(nm_usuario) = UPPER('{user}') OR UPPER(DS_LOGIN) = UPPER('{user}'))
                """
                cursor.execute(query)
                rows = cursor.fetchone()

            if rows:
                nm_usuario_bd = rows[4]
                cd_pessoa_fisica = rows[3]

                with conn.cursor() as cursor:
                    query = f"""SELECT COUNT(*) from tasy.MAN_RESP_LOCALIZACAO 
                                WHERE CD_PESSOA_RESP_LOCALIZACAO = :cd_pessoa_fisica"""
                    cursor.execute(query,{"cd_pessoa_fisica":cd_pessoa_fisica})
                    if_manager = cursor.fetchone()

                if nm_usuario_bd == user.upper() and if_manager[0] != 0:
                    return rows
                else:
                    return None
            else:
                return None

        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

class applicant:
    def __init__(self):
        pass

    def search_applicant(self,nr_cpf):
        try:
            conn = db.connect_sql_server_bd()
            conn2 = db.connect_oracle_bd()
            with conn.cursor() as cursor:
                query = f"""select Codigo as MATRICULA, Nome, eMail, cpf from EPG
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
                response = {"mat":rows[0],"name":rows[1], "email":rows[2], "id_tasy":rows2[0], "cpf":rows[3]}
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
                            :nr_seq_localizacao, 21926, 33, 52, 
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
                query = f"""SELECT to_char(dt_ordem_servico, 'dd/mm/yyyy hh24:mi') dt_ordem_servico
                                   ,b.nr_sequencia
                                   ,tasy.obter_nome_pf(b.cd_pessoa_solicitante)ds_pessoa_solicitante
                                   ,tasy.obter_desc_man_localizacao(b.nr_seq_localizacao) ds_localizacao
                                   ,b.ds_dano_breve
                                   ,b.ds_contato_solicitante
                                   ,b.nr_grupo_trabalho
                                   ,b.ds_dano
                                   ,SUBSTR(b.ds_dano_breve, instr(b.ds_dano_breve,'- ') + 2, length(b.ds_dano_breve)) data_ocorrencia
                            FROM TASY.MAN_ORDEM_SERVICO_EXEC A RIGHT JOIN TASY.MAN_ORDEM_SERVICO B ON(A.NR_SEQ_ORDEM = B.NR_SEQUENCIA)
                                WHERE B.ie_status_ordem not in 3 and  UPPER(a.nm_usuario_exec) IS NULL
                                and b.NR_SEQ_WHEB is null
                                and b.nr_grupo_trabalho = 52
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

    def approve_justification(self,nm_user,nr_order,ds_treatment, ds_observation):
        try:

            ds_history = f"""Autorizo a justificativa ser tratada com o seguinte motivo: {ds_treatment} \nOBS: {ds_observation}"""
            conn = db.connect_oracle_bd()

            with conn.cursor() as cursor:
                query = f"""INSERT INTO tasy.man_ordem_serv_tecnico (nr_seq_tipo,dt_liberacao,dt_historico,nm_usuario_lib,
                                                                        dt_atualizacao,ds_relat_tecnico,ie_relevante_teste,nm_usuario,
                                                                        nr_seq_ordem_serv,ie_origem,nr_sequencia) 
                           VALUES (5,SYSDATE,SYSDATE,:get_user,SYSDATE,:ds_history,'N',:get_user,:nr_ordem,'I',tasy.MAN_ORDEM_SERV_TECNICO_SEQ.NEXTVAL)"""
                
                query2 = f"""update tasy.man_ordem_servico set nr_grupo_trabalho = 53 where nr_sequencia = :nr_ordem"""

                cursor.execute(query, {"ds_history": ds_history,
                                       "get_user": nm_user,
                                       "nr_ordem":nr_order})
                
                cursor.execute(query2, {"nr_ordem":nr_order})

                conn.commit()
                response = "Success"

        except Exception as e:
            response = str(e)
            conn.rollback()
        finally:
            return response

    def disapprove_justification(self,nm_user,nr_order, ds_observation):
        try:

            ds_history = f"""Justificativa recusada com o seguinte motivo: {ds_observation}"""
            conn = db.connect_oracle_bd()

            with conn.cursor() as cursor:
                query = f"""INSERT INTO tasy.man_ordem_serv_tecnico (nr_seq_tipo,dt_liberacao,dt_historico,nm_usuario_lib,
                                                                        dt_atualizacao,ds_relat_tecnico,ie_relevante_teste,nm_usuario,
                                                                        nr_seq_ordem_serv,ie_origem,nr_sequencia) 
                           VALUES (6,SYSDATE,SYSDATE,:get_user,SYSDATE,:ds_history,'N',:get_user,:nr_ordem,'I',tasy.MAN_ORDEM_SERV_TECNICO_SEQ.NEXTVAL)"""
                
                query2 = f"""UPDATE TASY.MAN_ORDEM_SERVICO SET IE_STATUS_ORDEM = 3, NR_SEQ_ESTAGIO = 23, DT_FIM_REAL = sysdate WHERE NR_SEQUENCIA = :nr_ordem"""

                cursor.execute(query, {"ds_history": ds_history,
                                       "get_user": nm_user,
                                       "nr_ordem":nr_order})
                
                cursor.execute(query2, {"nr_ordem":nr_order})

                conn.commit()
                response = "Success"

        except Exception as e:
            response = str(e)
            conn.rollback()
        finally:
            return response

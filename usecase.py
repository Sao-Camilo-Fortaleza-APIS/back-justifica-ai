import repository as repo
from hashlib import sha256
from flask import jsonify

class LoginUseCase():
    def __init__(self):
        self.user_repo = repo.UserRepository()

    def check_credentials(self, user, pwd):
        try:
            user_return = self.user_repo.find_user(user)
            if user_return:
                nm_user = user_return[0]
                nm_user_bd = user_return[4]
                ds_senha_banco = user_return[1]
                ds_tec = user_return[2]

                password_cripto = pwd.upper() + ds_tec
                password_cripto = password_cripto.encode('utf-8')
                password_cripto = sha256(password_cripto).hexdigest().upper()
                password_cripto = str(password_cripto)

                if password_cripto == ds_senha_banco and nm_user_bd == user.upper():
                    response = nm_user
                elif password_cripto != ds_senha_banco:
                    response = 400
            else:
                response = 404
        except Exception as e:
            response = jsonify({"message":str(e)}),500
        finally:
            return response

class applicant_usecase:
    def __init__(self):
        self.applicant_repo = repo.applicant()

    def load_applicant(self,nr_cpf):
        try:
            if nr_cpf:
                resp = self.applicant_repo.search_applicant(nr_cpf)
                if resp is None:
                    response = jsonify({"message":"CPF Não localizado!"}),404
                else:
                    response = jsonify(resp),200
            else:
                response = jsonify({"message:":"Informe um cpf válido!"}),400
        except Exception as e:
            response = jsonify({"message:":str(e)}),500
        
        finally:
            return response

class orders:
    def __init__ (self):
        self.orders_repo = repo.Orders()

    def post_order(self,aware_p,requester_p,number_p,mat_p,cd_sector_p,occurrence_date_p,reason_p,component_p):
        try:
            print(aware_p,requester_p,number_p,mat_p,cd_sector_p,occurrence_date_p,reason_p,component_p)
            if aware_p and requester_p and number_p and mat_p and cd_sector_p and occurrence_date_p and reason_p and component_p:
                resp = self.orders_repo.post_justify_order(aware_p,requester_p,number_p,mat_p,cd_sector_p,occurrence_date_p,reason_p,component_p)

                if resp is None:
                    response = jsonify({"message": "Não foi possível gerar a ordem de serviço com os dados informados!"}),400
                elif resp:
                    response = jsonify({"order":resp}),200
            elif aware_p == False:
                response = jsonify({"message": "Termo de aceite não confirmado!"}),403
            else:
                response = jsonify({"message":"Possuem dados que não estão preenchidos de forma correta."}),400
        except Exception as e:
            response = jsonify({"message":str(e)}),500
        finally:
            return response

    def get_sector(self):
        try:
            sectors = self.orders_repo.get_sector()
            if sectors is None:
                response = jsonify({"message":"Não foi possível buscar os setores."}),400
            else:
                response = jsonify(sectors),200
        except Exception as e:
            response = jsonify({"message":str(e)}),500
        finally:
            return response
        
    def orders_pendents(self,nm_user):
        try:
            if nm_user:
                result_orders = self.orders_repo.get_orders_pendents(nm_user)
                response = jsonify([{"date_order": row[0], 
                                     "number": row[1], 
                                     "requester": row[2], 
                                     "location": row[3], 
                                     "damage": row[4], 
                                     "contact": row[5], 
                                     "group": row[6], 
                                     "describe": row[7], 
                                     "date_occurrence": row[8]}for row in result_orders])
                if response is None:
                    response = jsonify({"message":"Não foram localizadas nenhuma ordem pendente para este usuário."}),404
        except Exception as e:
            response = jsonify({"message":str(e)})
        finally:
            return response

    def action_order(self,nm_user,nr_order,ds_treatment, ds_observation,ie_approve):
        try:
            if nm_user and nr_order and ds_treatment and ds_observation and ie_approve is not None:
                if ie_approve == True:
                    response = self.orders_repo.approve_justification(nm_user,nr_order,ds_treatment, ds_observation)
                    response = jsonify({"message":response}),200
                elif ie_approve == False:
                    response = self.orders_repo.disapprove_justification(nm_user,nr_order,ds_observation)
                    response = jsonify({"message":response}),200
            else:
                response = jsonify({"message":"Há campos não preenchidos!"}),400
        except Exception as e:
            response = jsonify({"message":str(e)}),500
        finally:
            return response
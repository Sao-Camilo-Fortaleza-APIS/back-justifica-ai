import repository as repo
from flask import jsonify

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
                response = jsonify({"sectors":sectors})
        except Exception as e:
            response = jsonify({"message":str(e)})
        finally:
            return response
        
    def orders_pendents(self,nm_user):
        try:
            if nm_user:
                result_orders = self.orders_repo.get_orders_pendents(nm_user)
                response = jsonify([{"date_order": row[0], "number": row[1], "requester": row[2], "location": row[3], "damage": row[4], "contact": row[5], "group": row[6], "describe": row[7]}for row in result_orders])
                if response is None:
                    response = jsonify({"message":"Não foram localizadas nenhuma ordem pendente para este usuário."}),404
        except Exception as e:
            response = jsonify({"message":str(e)})
        finally:
            return response

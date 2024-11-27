import os
import usecase
#import socket
from flask import Flask,jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from flask_jwt_extended import (JWTManager, create_access_token)
import datetime
import logging

load_dotenv()

# Configurar o logger para exibir mensagens no stdout
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)  # Nível de logging: INFO, DEBUG, WARNING, ERROR, etc.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

PORT_API = os.getenv("PORT_API")

app = Flask(__name__)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=12)
#app.config['JWT_SESSION_COOKIE'] = True
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Define que o token será armazenado em cookies
app.config['JWT_COOKIE_SECURE'] = False  # Apenas True se usar HTTPS
#app.config['JWT_COOKIE_HTTPONLY'] = True  # Torna o cookie HttpOnly

jwt = JWTManager(app)
CORS(app, supports_credentials=True)

## LOGIN ##
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get("username")
        password = request.json.get("password")

        login_use_case = usecase.LoginUseCase()
        response = login_use_case.check_credentials(user=username,pwd=password)
        if response == 400:
            return jsonify({"message":"Usuário ou senha incorreto!"}),400
        elif response == 404:
            return jsonify({"message":"Usuário/Senha não localizado!"}),404
        else:
            access_token = create_access_token(identity=response)
            return jsonify({"token":access_token,"user":response}),200
    except Exception as e:
        return jsonify({"message": str(e)}),500

## LOCALIZADORES ##
@app.route('/applicant/information/<cpf>', methods=['GET'])
def load_applicant_information(cpf):
    applicant_us = usecase.applicant_usecase()
    try:
        response = applicant_us.load_applicant(cpf)

    except Exception as e:
        response = jsonify({"message":str(e)}),500

    finally:
        app.logger.info(response)
        return response
    
@app.route("/sectors", methods=["GET"])
def get_setor():
    repo_order = usecase.orders()
    try:
        response = repo_order.get_sector()
    except Exception as e:
        response = jsonify({"message":str(e)}),500
    finally:
        app.logger.info(response)
        return response

@app.route("/justification/pendents/<nm_user>", methods=['GET'])
#@jwt_required()
def justification_pendents(nm_user):
    order_usecase = usecase.orders()
    try:
        response = order_usecase.orders_pendents(nm_user)
    except Exception as e:
        response = jsonify({"message":str(e)}),500
    finally:
        app.logger.info(response)
        return response

## AÇÕES ORDENS ##
@app.route('/justification/open', methods=['POST'])
#@jwt_required()
def open_order_serv():
    order_usecase = usecase.orders()
    try:
        component_p = request.json.get("complement")
        requester_p = request.json.get("id_tasy")
        number_p = request.json.get("phone")
        mat_p = request.json.get("mat")
        cd_sector_p = request.json.get("id_sector")
        occurrence_date_p = request.json.get("date_occurrence")
        reason_p = request.json.get("reason")
        aware_p = request.json.get("is_aware")

        response = order_usecase.post_order(aware_p,requester_p,number_p,mat_p,cd_sector_p,occurrence_date_p,reason_p,component_p)

    except Exception as e:
        response = jsonify({"message":str(e)}),50

    finally:
        app.logger.info(response)
        return response
    
@app.route('/justification/manager/action', methods=['POST'])
#@jwt_required
def action_manager():
    order_usecase = usecase.orders()
    try:
        nm_user = request.json.get("user")
        nr_order = request.json.get("order")
        ds_treatment = request.json.get("treatment") 
        ds_observation = request.json.get("observation")
        ie_approve = request.json.get("approve")

        response = order_usecase.action_order(nm_user,nr_order,ds_treatment, ds_observation,ie_approve)
    except Exception as e:
        response = jsonify({"message": str(e)}),501
    finally:
        app.logger.info(response)
        return response

# Inicie a aplicação
if __name__ == "__main__":
    app.run(ssl_context=('certs/nginx.crt','certs/nginx.key'), host='0.0.0.0', port=PORT_API, debug=True)

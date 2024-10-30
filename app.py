import os
import usecase
#import socket
from flask import Flask,jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
#from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity,set_access_cookies, unset_jwt_cookies)

load_dotenv()

PORT_API = os.getenv("PORT_API")

app = Flask(__name__)


CORS(app, supports_credentials=True)

## LOCALIZADORES ##
@app.route('/applicant/information/<cpf>', methods=['GET'])
def load_applicant_information(cpf):
    applicant_us = usecase.applicant_usecase()
    try:
        response = applicant_us.load_applicant(cpf)

    except Exception as e:
        response = jsonify({"message":str(e)}),500

    finally:
        return response
    
@app.route("/sectors", methods=["GET"])
def get_setor():
    repo_order = usecase.orders()
    try:
        response = repo_order.get_sector()
    except Exception as e:
        response = jsonify({"message":str(e)}),500
    finally:
        return response

@app.route("/justification/pendents/<nm_user>", methods=['GET'])
def justification_pendents(nm_user):
    order_usecase = usecase.orders()
    try:
        response = order_usecase.orders_pendents(nm_user)
    except Exception as e:
        response = jsonify({"message":str(e)}),500
    finally:
        return response

## AÇÕES ORDENS ##
@app.route('/justification/open', methods=['POST'])
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
        return response

# Inicie a aplicação
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT_API, debug=True)

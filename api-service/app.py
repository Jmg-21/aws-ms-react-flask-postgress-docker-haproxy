from flask import Flask
from flask_restful import Resource, reqparse, request , Api
from flask import request
from flask_httpauth import HTTPBasicAuth 
import jwt,json,os,datetime,time,random,base64 
from flask_jwt_extended import JWTManager
from functools import wraps
from itertools import chain 
from database import Database  

from api.upload_agency import ApiUploadAgency
from api.upload_skus import ApiUploadSKUs
from api.upload_category import ApiUploadCategory
from api.upload_category_refs import ApiUploadCategoryRefs
from api.upload_area import ApiUploadArea
from api.upload_chain import ApiUploadChain
from api.upload_stores import ApiUploadStores
from api.upload_users import ApiUploadUsers
from api.upload_users_schedules import ApiUploadUsersSchedules
from api.auth import ApiAuth
from api.skus import ApiGetSKUs
from api.latestupdates import ApiLatestUpdates
from api.appversion import ApiAppVersion
from api.stores import ApiGetAllStores,ApiGetStoreSKUs,ApiGetAssignUsersInStore
from api.category import ApiGetCategory
from api.user_stores_skus import ApiGetUserStoresSKU
from api.announcement import ApiGetAnnUsers,ApiGetAnnAll
from api.video_access import ApiGetVideoAccessUser

from api.users import ApiGetUserHeirarchyAC,ApiGetUserHeirarchyACSUP
 
from api.m_changdayoff import ApiPostChangeDayoff,ApiGetChangedayOff,ApiPostConfirmChangeDayoff
from api.m_attendance import ApiPostTeamAttendance,ApiPostIndividualAttendance,ApiGetAttendanceACACSUP
from api.logs_mobile import ApiPostLogsMobile
from api.m_breaks import ApiPostBreaks
from api.m_file_leave import ApiPostFileLeave,ApiGetLeavePerMerch,ApiPostConfirmLeave
from api.m_facings import ApiPostFacings
from api.m_mcp import ApiPostMCP,ApiPostTCP,ApiGetMCPPending,ApiGetMCPNotPending,ApiPostMCPChangeRequest,ApiPostConfirmRequest
from api.m_osa import ApiPostOSA
from api.m_planograms import ApiPostPlanograms
from api.m_promo_compet_acts import ApiPostPromoCompetActs
from api.m_storeaudit import ApiPostStoreAuditData,ApiPostStoreAuditImages
from api.m_over_time import ApiPostOvertime,ApiGetPendingOT

from utils import BASE_API_URI,server_generated_id,UPLOAD_FOLDER_PHOTO 

app = Flask(__name__)
jwt = JWTManager()
api = Api(app)
jwt.init_app(app)
auth = HTTPBasicAuth()
app.config['SECRET_KEY'] = 'mykey'

USER_DATA = {"admin":"admin"}
# dbconfig = {
#     'dbname':'sales_track_v2', 
#     'user':'postgres',
#     'host':'db.pcrwpfgzubsfyfbrczlj.supabase.co', 
#     'password':'jmgtechplays21x', 
#     'connect_timeout':'3',
#     'options':'-c statement_timeout=5000000'            
#     } 

@auth.verify_password
def verify(username, password):
    if not (username and password):
        return False
    return USER_DATA.get(username) == password

class Login(Resource): 
    @auth.login_required
    def get(self):
        token = jwt.encode({
            'user':request.authorization.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),

        }, app.config['SECRET_KEY'])

        return json.dumps({
            'token':token.decode('UTF-8')
        }, indent=3)



def verify_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('token', None)
        if token is None:
            return {"Message":"Your are missing Token"}
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return {"Message":"Token is Missing or invalid" + str(e)}
    return decorator


class HelloWorld(Resource):
    @verify_token
    def get(self):
        return json.dumps({"Messagesssssss ":"ok "})
class UPFILE(Resource):
    def post(self):

        json_dict = request.get_json(force=True, silent=True)
        x = len(json_dict) 
        photo_name = []
        for i in chain(range(0, x)): 
            use_id = server_generated_id() 
            if json_dict[i]['photo'] !=".":
                with open(os.path.join(UPLOAD_FOLDER_PHOTO, use_id + ".jpg"), "wb") as fh:
                    photo_name.append(str(UPLOAD_FOLDER_PHOTO + use_id + ".jpg"), )
                    fh.write(base64.b64decode(json_dict[i]['photo']))
            else:
                print('no photo')

        list = os.listdir(UPLOAD_FOLDER_PHOTO)
        number_files = len(list) 

        print('json_dict > ',json_dict , number_files)
        return json.dumps({"FILE ":"ok "})


class STATUS(Resource):
    def get(self):    
        # data = conn.execute('select version()') 
        data = []
        print('result',data) 
        return {"result ":data}


api.add_resource(Login, '/api/login')
api.add_resource(HelloWorld, '/api/verify')
api.add_resource(UPFILE, '/api/upload')
api.add_resource(STATUS, '/api/status')


api.add_resource(ApiAuth, BASE_API_URI + '/login_api') 

# GET REQUEST
api.add_resource(ApiLatestUpdates, BASE_API_URI +'/get/latest_store_sku_category_ref/<string:userid>')
api.add_resource(ApiGetSKUs, BASE_API_URI + '/get/sku')
api.add_resource(ApiAppVersion, BASE_API_URI + '/get/latest/app-version')
api.add_resource(ApiGetAllStores, BASE_API_URI + '/get/store_sku_50')
api.add_resource(ApiGetCategory, BASE_API_URI + '/get/category_api')
api.add_resource(ApiGetStoreSKUs, BASE_API_URI + '/get/store_api/<string:storeid>')
api.add_resource(ApiGetAssignUsersInStore, BASE_API_URI + '/get/assigned_user_in_store_api/<string:storeid>')
api.add_resource(ApiGetUserStoresSKU, BASE_API_URI + '/get/sku_per_store_lists/<string:userid>')
api.add_resource(ApiGetUserHeirarchyACSUP, BASE_API_URI + '/get/users_heirarchy_ac_acsup/<string:userid>')
api.add_resource(ApiGetUserHeirarchyAC, BASE_API_URI + '/get/users_heirarchy_ac/<string:userid>')

api.add_resource(ApiGetMCPNotPending, BASE_API_URI + '/get/mcp_not_pending/<string:userid>')
api.add_resource(ApiGetMCPPending, BASE_API_URI + '/get/mcp_pending/<string:userid>')
api.add_resource(ApiGetPendingOT, BASE_API_URI + '/get/request_ot/<string:userid>')

api.add_resource(ApiGetVideoAccessUser, BASE_API_URI + '/get/video_access/<string:userid>')
api.add_resource(ApiGetLeavePerMerch, BASE_API_URI + '/get/file_leave_per_mechandiser/<string:userid>')
api.add_resource(ApiGetChangedayOff, BASE_API_URI + '/get/changed_dayoff/<string:userid>')
api.add_resource(ApiGetAttendanceACACSUP, BASE_API_URI + '/get/attendance_ac_acsup/<string:userid>')
api.add_resource(ApiGetAnnAll, BASE_API_URI + '/get/announcements_for_all/')
api.add_resource(ApiGetAnnUsers, BASE_API_URI + '/get/Announcements_for_users/<string:userid>')

# POST REQUEST
api.add_resource(ApiPostMCPChangeRequest, BASE_API_URI + '/update/mcp_api')
api.add_resource(ApiPostConfirmRequest, BASE_API_URI + '/update/confirm_mpc')

api.add_resource(ApiPostMCP, BASE_API_URI + '/insert/mcp_api') 
api.add_resource(ApiPostOSA, BASE_API_URI + '/insert/shelf_availability_api')  
api.add_resource(ApiPostFacings, BASE_API_URI + '/insert/facings_api') 
api.add_resource(ApiPostPlanograms,  BASE_API_URI + '/insert/planograms_api') 
api.add_resource(ApiPostLogsMobile, BASE_API_URI + '/insert/tbl_logs_api') 

api.add_resource(ApiPostFileLeave, BASE_API_URI + '/insert/file_leave_api') 
api.add_resource(ApiPostConfirmLeave, BASE_API_URI + '/insert/confirmation_file_leave_api') 

api.add_resource(ApiPostChangeDayoff, BASE_API_URI + '/insert/change_dayoff_api') 
api.add_resource(ApiPostConfirmChangeDayoff, BASE_API_URI +'/insert/confirm_change_dayoff_api')

api.add_resource(ApiPostBreaks, BASE_API_URI + '/insert/break_time_api') 
api.add_resource(ApiPostTeamAttendance, BASE_API_URI + '/insert/team_attendance_api') 
api.add_resource(ApiPostPromoCompetActs, BASE_API_URI + '/insert/competitors_promotion_api') 
api.add_resource(ApiPostStoreAuditData, BASE_API_URI + '/insert/store_audit_api')
api.add_resource(ApiPostStoreAuditImages, BASE_API_URI +'/insert/store_audit_media_api')
api.add_resource(ApiPostTCP, BASE_API_URI +'/insert/tcp_api')
api.add_resource(ApiPostIndividualAttendance, BASE_API_URI +'/insert/individual_attendance_api')
api.add_resource(ApiPostOvertime, BASE_API_URI +'/insert/request_over_time_api')

# API UPLOADS
api.add_resource(ApiUploadCategoryRefs, '/api/upload/template/category_reference')
api.add_resource(ApiUploadCategory, '/api/upload/template/category')
api.add_resource(ApiUploadSKUs, '/api/upload/template/skus')
api.add_resource(ApiUploadUsers, '/api/upload/template/users')
api.add_resource(ApiUploadArea, '/api/upload/template/area')
api.add_resource(ApiUploadChain, '/api/upload/template/chain')
api.add_resource(ApiUploadAgency, '/api/upload/template/agency')
api.add_resource(ApiUploadStores, '/api/upload/template/stores')
api.add_resource(ApiUploadUsersSchedules, '/api/upload/template/users_schedules') 

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True,host="0.0.0.0",port=port)
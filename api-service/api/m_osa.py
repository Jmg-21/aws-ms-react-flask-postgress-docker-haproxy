from flask_restful import Resource,request
from utils import server_generated_id
from database import Database  
from itertools import chain 
import psycopg2 

class ApiPostOSA(Resource):
    def post(self):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try: 

            x = len(json_dict)
            data = [] 

            for i in chain(range(0, x)):
                userid = json_dict[i]['tbluserid']
                storeid =  json_dict[i]['tblstoreid']
                mobile =  json_dict[i]['tblstoreid']
                
                gid = json_dict[i]['mobile_generated_id'] 
                mobile_id = server_generated_id() if gid in ('.','') else gid
                created = json_dict[i]['date_created'] 
                updated = json_dict[i]['date_updated'] 
                
                for j in chain(range(0, len(json_dict[i]['sku']))):
                    tblskuid = json_dict[i]['sku'][j]['tblskuid'] 
                    availability = json_dict[i]['sku'][j]['availability'] 
                    sku_id = mobile_id + tblskuid
                    data.append((userid,storeid,mobile_id,tblskuid,availability,sku_id ,created,updated ))

            print(data) 
            args_str = ','.join(['%s'] * len(data)) 
            query = conn.mogrify("""
                insert into m_osa (tbluserid,tblstoreid,mobile_generated_id,tblskuid,availability,sku_generated_id,date_created,date_updated) values {}
                ON CONFLICT (tbluserid,tblstoreid,tblskuid,date_created) DO NOTHING;
                """.format(args_str) , data , commit=True) 
        
            return {'status' : 'success', 'message' : 'success'}

        except psycopg2.ProgrammingError as exc:
            conn.rollback()
            return {'status' : 'failed', 'message' : str(exc)}
            
        except psycopg2.ProgrammingError as exc:
            return {'status' : 'failed', 'message' : str(exc)}
            
        except BaseException as e:
            return {'status' : 'failed', 'message' : str(e)}
        except Exception as e:
            x = str(e)
            x.replace('\n', '')
            return {'status' : 'failed', 'message' : str(x)}
        finally:
            print("completed")


def contructed(data):

    # data['sku']['tblstoreid'] = data['tblstoreid']
    # data['sku']['tbluserid'] = data['tbluserid']
    # data['sku']['mobile_generated_id'] = data['mobile_generated_id']
    # data['sku']['date_created'] = data['date_created']
    # data['sku']['date_updated'] = data['date_updated']
    data['sku']['sku_generated_id'] = server_generated_id()

    return data['sku']
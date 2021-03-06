import os,base64
from flask_restful import Resource,request 
from utils import server_generated_id,UPLOAD_FOLDER_PHOTO
from database import Database  
from itertools import chain 
import psycopg2 



class ApiPostIndividualAttendance(Resource):
    def post(self):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try: 

            x = len(json_dict)
            data = []
            for i in chain(range(0, x)):  
                use_id = server_generated_id() 
                if json_dict[i]['base64_string'] !=".":
                    with open(os.path.join(UPLOAD_FOLDER_PHOTO, use_id + ".jpg"), "wb") as fh: 
                        fh.write(base64.b64decode(json_dict[i]['base64_string']))
                        json_dict[i]['base64_string'] = str(UPLOAD_FOLDER_PHOTO + use_id + ".jpg")
                else:
                    print('no photo')

                data.append((
                    json_dict[i]['tbluserid'],
                    json_dict[i]['tblstoreid'],
                    json_dict[i]['longitude_in'],
                    json_dict[i]['latitude_in'],
                    json_dict[i]['time_in'],
                    json_dict[i]['timein_status'], 
                    json_dict[i]['base64_string'], 
                    json_dict[i]['date_created']
                    ))

            args_str = ','.join(['%s'] * len(data)) 
            query = conn.mogrify("""
                insert into m_attendance_monitoring (tbluserid,tblstoreid,longitude_in,latitude_in,time_in,timein_status,captured_photo,date_created) values {}
                ON CONFLICT (tbluserid,tblstoreid,date_created) DO NOTHING;
                """.format(args_str) , data , commit=True) 
        
            return {'status' : 'success', 'message' : 'success'}

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

class ApiPostTeamAttendance(Resource):
    def post(self):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try: 

            x = len(json_dict)
            data = []
            for i in chain(range(0, x)): 
                
                gid = json_dict[i]['mobile_generated_id'] 
                # print('gid',str(gid))  
                json_dict[i]['mobile_generated_id'] = server_generated_id() if gid in ('.','',None) else gid
                # print('mobile_generated_id',json_dict[i]['mobile_generated_id'])

                early_file = "No"
                mobile_generated_id = ""
                try: 
                    early_file = json_dict[i]['early_file']
                    mobile_generated_id = json_dict[i]['mobile_generated_id']
                except Exception as e: 
                    print("apps api is not yet updated!")

                data.append((
                     json_dict[i]['tbluserid'],
                    json_dict[i]['tblstoreid'],
                    json_dict[i]['tblsingleroleid'],
                    json_dict[i]['remarks'],
                    mobile_generated_id,
                    early_file,
                    json_dict[i]['date_created'], 
                    ))

            args_str = ','.join(['%s'] * len(data)) 
            query = conn.mogrify("""
                insert into m_team_attendance (tbluserid,tblstoreid, tblsingleroleid,remarks,mobile_generated_id,early_file,date_created) values {}
                ON CONFLICT (tbluserid,mobile_generated_id) DO NOTHING;
                """.format(args_str) , data , commit=True) 
        
            return {'status' : 'success', 'message' : 'success'}

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



class ApiGetAttendanceACACSUP(Resource):
    def get(self,userid=None):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try:   
            
            cursor = conn.execute("""
            select remarks from m_team_attendance where tbluserid in ( select 
                userid as tbluserid  
                from users where userid in 
                ( 
                    select userid from users_schedules where storeid in (
                        select storeid  from users_schedules where userid = 'DPUSER001'
                    ) and userid != 'DPUSER001'
                )
            ) and date_sync::date = DATE(TO_CHAR(now(),'yyyy-mm-dd'));
            """.format(u=userid),result=True)
             
            data  = [dict(((cursor.description[i][0]), value) for i, value in enumerate(row)) for row in cursor.fetchall()]


            conso_np = list(filter(lambda att: str(att['remarks']) == 'no report', data))
            conso_present = list(filter(lambda att: str(att['remarks']) == 'present', data))
            conso_absent = list(filter(lambda att: str(att['remarks']) == 'absent', data))

            print('data',data)


            return [
                    {
                        "number_of_stores": len(data),
                        "server_id": server_generated_id("SRATT"),
                        "total_absent": len(conso_absent),
                        "total_noreport": len(conso_np),
                        "total_present": len(conso_present)
                    }
                ]

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
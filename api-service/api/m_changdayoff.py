from flask_restful import Resource,request
from utils import server_generated_id
from database import Database  
from itertools import chain 
import psycopg2 

class ApiPostChangeDayoff(Resource):
    def post(self):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try: 

            x = len(json_dict)
            data = []
            for i in chain(range(0, x)): 
                gid = json_dict[i]['mobile_generated_id'] 
                json_dict[i]['mobile_generated_id'] = server_generated_id() if gid in ('.','') else gid

                data.append((
                    json_dict[i]['tbluserid'],
                    json_dict[i]['mobile_generated_id'],
                    json_dict[i]['tblstoreid'],
                    json_dict[i]['current_day_off'],
                    json_dict[i]['new_day_off'],
                    json_dict[i]['confirm_by'],
                    json_dict[i]['confirmation'],
                    json_dict[i]['change_by_id'],
                    json_dict[i]['date_created'], 
                    ))

            args_str = ','.join(['%s'] * len(data)) 
            query = conn.mogrify("""
                insert into m_changedayoff(tbluserid,mobile_generated_id, tblstoreid, current_day_off, new_day_off, confirm_by, confirmation,change_by_id, date_created) values {}
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


class ApiPostConfirmChangeDayoff(Resource):
    def post(self):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try:  

            tbl_confirmation_change_dayoff = []  
            for c in chain(range(0, len(json_dict))): 
                tbl_confirmation_change_dayoff.append((
                    json_dict[c]['tbluserid'],
                    json_dict[c]['confirmation'],
                    json_dict[c]['confirm_by'],
                    json_dict[c]['mobile_generated_id'],
                    json_dict[c]['date_confirmed'],
                ))

                if json_dict[c]['confirmation'] == 'approved': 
                    conn.execute('UPDATE users_schedules SET day_off = \''+json_dict[c]['new_day_off']+'\',date_updated = \''+json_dict[c]['updated_date']+'\'  WHERE userid = \''+json_dict[c]['tbluserid']+'\'',commit=True)
                    conn.execute('UPDATE m_changedayoff SET confirmation = \''+json_dict[c]['confirmation']+'\', confirm_by = \''+json_dict[c]['confirm_by']+'\',  date_confirmed = \''+json_dict[c]['date_confirmed']+'\' WHERE mobile_generated_id = \''+json_dict[c]['mobile_generated_id']+'\'',commit=True)
                else:
                    conn.execute('UPDATE m_changedayoff SET confirmation = \''+json_dict[c]['confirmation']+'\', confirm_by = \''+json_dict[c]['confirm_by']+'\',  date_confirmed = \''+json_dict[c]['date_confirmed']+'\' WHERE mobile_generated_id = \''+json_dict[c]['mobile_generated_id']+'\'',commit=True)
                    
            
            str_args = ','.join(['%s'] * len(tbl_confirmation_change_dayoff))
            conn.mogrify('INSERT INTO confirm_changedayoff(tbluserid, confirmation, confirm_by, mobile_generated_id, date_confirmed) VALUES {}'.format(str_args), tbl_confirmation_change_dayoff,commit=True)
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


class ApiGetChangedayOff(Resource):
    def get(self,userid=None):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try:  
            data = []
            user = conn.execute('SELECT roleid as tblsingleroleid,agencyid FROM users WHERE userid = \'{}\''.format(userid) ,result=True )

            tblsingleroleid = [dict(((user.description[i][0]), value) for i, value in enumerate(row)) for row in user.fetchall() if row]

            if len(tblsingleroleid) !=0:
                if int(tblsingleroleid[0]['tblsingleroleid']) == 8:
                    print('request for 8 manager')
                    data =  []

                elif int(tblsingleroleid[0]['tblsingleroleid']) == 6:
                    data = [] 
                elif int(tblsingleroleid[0]['tblsingleroleid']) == 5:
                    item = conn.execute("""
                        select 
                        tbluserid, 
                        (select CONCAT(trim(firstname),' ',trim(lastname)) from users where userid = m_changedayoff.tbluserid ) AS employee_name, 
                        tblstoreid,
                        (select name from stores where storeid = m_changedayoff.tblstoreid) as store_name,
                        current_day_off,
                        new_day_off,
                        confirmation,
                        confirm_by,
                        mobile_generated_id,
                        change_by_id,
                        to_char(date_created,'yyyy-mm-dd HH24:MI:SS') AS date_created
                        from m_changedayoff where tbluserid in (
                            select userid as tbluserid from users where userid in (
                            select  userid  from users where userid in 
                            ( 
                                select userid from users_schedules where storeid in (
                                    select storeid  from users_schedules where userid = '{u}'
                                ) and userid != '{u}'
                            )
                            ) and roleid = '6'
                        ) and date_sync::date >= now()::date - INTERVAL '3 DAY' 
                        """.format(u=userid),result=True)
                    data =  [dict(((item.description[i][0]), value) for i, value in enumerate(row)) for row in item.fetchall() if row]

            return data

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

from flask_restful import Resource,request
from utils import server_generated_id
from database import Database  
from itertools import chain 
import psycopg2 


class ApiGetAnnUsers(Resource):
    def get(self,userid=None):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try:  
             
            return []

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


class ApiGetAnnAll(Resource):
    def get(self):

        conn = Database() 
        json_dict = request.get_json(force=True, silent=True)
        try:  
                # Wed, 14 Jul 2021 00:00:00 GMT
            data = conn.execute("""
                SELECT id as tblannouncementsid, 
                (select CONCAT(firstname,\' \',lastname) from users where userid = announcements.tbluserid)  AS name, 
                (select userrole from users,users_role where users.roleid = users_role.roleid AND userid = announcements.tbluserid ) AS position, 
                announcements,
                to_char(announcements.date_posted,'Dy, dd Mon YYYY 00:00:00 GMT') as date_posted 
                FROM announcements  where announcements.date_posted::date >= now()::date - INTERVAL \'3 DAY\' AND 
                announcements.date_posted::date <= now()::date ORDER BY date_posted DESC""",result=True)
            announcements = [dict(((data.description[i][0]), value) for i, value in enumerate(row)) for row in data.fetchall() if row]
        
            return announcements

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
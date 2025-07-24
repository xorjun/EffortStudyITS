from pymongo import MongoClient
import argparse

def check_user_exists(username, db):
    user_exists = db.system.users.find_one({'user': username}) is not None
    #users = db.command('usersInfo')['users']
    #user_exists = len(users['users']) > 0
    #number_users = client.system.users.find({"username"}).count()
    if user_exists == 0:
        return False
    else: 
        return True
    
def create_user(username, pwd, roles=[{'role':'read', "db": "its_db" }]):
    client.admin.command("createUser", username, 
                            pwd=pwd, 
                            roles=roles)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Command-line argument parser for adding users to the database")
    
    # Add the --database-network argument with a default value of "localhost"
    parser.add_argument("--database-host", default="localhost", help="Specify the database network address")
    parser.add_argument("--database-port", default="27017", help="Specify the database network address")
    parser.add_argument("--useradmin-pwd", default="29820", help="Specify the userdamin password")
    parser.add_argument("--backend-service-pwd", default="SECRET")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    db_uri = f"mongodb://useradmin:{args.useradmin_pwd}@{args.database_host}:{args.database_port}/?authSource=admin"
    #client = MongoClient(host=args.database_host, port=int(args.database_port))
    client = MongoClient(db_uri)
    if not check_user_exists("useradmin", client.admin):
        if args.useradmin_pwd is None:
            print("user 'useradmin' does not exist, please give a secure password in order to create it:")
            admin_pwd = input()
        else:
            print("user 'useradmin' does not exist, it will be created using the specified useradmin_pw")
            admin_pwd = args.useradmin_pwd
        create_user(username='useradmin', pwd=admin_pwd, roles=[{ "role": "userAdminAnyDatabase", "db": "admin" }])
        print("Please add the following to your mongod.conf now:")
        print('security:\n    authorization: "enabled"')
        print("Then call this script again with the correct password")
    else:
        if not check_user_exists("backend_service_user", client.its_db):
            print("user 'backend_service_user' does not exist, it will now be created")
            #client.its_db.command("createUser", "backend_service_user", 
            #                      pwd=args.backend_service_pwd, 
            #                      roles=[{'role':'readWrite', "db": "its_db" }])
            create_user(username="backend_service_user", 
                                  pwd=args.backend_service_pwd, 
                                  roles=[{'role':'readWrite', "db": "its_db" }])


use('admin')

db.createUser(
    {
      user: "user",
      pwd: "pwd",
      roles: [ { role: "readWrite", db: "its_db" } ]
    }
  )
use admin;
db.createUser(
  {
    user: "username",
    pwd: "cc",
    roles: [
      {
        roles: ["root"],
      }
    ]
  }
);

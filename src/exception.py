class AuthError(Exception):
  code = 403
  description = "Authentication Error"

class SignUpError(Exception):
  code = 400
  description = "User with this username already exists"
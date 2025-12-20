from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from authentication.auth_dependence.token import verify_token
from .services import get_instructor_classes_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Authentication Credentials")
    return payload

@router.get("/my-classes", summary="Get My Teaching Schedule")
def get_my_classes(user: dict = Depends(get_current_user)):
    # The token contains the user's ID in the 'sub' field
    instructor_id = user.get("sub")
    
    classes = get_instructor_classes_service(instructor_id)
    return classes
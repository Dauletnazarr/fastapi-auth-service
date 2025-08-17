from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import User, UserToken
from ..schemas import RegisterIn, LoginIn, TokenPair, UserOut, ChangePasswordIn, RefreshIn
from ..security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
    hash_token, verify_token_hash
)
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email.lower(), hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    db.query(UserToken).filter(UserToken.user_id == user.id).delete()

    access = create_access_token(user.email)
    refresh, exp, jti = create_refresh_token(user.email)

    db.add(UserToken(
        user_id=user.id,
        refresh_token_hash=hash_token(refresh),
        jti=jti,
        expires_at=exp
    ))
    db.commit()

    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("typ") != "refresh":
            raise ValueError("Not a refresh token")
        subject = data["sub"]
        jti = data["jti"]
        exp = data["exp"]  # jose уже проверил exp; поле может быть datetime
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(User).filter(User.email == subject).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    token_row = db.query(UserToken).filter(UserToken.jti == jti).first()

    if not token_row:
        db.query(UserToken).filter(UserToken.user_id == user.id).delete()
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token reuse detected")

    if not verify_token_hash(payload.refresh_token, token_row.refresh_token_hash):
        db.query(UserToken).filter(UserToken.user_id == user.id).delete()
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid refresh token contents")

    if token_row.expires_at < datetime.utcnow():
        db.delete(token_row)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    db.delete(token_row)
    new_access = create_access_token(subject)
    new_refresh, new_exp, new_jti = create_refresh_token(subject)
    db.add(UserToken(
        user_id=user.id,
        refresh_token_hash=hash_token(new_refresh),
        jti=new_jti,
        expires_at=new_exp
    ))
    db.commit()

    return TokenPair(access_token=new_access, refresh_token=new_refresh)

@router.post("/logout")
def logout(payload: RefreshIn, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("typ") != "refresh":
            raise ValueError("Not a refresh token")
        jti = data["jti"]
    except Exception:
        return {"detail": "Logged out"}

    row = db.query(UserToken).filter(UserToken.jti == jti).first()
    if row:
        db.delete(row)
        db.commit()
    return {"detail": "Logged out"}

@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current

@router.post("/change-password")
def change_password(payload: ChangePasswordIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.old_password, current.hashed_password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    current.hashed_password = hash_password(payload.new_password)
    db.add(current)
    db.commit()
    return {"detail": "Password changed"}

@router.delete("/delete-account", status_code=204)
def delete_account(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(UserToken).filter(UserToken.user_id == current.id).delete()
    db.delete(current)
    db.commit()
    return {"detail": "Account deleted"}

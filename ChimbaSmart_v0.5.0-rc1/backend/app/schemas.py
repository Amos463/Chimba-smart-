from pydantic import BaseModel,Field
from typing import Any
from datetime import datetime
class RecordIn(BaseModel):
    record_uuid:str=Field(min_length=36,max_length=36); project_id:str; record_type:str; payload:dict[str,Any]
    created_at_utc:datetime; updated_at_utc:datetime
    device_id:str=Field(min_length=1,max_length=100); source_method:str='mobile'
    crs:str|None=None; content_hash:str|None=Field(None,max_length=64)  # ushauri; seva hukokotoa yake
class PushRequest(BaseModel): records:list[RecordIn]=Field(max_length=500)
class PushAck(BaseModel):
    record_uuid:str; status:str; server_version:int|None=None; conflict_id:int|None=None; detail:str|None=None; retry:bool=False
class PushResponse(BaseModel): accepted:list[PushAck]; server_time_utc:datetime
class PullResponse(BaseModel): records:list[dict]; next_cursor:int|None
class LoginIn(BaseModel): username:str=Field(max_length=100); password:str=Field(max_length=200)
class TokenOut(BaseModel):
    access_token:str
    refresh_token:str|None=None
    token_type:str='bearer'
class UserIn(BaseModel): username:str=Field(min_length=3,max_length=100); password:str=Field(min_length=8,max_length=200); role:str='field_user'
class ProjectIn(BaseModel): name:str=Field(min_length=1,max_length=200); projected_crs:str='auto'
class MemberIn(BaseModel): username:str; role:str='member'
class JobIn(BaseModel): project_id:str; engine:str; params:dict[str,Any]={}
class RefreshIn(BaseModel): refresh_token:str=Field(min_length=32,max_length=512)
class LogoutIn(BaseModel): refresh_token:str|None=Field(None,min_length=32,max_length=512)
class PasswordResetRequestIn(BaseModel): username:str=Field(min_length=3,max_length=100)
class PasswordResetConfirmIn(BaseModel): token:str=Field(min_length=32,max_length=512); password:str=Field(min_length=12,max_length=200)

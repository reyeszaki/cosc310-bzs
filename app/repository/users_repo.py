import json
from pathlib import Path

DEFAULT_DATA_PATH= Path(__file__).resolve().parents[2] /"data"/ "users.json"

class UserRepository:
    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH) -> None:
            self.data_path = Path(data_path)

    def get_all(self) -> list[dict]:
          if not self.data_path.exists():
                return []
          with self.data_path.open(encoding="utf-8") as f:
                return json.load(f)

    def _save(self,users: list[dict]) -> None:
          self.data_path.parent.mkdir(parents=True, exist_ok=True)
          with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(users,f,indent=2)

    def get_by_id(self, user_id:int) -> dict | None:
        for user in self.get_all():
            if user["id"]==user_id:
                return user
        return None

    def get_by_email(self, email:str) -> dict | None:
        for user in self.get_all():
            if user["email"]==email:
                return user
        return None

    def create(self, fields: dict) -> dict:
         users=self.get_all()
         new_id = max((user["id"] for user in users), default=0) + 1
         new_user={**fields, "id":new_id}
         users.append(new_user)
         self._save(users)
         return new_user

    def update(self,user_id:int, fields: dict) -> dict | None:
        users=self.get_all()
        for user in users:
            if user["id"]== user_id:
                user.update(fields)
                user["id"]=user_id
                self._save(users)
                return user
        return None



    


                   
    


    
              
              

            

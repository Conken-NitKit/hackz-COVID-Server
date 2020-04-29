import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import datetime

class FireStore:
  
  def __init__(self, path: str = './cred.json'):
    cred = credentials.Certificate(path)
    firebase_admin.initialize_app(cred)    
    self.db = firestore.client()

  def id_to_ref(self, collection: str, id: str) -> 'ref':
    return self.db.collection(collection).document(id)

  def ref_to_data(self, ref: 'ref') -> {}:
    return ref.get().to_dict()

  def id_to_data(self, collection: str, id: str) -> {}:
    return self.db.collection(collection).document(id).get().to_dict()

  def init_user(self, name: str) -> str:
    # ユーザーを登録
    response = self.db.collection('Users').add({
      'meeting': [],
      'meeting_admin': [],
      'name': name
    })

    return response[1].get().id

  def init_meeting(self, title: str, owner_id: str) -> str:
    
    owner_ref = self.id_to_ref(collection='Users', id=owner_id)
    # 管理者の名前を取得
    owner_name = owner_ref.get().to_dict()['name']
    # ミーティングを登録
    response = self.db.collection('Meetings').add({
      'black_list': [],
      'keywords': [],
      'members': [],
      'owner': {
        'name': owner_name,
        'id': owner_ref.get().id
      },
      'records': [],
      'title': title
    })
    # 管理者の管理ミーティングを追加
    meeting_id = response[1].get().id
    owner_ref.update({
      'meeting_admin': firestore.ArrayUnion([{
        'id': meeting_id,
        'title': title
      }])
    })
    return meeting_id

  def get_users(self, meeting_id: str) -> {}:
    return self.id_to_data(collection='Meetings', id=meeting_id)

  def get_meetings(self, user_id: str) -> {}:
    return self.id_to_data(collection='Users', id=user_id)

  def add_user(self, meeting_id: str, user_id: str) -> {}:
    meeting_ref = self.id_to_ref(collection='Meetings' ,id=meeting_id)
    user_ref = self.id_to_ref(collection='Users', id=user_id)

    meeting_data = self.ref_to_data(ref=meeting_ref)
    user_data = self.ref_to_data(ref=user_ref)

    if meeting_data['owner']['id'] is user_id:
      return 'そのユーザーは管理者です。'

    if user_id in [member['id'] for member in meeting_data['members']]:
      return 'そのユーザーは登録済みです。'

    meeting_ref.update({
      'members': firestore.ArrayUnion([{
        'id': user_id,
        'name': user_ref.get().to_dict()['name']
      }])
    })

    user_ref.update({
      'meeting': firestore.ArrayUnion([{
        'id': meeting_id,
        'title': meeting_ref.get().to_dict()['title']
      }])
    })

    return '正常に登録しました。'

  def add_record(self, meeting_id: str, user_id: str, record_data: {}) -> None:
    meeting_ref = self.id_to_ref(collection='Meetings', id=meeting_id)
    
    meeting_ref.update({'records.'+user_id: record_data})
    
    return

  def add_black_list(self, meeting_id: str, black_words: [str]) -> None:
    
    meeting_ref = self.id_to_ref(collection='Meetings', id=meeting_id)

    meeting_ref.update({'black_list': firestore.ArrayUnion(black_words)})

    return

  def update_keywords(self, meeting_id: str, keywords: [str]) -> None:
    
    meeting_ref = self.id_to_ref(collection='Meetings', id=meeting_id)

    meeting_ref.update({'keywords': keywords})

    return

if __name__ == '__main__':

  # インスタンスを作成
  my_firestore = FireStore()
  
  user_id = 'FDMjs0l3JUP6tbYzXXvk'
  meeting_id = 'DMzzRc2xqbx6lJCJvcpp'
  
  new_user_id = my_firestore.init_user(name='わたし')
  new_meeting_id = my_firestore.init_meeting(title='新規', owner_id=user_id)
  print('new_user: ', new_user_id)
  print('new_meeting: ', new_meeting_id)

  my_firestore.add_user(user_id=user_id, meeting_id=meeting_id)
  my_firestore.add_record(meeting_id=meeting_id, user_id=user_id, record_data={'a': 'a'})
  my_firestore.add_black_list(meeting_id=meeting_id, black_words= ['b', 'c'])
  my_firestore.update_keywords(meeting_id=meeting_id, keywords= ['b', 'c', 'aaa'])

  print(my_firestore.get_meetings(user_id=user_id))
  print(my_firestore.get_users(meeting_id=meeting_id))
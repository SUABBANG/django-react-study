import sqlite3

# SQL 인젝션 방지를 위한 입력값
query = "1' OR 1=1 --"
print("검색어:", query)

# SQLite 데이터베이스 연결
connection = sqlite3.connect("melon-20230906.sqlite3")
cursor = connection.cursor()
connection.set_trace_callback(print)

# 검색어 파라미터 생성
search_term = '%악뮤%'

# SQL 쿼리 수정 (파라미터화된 쿼리 사용)
sql = "SELECT * FROM songs WHERE 가수 LIKE ? OR 곡명 LIKE ?"
print(sql)
cursor.execute(sql, (search_term, search_term))

# 컬럼 이름 가져오기
column_names = [desc[0] for desc in cursor.description]

# 결과 가져오기
song_list = cursor.fetchall()

print("list size :", len(song_list))

# 결과 출력
for song_tuple in song_list:
    song_dict = dict(zip(column_names, song_tuple))
    print("{곡명} {가수}".format(**song_dict))

# 연결 종료
connection.close()

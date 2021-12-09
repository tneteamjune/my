import json

file = open("./z_address_data/data_용산구.csv")

file_list=[]      # 전체 리스트(raw data)
line_list=[]      # 라인별 리스트
line_no=[]        # 넘버링
address=[]        # 주소
latitude=[]       # 위도
longitute=[]      # 경도
status=[]         # 정좌표 or 인근좌표
address_detail=[] # 설치장소상세(e.g.가게앞)
address_type=[]   # 설치장소타입(e.g.버스정류장, 횡단보도..)
trash_type=[]     # 쓰레기통 형태
gov=[]            # 관할기관
gov_num=[]        # 관할기관 연락처

for line in file :
    file_list.append(line.strip())
del file_list[0]

for i in range(len(file_list)) :
   line_list.append(file_list[i].split(','))

for i in range(len(line_list)) :
   line_no.append(line_list[i][0])
   address.append(line_list[i][1])
   longitute.append(line_list[i][2])
   latitude.append(line_list[i][3])
   status.append(line_list[i][4])
   address_detail.append(line_list[i][5])
   address_type.append(line_list[i][6])
   trash_type.append(line_list[i][7])
   gov.append(line_list[i][8])
   gov_num.append(line_list[i][9])

for i in range(len(line_list)) :
    print('{')
    print("title:'"+ trash_type[i] +"',")
    print("latlng: new kakao.maps.LatLng("+latitude[i]+','+longitute[i]+'),')
    print("content: '"+'<div style="padding:5px;">'+address_detail[i]+"'")
    print('},')


# json data 생성
# file_path = ".test.json"
# data = {}
# data['positions'] = []
#
# for i in range(len(line_list)) :
#     data['positions'].append (
#         {
#         'title': address[i],
#         'latlng': 'new kakao.maps.LatLng('+longitute[i]+','+latitude[i]+')',
#         'content' : '<div style="padding:5px;">'+address_name[i]
#         }
#     )
# with open(file_path,'w') as outfile:json.dump(data,outfile)
# print(data)


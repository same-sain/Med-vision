import pytesseract
import ollama
import cv2
from flask import Flask
from flask_restful import Api,Resource,abort,reqparse,marshal_with,fields
from flask_sqlalchemy import SQLAlchemy
import requests

# app = Flask(__name__)
# api = Api(app)
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///medication_reminder.db'
# db = SQLAlchemy(app)

# # client side
# URL = "http://127.0.0.1:5000/med"
# response = requests.get(URL)
# message = response.json()
# print(message['data'])

# โหลดรูป
# img = cv2.imread('/home/sain/Med-vision/Med-vision/script/image/1732106712979.jpg')

# # Preprocess
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# blurred = cv2.GaussianBlur(gray, (5, 5), 0)
# thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)[1]

# # หา contour
# contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# # หาฉลากที่ใหญ่ที่สุด
# label_contour = None
# max_area = 0

# for cnt in contours:
#     area = cv2.contourArea(cnt)
#     if area > max_area:
#         max_area = area
#         label_contour = cnt

# ถ้ามีเจอ
# if label_contour is not None:
#     x, y, w, h = cv2.boundingRect(label_contour)
#     label_roi = img[y:y+h, x:x+w]  # ตัดเฉพาะฉลากออกมา
    
#     # OCR เฉพาะฉลาก
#     label_text = pytesseract.image_to_string(img, lang='tha+eng')
    # print(label_text)
text = """[โรงพยาบาลราษฎร์ขินดี @ @ 074-200200
    8315/64 วับทิพิมพ์ : 13/07/2567 18:32
    H.
    นาย วิสลิทธกร ชฎาร์ตน์
    ACEO CAPSULES RETARD 90MG                       #10
    (เอชิโอ=อะซี-เมทาชิน)
    fu ครั้งละ 1 เม็ด วันละ 1 ครั้ง หลังอาหาร เช้า
    F-3-3
    Sse)
    [ๆ
    วันหมดจายุแสกงบนผลิตภัณฑ์
    ยาลดปวด-ลดอักเสบ
    ก 4   i   2 0 ด ให้พบแพทย์ด่วน
    ยใช้ตามแพทย์สังเท่านัน ห้ามให้ผู้อื่นใช้ หากมีอาการผิดปกติ ให้พบแพ"""
        
        
    # ส่งข้อความเข้า Ollama ช่วยจัดรูปแบบ
prompt = f"""
      "{text}"
      Read above data convert to JSON format follow this example:
      {{
      drug : "<example : Paracetamol>",
      time : "<example : ทุกๆ 6 ชั่วโมง",
      limit : "<example : paracetamol>"
      meal : "<example : เช้า, เที่ยง, เย็น>"
      use : "<example : ครั้งละ 1 เม็ด>"
      }}
      """
  

response = ollama.chat(
      model='llama3.2',
      messages=[{'role': 'user', 'content': prompt}]
  )
      
formatted_text = response['message']['content']
print("\nข้อความที่ Ollama จัดรูปแบบแล้ว:")
print(formatted_text)


# # make column in sqlite database
# class MED_MODEL(db.Model):
#   id =  db.Column(db.Integer, primary_key=True)
#   hospital_name = db.Column(db.String(100), nullable =False)
#   medicine = db.Column(db.String(100), nullable =False)
#   effectiveness = db.Column(db.String(100), nullable =False)
#   instructions = db.Column(db.String(100), nullable =False)
#   meal = db.Column(db.String(100), nullable =False)
  
#   def __repr__(selt):
#     return f"med(hospital_name = {selt.hospital_name},medicine = {selt.medicine},effectiveness = {selt.effectiveness},instructions = {selt.instructions},meal = {selt.meal})"
# with app.app_context():
#   db.create_all()
  
#   # fields data
# resource_fields = {
#   "id" : fields.Integer,
#   "hospital" : fields.String,
#   "medicine" : fields.String,
#   "effectiveness" : fields.String,
#   "instructions" : fields.String,
#   "meal" : fields.String,
# }

# # request Parser
# med_add_args = reqparse.RequestParser()
# med_add_args.add_argument("instructions",type=str,required=True,help="กรุนาป้อนชื่อคำเเนะนำเป็นข้อความ")
# med_add_args.add_argument("effectiveness",type=str,required=True,help="กรุนาป้อนชื่อประสิทธิผลเป็นข้อความ")
# med_add_args.add_argument("medicine",type=str,required=True,help="กรุนาป้อนชือยาเป็นข้อความ")
# med_add_args.add_argument("hospital",type=str,required=True,help="กรุนาป้อนชื่อโรงพยาบาลเป็นข้อความ")

# # update request parser
# med_update_args = reqparse.RequestParser()
# med_update_args.add_argument("instructions",type=str,help="กรุนาป้อนข้อความคำเเนะนำที่ต้องการแก้ไข")
# med_update_args.add_argument("effectiveness",type=str,help="กรุนาป้อนชื่อประสิทธิผลที่ต้องการแก้ไขเป็นข้อความ")
# med_update_args.add_argument("medicine",type=str,help="กรุนาป้อนชือยาที่ต้องการแก้ไขเป็นข้อความ")
# med_update_args.add_argument("hospital",type=str,help="กรุนาป้อนชื่อโรงพยาบาลที่ต้องการแก้ไขเป็นข้อความ")

# class med_medication(Resource):
#     @marshal_with(resource_fields)
#     def get(selt,med_id):
#         result = MED_MODEL.query.filter_by(id = med_id).first()
#         if not result :
#           abort(404,message("NotFound"))
#           return result
      
#     @marshal_with(resource_fields)
#     def post(selt,med_id):
#         result = MED_MODEL.query.filter_by(id = med_id).first()
#         if not result :
#           abort(404,message("มีอยู่เเล้ว"))
#         args = med_add_args.parse_args()
#         med = MED_MODEL(id = med_id,hospital=args["hospital"],medicine=args["medicine"],effectiveness=args["effectiveness"],instructions=args["instructions"])
#         db.session.add(med)
#         db.session.commit()
#         return med 
    
#     @marshal_with(resource_fields)
#     def patch(self,med_id):
#         args = med_update_args.parse_args()
#         result = MED_MODEL.query.filter_by(id = med_id).first()
#         if not result :
#             abort(404,message="Not found you data")
#         if args["hospital"]:
#             result.hospital=args["hospital"]
#         if args["medicine"] :
#             result.medicine=args["medicine"]
#         if args["effectiveness"] :
#             result.effectiveness=args["effectiveness"]
#         if args["instructions"] :
#             result.instructions=args["instructions"]
#         if args["meal"] :
#             result.meal=args["meal"]
#         db.session.commit()
#         return result
    
# call 
# api.add_resource(med_medication,"/med/<int:med_id>")

# Run the app
# if __name__ == "__main__":
#     app.run(debug=True)

#  format json use for add in data base
# med_text_info={
#   "hospital": {
#     "name": "โรงพยาบาลหาดใหญ่",
#   },
#   "medicine": {
#     "name": "ซือยา",
#     "active ingredient": "Paracetamol 500 mg",
#     "dosage": "#20 เม็ด"
#   },
#   "effectiveness": {
#     "symptoms": ["ปวด", "ไข้"],
#     "description": "ยาแก้ปวด ลดไข้"
#   },
#   "instructions": {
#     "dosage": "รบประทานครั้งละ1 LNA ทุก 6 ชัวโมงเวลาปวดหรือมีไข้",
#     "precaution": "ไม่ควรใช้ยาเกิน 8 เม็ดต่อวัน"
#   },
#   "meal" : ["เช้า","เที่ยง","เย็น"]
# }
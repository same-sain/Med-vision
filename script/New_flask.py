from flask import Flask
from flask_restful import Api,Resource,abort,reqparse,marshal_with,fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///database_name.db'
db=SQLAlchemy(app)

api=Api(app)

class med_Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital = db.Column(db.String(100), nullable=False)
    medicine = db.Column(db.String(100), nullable=False)
    effectiveness = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"med(hospital={self.hospital}, medicine={self.medicine}, effectiveness={self.effectiveness} ,instructions={self.instructions} )"
with app.app_context():
    db.create_all()
    
# request Parser
med_add_args = reqparse.RequestParser()
med_add_args.add_argument("instructions",type=str,required=True,help="กรุนาป้อนชื่อคำเเนะนำเป็นข้อความ")
med_add_args.add_argument("effectiveness",type=str,required=True,help="กรุนาป้อนชื่อประสิทธิผลเป็นข้อความ")
med_add_args.add_argument("medicine",type=str,required=True,help="กรุนาป้อนชือยาเป็นข้อความ")
med_add_args.add_argument("hospital",type=str,required=True,help="กรุนาป้อนชื่อโรงพยาบาลเป็นข้อความ")

# update request parser
med_update_args = reqparse.RequestParser()
med_update_args.add_argument("instructions",type=str,help="กรุนาป้อนชื่อคำเเนะนำที่ต้องการแก้ไข")
med_update_args.add_argument("effectiveness",type=str,help="กรุนาป้อนชื่อประสิทธิผลที่ต้องการแก้ไขเป็นข้อความ")
med_update_args.add_argument("medicine",type=str,help="กรุนาป้อนชือยาที่ต้องการแก้ไขเป็นข้อความ")
med_update_args.add_argument("hospital",type=str,help="กรุนาป้อนชื่อโรงพยาบาลที่ต้องการแก้ไขเป็นข้อความ")


resource_field = {
    "id":fields.Integer,
    "hospital":fields.String,
    "medicine":fields.String,
    "effectiveness":fields.String,
    "instructions":fields.String
}


# validate request
def notFoundMed(med_id):
    # if med_id not in med_info :
        abort(404,message = "ไม่พบยาที่คุณระบุ")
# design
class Med_medication(Resource):

    @marshal_with(resource_field)
    def get(self,med_id):
        result = med_Model.query.filter_by(id = med_id).first()
        if not result:
            abort(404,message="NotFound")
        return result
        

    @marshal_with(resource_field)
    def post(self,med_id):
        result = med_Model.query.filter_by(id = med_id).first()
        if result:
            abort(409,message="it have encode yet")
        args = med_add_args.parse_args()
        med = med_Model(id = med_id,hospital=args["hospital"],medicine=args["medicine"],effectiveness=args["effectiveness"],instructions=args["instructions"])
        db.session.add(med)
        db.session.commit()
        return med 
    
    @marshal_with(resource_field)
    def patch(self,med_id):
        args = med_update_args.parse_args()
        result = med_Model.query.filter_by(id = med_id).first()
        if not result :
            abort(404,message="Not found you data")
        if args["hospital"]:
            result.hospital=args["hospital"]
        if args["medicine"] :
            result.medicine=args["medicine"]
        if args["effectiveness"] :
            result.effectiveness=args["effectiveness"]
        if args["instructions"] :
            result.instructions=args["instructions"]
        db.session.commit()
        return result
        
# call 
api.add_resource(Med_medication,"/med/<int:med_id>")

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
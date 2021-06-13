from flask import Flask
from flask_restful import Api
from controller.parkingcontroller import ParkingSlot,ParkingZone, ParkingHistory, ParkingBook, ParkingRelease
app = Flask(__name__)
api = Api(app) # link bw API and resource

api.add_resource(ParkingSlot,'/Parking/Slot')
api.add_resource(ParkingBook,'/Parking/Book')
api.add_resource(ParkingRelease,'/Parking/Release')
api.add_resource(ParkingZone,'/Parking/Zone')
api.add_resource(ParkingHistory,'/Parking/History')

app.run(port = 5000, debug=True)
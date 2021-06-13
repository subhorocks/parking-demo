import traceback
from flask_restful import Resource, reqparse,request
from parking.service.soltdetailservice import getslotdetails, postlotDetails, \
    DeleteSlot,SlotBook, zoneDetails, zoneDelete, postZoneDetails, getParkingHistory, SlotRelease
class ParkingSlot(Resource):

    def get(self):

        op,status = getslotdetails()
        if status:
            return op,200
        else:
            return {'output' : op}, 200

    def post(self):
        try:
            d = {}
            parser = reqparse.RequestParser()
            parser.add_argument('payload', type=str, required=True,location = 'json')
            payload = request.get_json()
            if payload:
                if 'ZoneId' in payload:
                    zone_Id = payload['zone_Id']
                else:
                    return 'zone_Id is missing in the payload', 400
                sid,status = postlotDetails(zone_Id)
                d['slotId'] = sid
                d['zoneId'] = zone_Id
                d['status'] = 'available'
                d['occupiedBy'] = None
                if status:
                    return d, 201
        except:
            return traceback.format_exc(), 500
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('slotId', type=int, required=True)
        slotId = request.args.get('slotId')
        slotId, status = DeleteSlot(slotId)
        if status:
            return 'slot deleted',201
        else:
            return 'No data found', 404

class ParkingBook(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('payload', type=str, required=True)
        parser.add_argument('slotId', type=int, required=True)

        slotId = request.args.get('slotId')
        payload = request.get_json()
        if payload:
            if 'status' in payload:
                status = payload['status']
            else:
                return 'status is missing in the payload', 400
            if 'zoneId' in payload:
                zoneId = payload['zoneId']
            else:
                return 'zoneId is missing in the payload', 400
            if 'occupiedBy' in payload:
                occupiedBy = payload['occupiedBy']
            else:
                return 'occupiedBy is missing in the payload', 400
            if 'vechicleNum' in occupiedBy:
                vechicleNum = occupiedBy['vechicleNum']
            else:
                return 'vechicleNum is missing in the payload', 400
            if 'name' in occupiedBy:
                name = occupiedBy['name']
            else:
                return 'name is missing in the payload', 400

            res, st = SlotBook(slotId, status, vechicleNum, name, zoneId)
            if st:
                return res, 201
            elif st == 404:
                return 'slot is in valid', 400
            elif not st:
                return 'slot is already booked', 404
class ParkingRelease(Resource):
    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument('payload', type=str, required=True)
        parser.add_argument('slotId', type=int, required=True)

        slotId = request.args.get('slotId')
        payload = request.get_json()
        if payload:
            if 'zoneId' in payload:
                zoneId = payload['zoneId']
            else:
                return 'zoneId is missing in the payload', 400
            if 'occupiedBy' in payload:
                occupiedBy = payload['occupiedBy']
            else:
                return 'occupiedBy is missing in the payload', 400
            if 'vechicleNum' in occupiedBy:
                vechicleNum = occupiedBy['vechicleNum']
            else:
                return 'vechicleNum is missing in the payload', 400
            if 'name' in occupiedBy:
                name = occupiedBy['name']
            else:
                return 'name is missing in the payload', 400

            res, st = SlotRelease(slotId, vechicleNum, name, zoneId)
            if st:
                return res, 205
            else:
                return 'slot id not exists', 404


class ParkingZone(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('zoneId', type=str, required=False)

        zoneId = request.args.get('zoneId')
        op, status = zoneDetails(zoneId)
        if status:
            return op, 200
        else:
            return 'Zone id not exists', 404
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('zoneId', type=str, required=False)
        zoneId = request.args.get('zoneId')
        op, status = zoneDelete(zoneId)
        if status:
            return 'Zone Deleted', 200
        else:
            return 'Zone id not exists', 404
    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('payload', type=str, required=True)
        payload = request.get_json()
        zoneId = payload['zoneId']
        zoneDesc = payload['zoneDesc']
        price = payload['price']
        res , status = postZoneDetails(zoneId,zoneDesc,price)
        if status:
            return payload, 201
        else:
            return 'Zone id is already exists',400

class ParkingHistory(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('startDate', type=str, required=False)
    parser.add_argument('endDate', type=str, required=False)
    parser.add_argument('pagrNum', type=int, required=False)
    parser.add_argument('pageSize', type=int, required=False)


    def get(self):
        startDate = request.args.get('startDate')
        endDate = request.args.get('endDate')
        pageNum = request.args.get('pagrNum')
        pageSize = request.args.get('pageSize')
        res, status = getParkingHistory(startDate,endDate,pageNum, pageSize)

        if status:
            return res, 200
        else:
            return "No data found", 404
from parking.DB.connector import connect
import sys
from fpdf import FPDF
import uuid

def getslotdetails():
    conn = None
    cur = None
    try:
        conn = connect()

        cur = conn.cursor()

        cur.execute(("""select sid , vehicle_num, available_status,occupiedby, 
        parking_zone from slot where available_status =  'available' order by 1 asc """))
        data = cur.fetchall()
        columns = ["solt", "vehicle_num", "available_status", "occupiedBy", "parking_zone"]
        res=[]

        if len(data)>0:
            for row in data:
                res.append(dict(zip(columns,row)))

            return res,True
        else:
            return "Parking slot Full", False

    except:
        print(sys.exc_info()[1])
    finally:
         cur.close()
         conn.close()




def postlotDetails(zone_Id):
    conn = None
    cur= None
    try:
        conn = connect()

        cur = conn.cursor()
        cur.execute((""" insert into slot (parking_zone) values (%s) RETURNING sid"""), (zone_Id,))
        conn.commit()
        sid = cur.fetchone()[0]
        return sid, True
    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()

def DeleteSlot(slotId):
    conn = None
    cur = None
    try:
        conn = connect()

        cur = conn.cursor()
        cur.execute(("""select sid from slot where sid = %s """),(slotId,))
        data = cur.fetchone()
        if data:
            cur.execute((""" delete from slot where sid = %s """), (slotId,))
            conn.commit()
            return slotId, True
        else:
            return None, False

    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()


def SlotBook(slotId,status,vechicleNum,name,zoneId):
    conn = None
    cur = None
    try:
        d = {}
        conn = connect()

        cur = conn.cursor()
        cur.execute(( """ select sid from slot where sid = %s"""),(slotId,))
        data= cur.fetchone()
        if data is not None:
            cur.execute(("""select sid from slot where sid = %s and available_Status <> 'parked' """), (slotId,))
            data = cur.fetchone()
            if data:
                if status is not None and status =='parked'.lower():
                        cur.execute((""" update slot set available_status = %s,vehicle_num = %s, occupiedby = %s,
                         parking_zone = %s where sid = %s """), (status,vechicleNum,name,zoneId,slotId,))
                        conn.commit()
                        d['slotId'] = slotId
                        d['zoneId'] = zoneId
                        d['status'] = status
                        d['occupiedBy'] = name
                        d['vehicle_num'] = vechicleNum
                        cur.execute(("""insert into parking_history (sid,vehicle_num, 
                        occupiedby,start_time) values (%s,%s, %s, now())"""),(slotId,vechicleNum,name))
                        conn.commit()
                        return d, True
            else:
                return '', False
        else:
            return 'slot is not exists', 404
    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()

def SlotRelease(slotId, vechicleNum, name, zoneId):
    conn = None
    cur = None
    try:
        d= {}
        conn = connect()

        cur = conn.cursor()
        cur.execute(("""select sid from slot where sid = %s """), (slotId,))
        data = cur.fetchone()
        if data:
            # cur.execute(("""select end_time,start_time from parking_history
            #                                     where sid = %s and start_time is not null and end_time is null"""),
            #             (slotId,))
            # t = cur.fetchone()
            # print(t)
            # difference = (t[0] - t[1])
            cur.execute((""" update slot set available_status = 'available'
                                                ,vehicle_num = null, occupiedby = null,
                                                 parking_zone = null where sid = %s """), (slotId,))
            conn.commit()

            cur.execute(("""update parking_history set end_time = now(), vehicle_num = %s,occupiedby = %s
                                     where sid = %s and end_time is null """), (vechicleNum, name, slotId))
            conn.commit()

            cur.execute(("""select base_amount from price where parking_zone = %s """), (zoneId,))
            base_amount = cur.fetchone()

            cur.execute(("""select end_time,start_time from parking_history 
                                                            where sid = %s and start_time is not null and end_time is not null
                                                            order by end_time desc limit 1"""),
                        (slotId,))
            t = cur.fetchone()
            print(t)
            difference = (t[0] - t[1])

            # print(difference)
            hr_val = (difference.total_seconds()) / 3600
            # print(hr_val, base_amount)
            amount = round((base_amount[0] * hr_val), 2)
            # print(amount)

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=15)
            pdf.cell(200, 30, txt="Bill Details: ",
                     ln=1, align='C')
            pdf.cell(200, 10, txt="Vehicle Num: " + vechicleNum,
                     ln=1, align='L')
            pdf.cell(200, 10, txt="Slot Booked On: " + t[1].strftime('%Y/%m/%d %H:%M:%S'),
                     ln=1, align='L')
            pdf.cell(200, 10, txt="Slot Released On: " + t[0].strftime('%Y/%m/%d %H:%M:%S'),
                     ln=1, align='L')
            pdf.cell(200, 10, txt="Parking Zone ID: " + zoneId,
                     ln=1, align='L')
            pdf.cell(200, 10, txt="Slot Number: " + str(slotId),
                     ln=1, align='L')
            pdf.cell(200, 10, txt="Charged Amount Rs. :" + str(amount),
                     ln=1, align='L')
            v = str(uuid.uuid1())
            f = v + '.pdf'
            pdf.output(f)
            d['slotId'] = slotId
            d['zoneId'] = zoneId
            d['status'] = 'available'
            d['occupiedBy'] = name
            d['vehicle_num'] = vechicleNum
            d['fileName'] = f
            return d, True
        else:
            return '', False
    except:
        print(sys.exc_info()[1])

    finally:
        cur.close()
        conn.close()


def zoneDetails(zoneId):
    cur = None
    conn = None
    try:
        conn = connect()

        cur = conn.cursor()
        if zoneId is not None:
            cur.execute(("""select parking_zone, zone_desc, base_amount from price where parking_zone = %s """), (zoneId,))
        else:
            cur.execute(("""select parking_zone, zone_desc, base_amount from price  """))
        data = cur.fetchall()
        #print(data)
        if data:
            columns = ["parking_zone", "zone_desc", "base_price_per_hour"]
            res = []

            for row in data:
                #print(row)
                res.append(dict(zip(columns, row)))
            #print(res)
            return res, True
        else:
            return '', False
    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()

def zoneDelete(zoneId):
    conn = None
    cur=None
    try:

        conn = connect()

        cur = conn.cursor()
        if zoneId is not None:
            cur.execute(("""select parking_zone, zone_desc, base_amount from price where parking_zone = %s """),
                        (zoneId,))
            data = cur.fetchall()
            if data:
                cur.execute(("""delete from price where parking_zone = %s """),
                            (zoneId,))
                conn.commit()
                return '', True
            else:
                return '' , False
    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()

def postZoneDetails(zoneId,zoneDesc,price):
    conn = None
    cur = None
    try:
        conn = connect()

        cur = conn.cursor()
        cur.execute((""" select parking_zone from price where parking_zone = %s """), (zoneId,))
        data = cur.fetchall()
        if len(data)==0:
            cur.execute((""" insert into price (parking_zone, zone_desc, base_amount) 
            values (%s, %s, %s)"""),(zoneId,zoneDesc,price))
            conn.commit()
            return '' , True
        else:
            return '', False
    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()

def getParkingHistory(startDate,endDate,pageNum, pageSize):
    conn = None
    cur = None
    try:
        conn = connect()
        cur = conn.cursor()


        if startDate and endDate is None and (pageNum and pageSize) is not None:
            #print("block 1")
            offset = int(pageNum) * int(pageSize)
            limit = pageSize
            cur.execute((""" select id, sid, vehicle_num, occupiedby, start_time,end_time 
            from parking_history where start_time::date >= %s and end_time is null order by end_time desc limit %s offset %s"""), (startDate,limit,offset))
        elif (startDate and endDate) and (pageNum and pageSize) is not None:
            offset = int(pageNum) * int(pageSize)
            limit = pageSize
            cur.execute((""" select id, sid, vehicle_num, occupiedby, start_time,end_time 
            from parking_history where start_time::date >= %s and end_time::date <= %s and 
            end_time is not null order by end_time desc limit %s offset %s"""),
                        (startDate,endDate,limit,offset))
        else:
            cur.execute(""" select id, sid, vehicle_num, occupiedby, start_time,end_time from parking_history 
            order by end_time desc """)
        data = cur.fetchall()

        if data:
            columns = [ "BillID","slotId","veichle_num","occupiedBy","start_time", "end_time"]
            res = []
            for row in data:
                if row[5] is not None:

                    (billId,slotId,veichle_num,occupiedBy,s_t , e_t) = (row[0],row[1],row[2],
                                                                        row[3],row[4].strftime('%Y/%m/%d %H:%M:%S'),
                                                                        row[5].strftime('%Y/%m/%d %H:%M:%S'))
                    res.append(dict(zip(columns,(billId,slotId,veichle_num,occupiedBy,s_t , e_t))))
                else:
                    # print(row)
                    (billId, slotId, veichle_num, occupiedBy, s_t, e_t) = (row[0], row[1], row[2],
                                                                           row[3],
                                                                           row[4].strftime('%Y/%m/%d %H:%M:%S'),
                                                                           '')
                    res.append(dict(zip(columns, (billId, slotId, veichle_num, occupiedBy, s_t, e_t))))
                #print(res)
            return res, True
        else:
            return '', False

    except:
        print(sys.exc_info()[1])
    finally:
        cur.close()
        conn.close()

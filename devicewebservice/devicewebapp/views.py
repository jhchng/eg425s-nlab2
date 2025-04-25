from django.shortcuts import render
import pymongo
import json
from datetime import datetime as dt

#for post request with query
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    return render(request,'devicewebapp/index.html')

def viewdevices(request):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["UIOT"]
    mycol = mydb["Devices"]
    devconncol = mydb["DeviceConns"]

    viewdevices = []
    viewdeviceconns = []

    for device in mycol.find():
        viewdevices.append(device)

    for devconns in devconncol.find():
        viewdeviceconns.append(devconns)
        print(devconns)

    devdata = {'viewdevicesdata': viewdevices, 'viewdeviceconndata':viewdeviceconns}
    return render(request,'devicewebapp/viewdevices.html',context=devdata)

def devices(request,param1):
    dev_name = param1
    dtnow = dt.now()

    iotdev = { "name": dev_name, "datetime": dtnow }

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["UIOT"]
    mycol = mydb["Devices"]
    devconncol = mydb["DeviceConns"]

    viewdevices = []
    for device in mycol.find({'name':dev_name}):
        viewdevices.append(device)

    if (len(viewdevices) >= 1):
        iotdevlog={ "name": dev_name, "datetime": dtnow, "status":"updated" }
        y = devconncol.insert_one(iotdevlog)
        dev_name = "{} updated in DB".format(dev_name)
    else:
        x = mycol.insert_one(iotdev)
        iotdevlog={ "name": dev_name, "datetime": dtnow, "status":"new" }
        y = devconncol.insert_one(iotdevlog)
        dev_name = "{} device has been recorded!!".format(dev_name)

    return render(request, 'devicewebapp/devices.html', context={'data': dev_name})
    #return render(request, 'devicewebapp/devices.html', context={'data': iotdev, 'datalog': iotdevlog, 'msg_display': res_dev_name})

@csrf_exempt
def postview(request):
    if request.method == 'POST':
        #print("RequestPost Data\n{}".format(request.POST))
        #print("RequestPost Data-Body\n{}".format(request.body))
        #print("RequestPost Data-Content\n{}".format(request.content_type))
        #print("RequestPost ContentParams\n{}".format(request.content_params))
        #if request.content_type == 'application/json':
        #    inputdata = request.body.decode('utf-8')
        #    print("Json string: {}".format(inputdata))
        #    jsoninput = dict(inputdata)
        #    print("json received input:{}".format(json.loads(inputdata)))
        usrname = request.POST.get('username')
        passwd = request.POST.get('password')
        print("HTTP-POST: username:{} and password:{}".format(usrname,passwd))
        return HttpResponse("POST Request data {} with {} sent- successful".format(usrname,passwd))

    elif request.method == 'GET':
        if request.GET.get('username',''):
            #print("?username - RequestPost Data\n{}".format(request.GET))
            #print("RequestPost Data-Body\n{}".format(request.body))
            #print("RequestPost Data-Content\n{}".format(request.content_type))
            #print("RequestPost Data-Content\n{}".format(request.META))
            #print("RequestPost ContentParams\n{}".format(request.content_params))
            usrname = request.GET.get('username','')
            access_token=request.GET.get('token','')
            if access_token != "":
                print("username:{} | token:{} - HTTP-GET successful".format(usrname,access_token))
                response_data = {"username": usrname, "token received": access_token}
            else:
                print("username:{} - HTTP-GET successful".format(usrname))
                response_data = {"username": usrname, "time queried": dt.now().strftime("%d-%m-%Y %H:%M:%S")}
            return JsonResponse(response_data)
            #return HttpResponse("Request {} exist with {} - HTTP-GET successful".format(usrname,passwd))
        else:
            #print("?not username - RequestPost Data\n{}".format(request.GET))
            #print("RequestPost Data-Body\n{}".format(request.body))
            #print("RequestPost Data-Content\n{}".format(request.content_type))
            #print("RequestPost ContentParams\n{}".format(request.content_params))
            qstring=request.GET.get('search','')
            print("HTTP-GET: query string:{}".format(qstring))
            return HttpResponse("HTTP-GET: Query Done - {}".format(qstring))

    else:
        print("Error - Request is Invalid {}".format(request))
        return HttpResponse("Request {} with {} - HTTP-GET error in data".format(usrname,passwd))

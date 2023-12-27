from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restful import Resource, Api
from csv_reader import CSVReader
# instantiate the app
csvReader=CSVReader()
app = Flask(__name__)
api = Api(app)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

sampleData={}
customData={}

class SampleDataManager(Resource):
    def __init__(self):
        #fill sample data
        csvReader.preprocess_csv("ressources/rdu-weather-history.csv")
        sampleData['sampleData1']=csvReader.read_csv("ressources/rdu-weather-history.csv", "tmax")
        sampleData['sampleData2']="Second"
        sampleData['sampleData3']="Third"

    def get(self, sampleData_id):
        return {sampleData_id: sampleData[sampleData_id]}

class CustomDataManager(Resource):
    def get(self, customData_id):
        return {customData_id: customData[customData_id]}
    
    def put(self, customData_id):
        customData[customData_id] = request.get_json()
        return{customData_id: customData[customData_id]}, 201
    
api.add_resource(SampleDataManager, '/sample/<string:sampleData_id>')
api.add_resource(CustomDataManager, '/custom/<string:customData_id>')



if __name__ == '__main__':
    app.run(debug=True)


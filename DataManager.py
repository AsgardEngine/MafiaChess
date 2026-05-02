import bge
import json
class DataManager:

    @staticmethod
    def getSaveData():
        path = bge.logic.expandPath("//Script\\")
        saveFile = f"{path}data.json"
        newData = None
        with open(saveFile, "r") as file:
            newData = json.load(file)
        return newData
    
    @staticmethod
    def setSaveData(data):
        jsonData = json.dumps(data, indent=4)
        path = bge.logic.expandPath("//Script\\")
        saveFile = f"{path}data.json"
        with open(saveFile, "w") as file:
            file.write(jsonData)
    
    @staticmethod
    def writeData(key, value):
        data = DataManager.getSaveData()
        try:
            data[key] = value
        except (KeyError, AttributeError):
            print("Key does not exist")

        DataManager.setSaveData(data)
    
    @staticmethod
    def getValue(key):
        val = None
        data = DataManager.getSaveData()
        try:
            val = data[key]
        except (KeyError, AttributeError):
            print("Key does not exist")
        
        return val